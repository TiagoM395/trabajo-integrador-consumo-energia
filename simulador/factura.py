"""Lectura de la factura de luz (EDEA u otra distribuidora) para calibrar la simulación.

- PDF con texto: se lee directo con pypdf (preciso).
- Foto o PDF escaneado: OCR con Tesseract (pytesseract). Si Tesseract no está instalado,
  la app lo avisa y se cargan los datos a mano.

Privacidad: la imagen se procesa en memoria y no se guarda. Solo se devuelven los campos
numéricos (kWh, fechas, importe); el texto completo (que tiene nombre, dirección y NIS) se descarta.
"""
from __future__ import annotations

import base64
import datetime as dt
import io
import json
import re
import shutil
from pathlib import Path

MAX_BYTES = 10 * 1024 * 1024
FECHA = r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})"


# ---------- Lectura ----------

# Ruta del instalador de Windows (UB-Mannheim), por si Tesseract no quedó en el PATH.
TESSERACT_WIN = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def ocr_disponible() -> bool:
    try:
        import pytesseract
    except ImportError:
        return False
    if shutil.which("tesseract"):
        return True
    if Path(TESSERACT_WIN).exists():
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_WIN
        return True
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def texto_pdf(datos: bytes) -> str:
    from pypdf import PdfReader

    lector = PdfReader(io.BytesIO(datos))
    return "\n".join((p.extract_text() or "") for p in lector.pages[:3])


def _abrir(datos: bytes):
    """Abre la imagen derecha (según el EXIF de la cámara)."""
    from PIL import Image, ImageOps

    return ImageOps.exif_transpose(Image.open(io.BytesIO(datos)))


def _preparar(img):
    """Escala de grises, contraste y un ancho de 1600 a 2400 px: mejora el OCR y lo hace más rápido
    con las fotos grandes del celular."""
    from PIL import ImageOps

    img = img.convert("L")
    if img.width < 1600 or img.width > 2400:
        k = (1600 if img.width < 1600 else 2400) / img.width
        img = img.resize((int(img.width * k), int(img.height * k)))
    return ImageOps.autocontrast(img, cutoff=2)


def texto_imagen(datos: bytes) -> str:
    import pytesseract

    img = _preparar(_abrir(datos))

    def ocr(psm: int) -> str:
        try:
            return pytesseract.image_to_string(img, lang="spa", config=f"--psm {psm}")
        except pytesseract.TesseractError:
            return pytesseract.image_to_string(img, config=f"--psm {psm}")  # sin el idioma español

    texto = ocr(6)  # bloque de texto uniforme
    if "kwh" not in texto.lower():
        texto += "\n" + ocr(11)  # texto disperso: tablas y recuadros de la factura
    return texto


# ---------- Códigos de barras y QR ----------

def codigos(datos: bytes, nombre: str = "") -> list[dict]:
    """Lee todos los códigos de barras y QR de una foto (o de las imágenes de un PDF)."""
    try:
        import zxingcpp
    except ImportError:
        return []
    imagenes = []
    try:
        if (nombre or "").lower().endswith(".pdf") or datos[:4] == b"%PDF":
            from pypdf import PdfReader

            for pag in PdfReader(io.BytesIO(datos)).pages[:2]:
                imagenes += [im.image for im in pag.images]
        else:
            imagenes.append(_abrir(datos))
    except Exception:
        return []
    vistos, out = set(), []
    for img in imagenes:
        try:
            leidos = zxingcpp.read_barcodes(img.convert("RGB"))
        except Exception:
            continue
        for c in leidos:
            if c.text and c.text not in vistos:
                vistos.add(c.text)
                out.append({"formato": str(c.format).split(".")[-1], "texto": c.text})
    return out


