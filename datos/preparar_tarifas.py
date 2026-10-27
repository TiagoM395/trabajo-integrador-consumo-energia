"""Arma el dataset de tarifas residenciales de EDEA a partir de los cuadros oficiales del OCEBA.

Fuente: Resolución MIySP N° 682/2026 de la Provincia de Buenos Aires (Boletín Oficial del
31/08/2026), cuadros tarifarios para consumos a partir del 1° de septiembre de 2026, publicados
por el OCEBA (Organismo de Control de Energía Eléctrica de la Provincia de Buenos Aires).

Uso:
    python datos/preparar_tarifas.py                 # descarga los PDF y genera los CSV
    python datos/preparar_tarifas.py --sin-descarga  # usa los PDF que ya están en datos/crudos/oceba/

Salidas:
    datos/tarifas_edea.csv   una fila por situación (escenario) y tramo de consumo
    datos/impuestos_residenciales.csv

Cómo se factura (y cómo lo usa el simulador):
    1. El tramo (R1…R7) se elige por el consumo TOTAL del mes.
    2. Cargo fijo del tramo + consumo × cargo variable del tramo.
    3. Si hay "bloque" (subsidio SEF o tarifa social), los primeros `bloque_kwh` kWh se cobran a
       `cargo_variable_bloque` y el resto a `cargo_variable`.
    4. + Cargo Transición Tarifaria (CTT) por kWh (`ctt_bloque` para el bloque, `ctt` para el resto).
    5. − Bonificación fija de la tarifa social (si corresponde).
    6. + Impuestos (`impuestos_pct` sobre el subtotal).
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import urllib.request
from pathlib import Path

AQUI = Path(__file__).parent
CRUDOS = AQUI / "crudos" / "oceba"
SALIDA = AQUI / "tarifas_edea.csv"
SALIDA_IMP = AQUI / "impuestos_residenciales.csv"

BASE = "https://oceba.gba.gov.ar/nueva_web/adjuntos/ct202609/"
RESOLUCION = "Resolución MIySP N° 682/2026 (Prov. de Buenos Aires)"
URL_RESOLUCION = BASE + "Reso_682_26.pdf"
URL_INDICE = "https://oceba.gba.gov.ar/nueva_web/s.php?i=17"
VIGENCIA = "2026-09-01"
ANEXOS = {
    "44": "IF-2026-27778457-GDEBA-GMOCEBA.pdf",  # residencial general (sin subsidio)
    "52": "IF-2026-27784547-GDEBA-GMOCEBA.pdf",  # residencial hasta 150 kWh/mes beneficiaria SEF
    "60": "IF-2026-27787960-GDEBA-GMOCEBA.pdf",  # tarifa social provincial - grupo 1
    "68": "IF-2026-27790623-GDEBA-GMOCEBA.pdf",  # tarifa social + SEF - grupo 1
    "87": "IF-2026-27797883-GDEBA-GMOCEBA.pdf",  # Cargo Transición Tarifaria (CTT)
}
BLOQUE_SEF = 150  # kWh/mes subsidiados (Anexo 52 y nota (2) del Anexo 87)

# Impuestos y contribuciones para la categoría T1R (tabla "Impuestos y FPCT" del OCEBA,
# https://oceba.gba.gov.ar/nueva_web/s.php?i=19 , revisada el 31/01/2026).
IMPUESTOS = [
    ("Decreto-Ley 9038 (Fondo Especial Grandes Obras Eléctricas)", 0.0, 0.0),
    ("Decreto-Ley 7290 (Fondo de Desarrollo Eléctrico Provincial)", 4.0, 0.01),  # tarifa social: 0,01 % (Res. 771/24 art. 52)
    ("Ley 11769 art. 75 (tasa municipal)", 6.0, 6.0),
    ("Ley 11769 art. 74", 0.001, 0.001),
    ("IVA", 21.0, 21.0),
    ("Ley 11769 art. 45 (Fondo Provincial de Compensaciones Tarifarias)", 5.5, 5.5),
]
URL_IMPUESTOS = "https://oceba.gba.gov.ar/nueva_web/s.php?i=19"


def descargar() -> None:
    CRUDOS.mkdir(parents=True, exist_ok=True)
    for anexo, archivo in ANEXOS.items():
        print(f"Descargando anexo {anexo}…")
        req = urllib.request.Request(BASE + archivo, headers={"User-Agent": "Mozilla/5.0"})
        (CRUDOS / archivo).write_bytes(urllib.request.urlopen(req, timeout=60).read())


def texto(anexo: str) -> str:
    from pypdf import PdfReader

    return "\n".join(p.extract_text() or "" for p in PdfReader(CRUDOS / ANEXOS[anexo]).pages)


def num(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))


def rango(desc: str) -> tuple[float, float | None]:
    """Convierte '( 100 < consumo en kWH-Mes ≤ 150)' en (100, 150); '> 1400' en (1400, None)."""
    d = desc.replace("hasta", "≤")
    desde = re.search(r"(\d+)\s*<", d)
    hasta = re.search(r"≤\s*(\d+)", d)
    mayor = re.search(r">\s*(\d+)", d)
    if mayor and not hasta:
        return float(mayor.group(1)), None
    return (float(desde.group(1)) if desde else 0.0), (float(hasta.group(1)) if hasta else None)


PATRON = re.compile(r"CARGO (FIJO|VARIABLE)\s+(R\d)\s*(.*?)\s+(\d[\d.]*,\d+)\s*\$/(mes|kWh)")


def leer_t1r(anexo: str) -> dict:
    """Lee la sección T1R (residencial) de un anexo: tramos con cargo fijo y variable."""
    t = texto(anexo)
    ini = t.index("T1R")
    fin = min(i for i in (t.find("T1RE", ini), t.find("T3", ini), t.find("BONIFICACI", ini)) if i > 0)
    fijos, variables, primeros = [], [], None
    for linea in t[ini:fin].splitlines():
        m = PATRON.search(" ".join(linea.split()))
        if not m:
            continue
        tipo, etiqueta, desc, valor, _ = m.groups()
        if tipo == "FIJO":
            fijos.append({"tramo": etiqueta, "desc": desc, "valor": num(valor)})
        else:
            d, h = rango(desc)
            variables.append({"tramo": etiqueta, "desde": d, "hasta": h, "valor": num(valor)})
            if "primeros 150" in desc:
                primeros = num(valor)
    # Cada cargo fijo define un tramo. Si no trae rango, toma el de su cargo variable.
    tramos = []
    for f in fijos:
        if "<" in f["desc"] or "≤" in f["desc"] or "hasta" in f["desc"] or ">" in f["desc"]:
            d, h = rango(f["desc"])
        else:
            v = next(v for v in variables if v["tramo"] == f["tramo"])
            d, h = v["desde"], v["hasta"]
        cv = [v["valor"] for v in variables if v["desde"] >= d and (h is None or (v["hasta"] or 1e9) <= h)]
        tramos.append({"tramo": f["tramo"], "desde": d, "hasta": h, "cargo_fijo": f["valor"], "cargo_variable": cv[0]})
    bonif = []
    k = t.find("BONIFICACI")
    if k > 0:
        for m in re.finditer(r"Bonificación\s+(R\d)\s*(\(.*?\))\s*(\d[\d.]*)\s*\$/mes", t[k:]):
            d, h = rango(m.group(2))
            bonif.append({"desde": d, "hasta": h, "valor": num(m.group(3) + ",0")})
    return {"tramos": tramos, "primeros_150": primeros, "bonif": bonif}


def leer_ctt() -> dict:
    t = texto("87")
    fila = re.search(r"\nEDEA\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)", t)
    a, b, _, _, e = (num(x) for x in fila.groups())
    return {"residencial": a, "sef_bloque": b, "tarifa_social": e}


def bonificacion(bonifs: list, desde: float) -> float:
    for b in bonifs:
        if b["desde"] <= desde and (b["hasta"] is None or desde < b["hasta"]):
            return b["valor"]
    return 0.0


def armar() -> list[dict]:
    general = leer_t1r("44")
    sef = leer_t1r("52")
    ts = leer_t1r("60")
    ts_sef = leer_t1r("68")
    ctt = leer_ctt()
    imp_general = round(sum(x[1] for x in IMPUESTOS), 3)
    imp_ts = round(sum(x[2] for x in IMPUESTOS), 3)
    filas = []

    def fila(esc, anexo, tr, cv, bloque=0.0, cv_bloque=0.0, bonif=0.0, c=0.0, c_bloque=0.0, imp=imp_general):
        filas.append({
            "escenario": esc, "tramo": tr["tramo"], "desde_kwh": tr["desde"],
            "hasta_kwh": "" if tr["hasta"] is None else tr["hasta"],
            "cargo_fijo": tr["cargo_fijo"], "cargo_variable": cv,
            "bloque_kwh": bloque, "cargo_variable_bloque": cv_bloque, "bonificacion_fija": bonif,
            "ctt": c, "ctt_bloque": c_bloque, "impuestos_pct": imp,
            "anexo": anexo, "resolucion": RESOLUCION, "vigencia_desde": VIGENCIA,
            "fuente_url": BASE + ANEXOS[anexo.split("+")[0]],
        })

    # Sin subsidio: Anexo 44
    for tr in general["tramos"]:
        fila("sin_subsidio", "44", tr, tr["cargo_variable"], c=ctt["residencial"])
    # Subsidio nacional (SEF): primeros 150 kWh a precio del Anexo 52, el resto a precio pleno (Anexo 44)
    for tr, ts_ in zip(general["tramos"], sef["tramos"]):
        fila("sef", "52+44", tr, tr["cargo_variable"], bloque=BLOQUE_SEF, cv_bloque=ts_["cargo_variable"],
             c=ctt["residencial"], c_bloque=ctt["sef_bloque"])
    # Tarifa social provincial (grupo 1): Anexo 60; desde 150 kWh, los primeros 150 al precio "primeros 150"
    for nombre, datos, anexo in (("tarifa_social", ts, "60"), ("tarifa_social_sef", ts_sef, "68")):
        for tr in datos["tramos"]:
            con_bloque = tr["desde"] >= 150
            fila(nombre, anexo, tr, tr["cargo_variable"],
                 bloque=150.0 if con_bloque else 0.0, cv_bloque=datos["primeros_150"] if con_bloque else 0.0,
                 bonif=bonificacion(datos["bonif"], tr["desde"]), c=ctt["tarifa_social"],
                 c_bloque=ctt["tarifa_social"] if con_bloque else 0.0,  # el CTT de tarifa social va sobre todo el consumo
                 imp=imp_ts)
    return filas


def main() -> int:
    p = argparse.ArgumentParser(description="Dataset de tarifas residenciales de EDEA (OCEBA)")
    p.add_argument("--sin-descarga", action="store_true")
    args = p.parse_args()
    if not args.sin_descarga:
        descargar()
    filas = armar()
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    with open(SALIDA_IMP, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["concepto", "alicuota_pct_residencial", "alicuota_pct_tarifa_social", "fuente_url"])
        for nombre, gral, ts in IMPUESTOS:
            w.writerow([nombre, gral, ts, URL_IMPUESTOS])
    print(f"Listo: {len(filas)} filas → {SALIDA}")
    for esc in dict.fromkeys(f["escenario"] for f in filas):
        print(f"  {esc}: {sum(1 for f in filas if f['escenario'] == esc)} tramos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