def qr_arca(texto: str) -> dict | None:
    """Datos del QR de factura electrónica (ARCA/AFIP): una URL con un JSON en base64."""
    mt = re.search(r"[?&]p=([A-Za-z0-9+/=_-]+)", texto)
    if not mt or "afip" not in texto.lower() and "arca" not in texto.lower():
        return None
    try:
        crudo = mt.group(1)
        datos = json.loads(base64.urlsafe_b64decode(crudo + "=" * (-len(crudo) % 4)).decode("utf8"))
    except Exception:
        return None
    fecha = None
    try:
        fecha = dt.date.fromisoformat(str(datos.get("fecha", ""))[:10])
    except ValueError:
        pass
    importe = datos.get("importe")
    return {"importe": float(importe) if importe else None, "fecha": fecha}


def leer(datos: bytes, nombre: str) -> tuple[str, str]:
    """Devuelve (texto, método). Lanza ValueError con un mensaje claro si no se puede leer."""
    if len(datos) > MAX_BYTES:
        raise ValueError("El archivo supera los 10 MB.")
    nombre = (nombre or "").lower()
    if nombre.endswith(".pdf") or datos[:4] == b"%PDF":
        texto = texto_pdf(datos)
        if len(texto.strip()) > 40:
            return texto, "PDF (texto)"
        raise ValueError("El PDF no tiene texto (está escaneado). Subí una foto de la factura para leerla con OCR.")
    if not ocr_disponible():
        raise ValueError("El OCR (Tesseract) no está instalado en este equipo. Subí el PDF de la factura "
                         "o cargá los datos a mano. Ver EJECUTAR.md para instalarlo.")
    return texto_imagen(datos), "OCR (foto)"


# ---------- Extracción de campos ----------

def numero_ar(s: str) -> float | None:
    """Convierte un número en formato argentino: '1.234,56' -> 1234.56; '320' -> 320."""
    s = s.strip().replace(" ", "")
    if not s:
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def _fecha(d, m, a) -> dt.date | None:
    a = int(a)
    a = a + 2000 if a < 100 else a
    try:
        return dt.date(a, int(m), int(d))
    except ValueError:
        return None


def _kwh(t: str) -> tuple[float | None, str]:
    # 1) "Consumo ... 320 kWh"
    for pat in (r"consumo[^\n\d$]{0,40}?(\d[\d.]*(?:,\d+)?)\s*kwh",
                r"energ[ií]a\s+(?:activa\s+)?consumida[^\n\d$]{0,30}?(\d[\d.]*(?:,\d+)?)",
                r"total\s+(?:de\s+)?consumo[^\n\d$]{0,30}?(\d[\d.]*(?:,\d+)?)"):
        mt = re.search(pat, t)
        if mt:
            v = numero_ar(mt.group(1))
            if v and 0 < v <= 2000:
                return v, "alta"
    # 2) diferencia de lecturas del medidor
    act = re.search(r"lectura\s+actual\D{0,25}(\d[\d.]*)", t)
    ant = re.search(r"lectura\s+anterior\D{0,25}(\d[\d.]*)", t)
    if act and ant:
        a, b = numero_ar(act.group(1)), numero_ar(ant.group(1))
        if a and b and 0 < a - b <= 2000:
            return a - b, "media"
    # 3) cualquier "NNN kWh" que no sea un precio ($/kWh)
    candidatos = []
    for mt in re.finditer(r"(?<![\d$/])(\d[\d.]*(?:,\d+)?)\s*kwh(?!\s*/)", t):
        previo = t[max(0, mt.start() - 3):mt.start()]
        if "$" in previo or "/" in t[mt.end():mt.end() + 1]:
            continue
        v = numero_ar(mt.group(1))
        if v and 10 <= v <= 2000:
            candidatos.append(v)
    if candidatos:
        return max(candidatos), "baja"
    return None, "no encontrado"


def _periodo(t: str):
    mt = re.search(r"(?:per[ií]odo|desde|del)\D{0,25}" + FECHA + r"\D{1,15}?" + FECHA, t)
    if mt:
        d1, d2 = _fecha(*mt.groups()[:3]), _fecha(*mt.groups()[3:])
        if d1 and d2 and d2 > d1:
            return d1, d2, "alta"
    fechas = [f for f in (_fecha(*g) for g in re.findall(FECHA, t)) if f]
    for a, b in zip(fechas, fechas[1:]):
        if 25 <= (b - a).days <= 65:
            return a, b, "baja"
    return None, None, "no encontrado"


def _importe(t: str) -> tuple[float | None, str]:
    for pat in (r"total\s+a\s+pagar\D{0,20}?\$?\s*(\d[\d.]*,\d{2})",
                r"importe\s+total\D{0,20}?\$?\s*(\d[\d.]*,\d{2})",
                r"total\s+(?:factura|general)\D{0,20}?\$?\s*(\d[\d.]*,\d{2})"):
        mt = re.search(pat, t)
        if mt:
            v = numero_ar(mt.group(1))
            if v and v > 0:
                return v, "alta"
    montos = [numero_ar(x) for x in re.findall(r"\$\s*(\d[\d.]*,\d{2})", t)]
    montos = [v for v in montos if v]
    return (max(montos), "baja") if montos else (None, "no encontrado")


def _subsidio(t: str) -> tuple[str | None, str]:
    """Situación de la factura: sin subsidio, subsidio nacional (SEF), tarifa social o las dos."""
    social = re.search(r"tarifa\s+social|\bt\.?\s*social\b", t) is not None
    sef = re.search(r"\bsef\b|subsidio\s+(?:energ|nacional|del\s+estado\s+nacional)"
                    r"|segmentaci[oó]n\D{0,15}[23]\b|\bnivel\s*[23]\b|\bn[23]\b", t) is not None
    if social and sef:
        return "tarifa_social_sef", "media"
    if social:
        return "tarifa_social", "media"
    if sef:
        return "sef", "media"
    if re.search(r"sin\s+subsidio|\bnivel\s*1\b|\bn1\b", t):
        return "sin_subsidio", "media"
    return None, "no encontrado"


def extraer(texto: str, codigos_leidos: list[dict] | None = None) -> dict:
    """Busca consumo (kWh), período, importe total, vencimiento y subsidio. Cada campo trae su
    confianza. Si la foto tenía el QR de factura electrónica, de ahí sale el importe."""
    t = texto.lower().replace(chr(13), "")
    kwh, c_kwh = _kwh(t)
    desde, hasta, c_per = _periodo(t)
    importe, c_imp = _importe(t)
    esc, c_esc = _subsidio(t)
    mv = re.search(r"venc\w*\D{0,25}" + FECHA, t)
    venc = _fecha(*mv.groups()) if mv else None
    dias = (hasta - desde).days if desde and hasta else None
    avisos = []
    for c in codigos_leidos or []:
        qr = qr_arca(c["texto"])
        if qr and qr["importe"]:
            if importe and abs(importe - qr["importe"]) > 1:
                avisos.append("El importe del texto y el del QR no coinciden: se usa el del QR.")
            importe, c_imp = qr["importe"], "alta"
    if dias is not None and not 25 <= dias <= 65:
        avisos.append(f"El período detectado tiene {dias} días (se esperaban 25 a 65).")
        dias, c_per = None, "dudosa"
    if dias and dias > 45:
        avisos.append("Parece una factura bimestral: el tope bonificado se prorratea por los días del período.")
    return {
        "kwh": kwh, "kwh_conf": c_kwh,
        "desde": desde, "hasta": hasta, "dias": dias, "periodo_conf": c_per,
        "importe": importe, "importe_conf": c_imp,
        "vencimiento": venc, "escenario": esc, "escenario_conf": c_esc,
        # De los códigos solo queda el formato: su texto puede traer DNI/CUIT del titular.
        "codigos": [c["formato"] for c in codigos_leidos or []], "avisos": avisos,
    }


def mes_del_periodo(desde: dt.date | None, hasta: dt.date | None) -> int | None:
    """Mes (0-11) del punto medio del período."""
    if not (desde and hasta):
        return None
    return (desde + (hasta - desde) / 2).month - 1
