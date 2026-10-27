"""Motor de cálculo del simulador de consumo.

Funciones puras: consumo activo/pasivo de cada electrodoméstico, consumo mensual de la casa y
factura de EDEA por tramos. Es una estimación determinista basada en los supuestos del usuario,
NO una predicción de aprendizaje automático. Lo usan todas las pestañas y las pruebas de tests/.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DIAS_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MODOS = {"horas", "ciclos", "anual", "siempre"}
RUTA_DATOS = Path(__file__).parent / "datos" / "datos.json"


@lru_cache(maxsize=1)
def datos() -> dict:
    """Catálogo, perfiles, estaciones y tarifas de ejemplo."""
    with open(RUTA_DATOS, encoding="utf-8") as f:
        return json.load(f)


def _num(v, defecto=0.0) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return defecto
    return x if x == x and abs(x) != float("inf") else defecto


def _clamp(v: float, a: float, b: float) -> float:
    return min(b, max(a, v))


def factores(inst: dict) -> list[float]:
    """Factor de uso de cada mes (0 = no se usa, 1 = uso normal)."""
    if inst.get("estacion") == "custom" and isinstance(inst.get("factores"), list) and len(inst["factores"]) == 12:
        return [_clamp(_num(f), 0, 2) for f in inst["factores"]]
    est = datos()["ESTACIONES"]
    return est.get(inst.get("estacion"), est["todo"])


def validar(inst: dict) -> list[str]:
    """Lista de errores de una instancia (vacía si es válida)."""
    e = []
    modo = inst.get("modo")
    if modo not in MODOS:
        e.append("Modo de uso desconocido.")
    q = _num(inst.get("cantidad"), -1)
    if q != int(q) or not 1 <= q <= 20:
        e.append("La cantidad debe ser un entero entre 1 y 20.")
    conn, uso = _num(inst.get("conectado")), _num(inst.get("uso"))
    if modo in ("horas", "ciclos") and not 0 <= conn <= 24:
        e.append("Las horas conectado van de 0 a 24.")
    if modo == "horas":
        if uso < 0:
            e.append("Las horas de uso no pueden ser negativas.")
        if uso > conn:
            e.append("Las horas en uso no pueden superar las horas conectado.")
        if not 1 <= _num(inst.get("dias"), 7) <= 7:
            e.append("Los días por semana van de 1 a 7.")
    if modo == "ciclos" and not 0 <= _num(inst.get("ciclos")) <= 21:
        e.append("Los ciclos por semana van de 0 a 21.")
    if modo == "anual" and not 0 <= _num(inst.get("kwh_anio")) <= 3000:
        e.append("El kWh/año va de 0 a 3.000.")
    if not 0 <= _num(inst.get("potencia_w")) <= 10000:
        e.append("La potencia va de 0 a 10.000 W.")
    if not 0 <= _num(inst.get("standby_w")) <= 100:
        e.append("El standby va de 0 a 100 W.")
    return e


def diaria(inst: dict, k: float = 1.0) -> dict:
    """Energía de un día promedio en kWh, separada en activo y pasivo (sin estacionalidad).

    k escala las horas o ciclos de uso (0,75 y 1,25 para el rango mínimo/máximo).
    """
    q = _num(inst.get("cantidad"), 1)
    modo = inst.get("modo")
    if modo == "horas":
        uso = _clamp(_num(inst.get("uso")) * k, 0, 24)
        conn = _clamp(max(_num(inst.get("conectado")), uso), 0, 24)
        f = _clamp(_num(inst.get("dias"), 7), 0, 7) / 7
        return {
            "act": _num(inst.get("potencia_w")) / 1000 * uso * q * f,
            "pas": _num(inst.get("standby_w")) / 1000 * (conn - uso) * q * f,
        }
    if modo == "ciclos":
        c = _num(inst.get("ciclos")) * k
        horas_ciclo_dia = c * _num(inst.get("ciclo_h"), 1) / 7
        return {
            "act": _num(inst.get("kwh_ciclo")) * c / 7 * q,
            "pas": _num(inst.get("standby_w")) / 1000 * max(0.0, _num(inst.get("conectado")) - horas_ciclo_dia) * q,
        }
    if modo == "anual":
        return {"act": _num(inst.get("kwh_anio")) / 365 * q, "pas": 0.0}
    if modo == "siempre":
        return {"act": _num(inst.get("potencia_w")) / 1000 * 24 * q, "pas": 0.0}
    return {"act": 0.0, "pas": 0.0}


def mensual(inst: dict, k: float = 1.0) -> list[dict]:
    """Consumo de cada mes en kWh: [{act, pas, total}] x 12.

    La estacionalidad afecta al consumo activo; el standby sigue mientras esté enchufado.
    En modo anual, el total de la etiqueta se reparte para que la suma dé exactamente el kWh/año.
    """
    f = factores(inst)
    if inst.get("modo") == "anual":
        suma = sum(fi * d for fi, d in zip(f, DIAS_MES))
        total = _num(inst.get("kwh_anio")) * _num(inst.get("cantidad"), 1)
        out = []
        for fi, d in zip(f, DIAS_MES):
            act = total * fi * d / suma if suma > 0 else 0.0
            out.append({"act": act, "pas": 0.0, "total": act})
        return out
    dd = diaria(inst, k)
    usa_factor = inst.get("modo") != "siempre"
    out = []
    for fi, d in zip(f, DIAS_MES):
        act = dd["act"] * (fi if usa_factor else 1) * d
        pas = dd["pas"] * d
        out.append({"act": act, "pas": pas, "total": act + pas})
    return out


def base_mensual(w: float) -> list[float]:
    """Consumo de base de la casa (equipos siempre enchufados no cargados)."""
    return [_clamp(_num(w), 0, 500) / 1000 * 24 * d for d in DIAS_MES]


# ---------- Curva horaria ----------

def solape(inicio: float, largo: float, h: int) -> float:
    """Fracción de la hora [h, h+1) cubierta por el intervalo circular [inicio, inicio+largo)."""
    if largo <= 0:
        return 0.0
    if largo >= 24:
        return 1.0
    s = inicio % 24
    t = sum(max(0.0, min(s + off + largo, h + 1) - max(s + off, h)) for off in (-24, 0, 24))
    return min(1.0, t)


def ventanas(inst: dict) -> dict:
    """Ventanas del día: 'uso' y 'conn' como (inicio, largo) en horas."""
    ini = _num(inst.get("inicio"))
    if inst.get("modo") == "horas":
        uso = _clamp(_num(inst.get("uso")), 0, 24)
        conn = _clamp(max(_num(inst.get("conectado")), uso), 0, 24)
        return {"uso": (ini, uso), "conn": (ini - (conn - uso) / 2, conn)}
    if inst.get("modo") == "ciclos":
        largo = _num(inst.get("ciclo_h"), 1) if _num(inst.get("ciclos")) > 0 else 0.0
        return {"uso": (ini, largo), "conn": (0.0, _clamp(_num(inst.get("conectado")), 0, 24))}
    return {"uso": (0.0, 24.0), "conn": (0.0, 24.0)}


def horaria(inst: dict, m: int) -> list[float]:
    """Energía de cada hora (kWh = kW medios) en un día típico del mes m. Suma = consumo diario."""
    f = factores(inst)[m]
    q = _num(inst.get("cantidad"), 1)
    modo = inst.get("modo")
    if modo == "anual":
        kwh_dia = mensual(inst)[m]["total"] / DIAS_MES[m]
        return [kwh_dia / 24] * 24
    if modo == "siempre":
        return [_num(inst.get("potencia_w")) / 1000 * q] * 24
    v = ventanas(inst)
    out = []
    if modo == "horas":
        fd = _clamp(_num(inst.get("dias"), 7), 0, 7) / 7
        p, sb = _num(inst.get("potencia_w")) / 1000, _num(inst.get("standby_w")) / 1000
        for h in range(24):
            ou, oc = solape(*v["uso"], h), solape(*v["conn"], h)
            out.append(q * fd * (p * ou * f + sb * max(0.0, oc - ou)))
        return out
    dd = diaria(inst)
    dur = max(0.1, _num(inst.get("ciclo_h"), 1))
    return [dd["act"] * f * solape(v["uso"][0], dur, h) / dur + dd["pas"] / 24 for h in range(24)]


def curva_dia(items: list[dict], base_w: float, m: int, ajuste: float = 1.0) -> dict:
    """Curva de carga del día típico del mes m, por artefacto y total (kW medios por hora)."""
    series = []
    for inst in items:
        vals = [0.0] * 24 if validar(inst) else [v * ajuste for v in horaria(inst, m)]
        series.append({"uid": inst.get("uid"), "valores": vals})
    base = [_clamp(_num(base_w), 0, 500) / 1000 * ajuste] * 24
    total = [base[h] + sum(s["valores"][h] for s in series) for h in range(24)]
    return {"series": series, "base": base, "total": total}


# ---------- Tarifas ----------

def bloques(tarifas: dict, esc_id: str) -> list[dict]:
    e = tarifas["escenarios"].get(esc_id)
    pleno = _num(tarifas["precio_pleno"])
    if not e or e.get("precio") is None or e.get("tope") is None:
        return [{"hasta_kwh": None, "precio_kwh": pleno}]
    return [
        {"hasta_kwh": _num(e["tope"]), "precio_kwh": _num(e["precio"])},
        {"hasta_kwh": None, "precio_kwh": pleno},
    ]


# ---------- Tarifas reales de EDEA (datos/tarifas_edea.csv) ----------

RUTA_TARIFAS = Path(__file__).parents[1] / "datos" / "tarifas_edea.csv"
ESCENARIOS_EDEA = {
    "sin_subsidio": {"nombre": "Sin subsidio", "corto": "Sin subsidio", "icono": "💸",
                     "desc": "Todos los kWh a precio pleno."},
    "sef": {"nombre": "Con subsidio nacional (SEF)", "corto": "Subsidio SEF", "icono": "🤝",
            "desc": "Los primeros 150 kWh del mes a precio subsidiado; el resto, a precio pleno."},
    "tarifa_social": {"nombre": "Tarifa social provincial", "corto": "Tarifa social", "icono": "🏛️",
                      "desc": "Cargos más bajos y un descuento fijo por mes según el consumo."},
    "tarifa_social_sef": {"nombre": "Tarifa social + subsidio SEF", "corto": "Social + SEF", "icono": "🏛️",
                          "desc": "Tarifa social provincial y, además, beneficiario del subsidio nacional."},
}


@lru_cache(maxsize=1)
def tarifas_edea() -> dict:
    """Cuadro tarifario residencial vigente de EDEA, leído de datos/tarifas_edea.csv."""
    import csv

    escenarios: dict = {}
    with open(RUTA_TARIFAS, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    for r in filas:
        e = escenarios.setdefault(r["escenario"], {
            **ESCENARIOS_EDEA.get(r["escenario"], {"nombre": r["escenario"], "corto": r["escenario"], "icono": "", "desc": ""}),
            "tramos": [], "impuestos_pct": float(r["impuestos_pct"]), "anexo": r["anexo"], "fuente_url": r["fuente_url"],
        })
        e["tramos"].append({
            "tramo": r["tramo"], "desde": float(r["desde_kwh"]),
            "hasta": float(r["hasta_kwh"]) if r["hasta_kwh"] else None,
            "cargo_fijo": float(r["cargo_fijo"]), "cargo_variable": float(r["cargo_variable"]),
            "bloque_kwh": float(r["bloque_kwh"]), "cargo_variable_bloque": float(r["cargo_variable_bloque"]),
            "bonificacion_fija": float(r["bonificacion_fija"]), "ctt": float(r["ctt"]), "ctt_bloque": float(r["ctt_bloque"]),
        })
    return {
        "distribuidora": "EDEA", "resolucion": filas[0]["resolucion"], "vigencia_desde": filas[0]["vigencia_desde"],
        "fuente": "Cuadros tarifarios oficiales publicados por el OCEBA",
        "url_indice": "https://oceba.gba.gov.ar/nueva_web/s.php?i=17",
        "escenarios": escenarios,
    }


def tramo_de(kwh: float, tramos: list[dict]) -> dict:
    """Tramo que corresponde al consumo total del mes (desde < kWh ≤ hasta)."""
    for t in tramos:
        if t["hasta"] is None or kwh <= t["hasta"]:
            return t
    return tramos[-1]


def _factura_edea(kwh: float, esc: dict) -> dict:
    t = tramo_de(kwh, esc["tramos"])
    bloque = min(kwh, t["bloque_kwh"]) if t["bloque_kwh"] > 0 else 0.0
    resto = kwh - bloque
    energia = bloque * t["cargo_variable_bloque"] + resto * t["cargo_variable"]
    ctt = bloque * t["ctt_bloque"] + resto * t["ctt"]
    subtotal = t["cargo_fijo"] + energia + ctt - t["bonificacion_fija"]
    impuestos = subtotal * esc["impuestos_pct"] / 100
    total = subtotal + impuestos
    return {
        "kwh": kwh, "tramo": t["tramo"], "tramo_desde": t["desde"], "tramo_hasta": t["hasta"],
        "cargo_fijo": t["cargo_fijo"], "energia": energia, "ctt": ctt, "bonificacion": t["bonificacion_fija"],
        "subtotal": subtotal, "impuestos": impuestos, "total": total, "efectivo": total / kwh if kwh > 0 else 0.0,
        "tope": t["bloque_kwh"] or None, "dentro": bloque, "fuera": resto if t["bloque_kwh"] > 0 else 0.0,
    }


# Casa de referencia para el precio fijo de Mi casa: 300 kWh por mes, en el medio del tramo R3
# (200 a 400 kWh), el de una casa típica.
KWH_REFERENCIA = 300.0


def precio_kwh(tarifas: dict, esc_id: str, kwh_ref: float = KWH_REFERENCIA) -> dict:
    """Precio fijo por kWh de Mi casa: no depende del consumo de la casa, solo del subsidio.

    Es lo que cuesta, en promedio, cada kWh de energía (precio de la energía + Cargo Transición
    Tarifaria + impuestos) en una casa de referencia de 300 kWh (tramo R3). Con subsidio SEF incluye
    el bloque de 150 kWh a precio subsidiado. No incluye el cargo fijo ni la bonificación fija, que
    van aparte (ver costo_casa).

    Al ser fijo, la plata de cada electrodoméstico depende solo de sus kWh: cambiar uno no cambia
    a los demás, y el total de la casa es la suma exacta de los electrodomésticos más el cargo fijo.
    """
    e = tarifas["escenarios"].get(esc_id)
    if not (e and "tramos" in e):
        f = factura(kwh_ref, tarifas, esc_id)
        return {"precio": f["efectivo"], "cargo_fijo": 0.0, "tramo": None, "kwh_ref": kwh_ref}
    f = _factura_edea(kwh_ref, e)
    imp = 1 + e["impuestos_pct"] / 100
    return {
        "precio": (f["energia"] + f["ctt"]) / kwh_ref * imp,
        "cargo_fijo": (f["cargo_fijo"] - f["bonificacion"]) * imp,  # con impuestos, neto del descuento fijo
        "energia": f["energia"] / kwh_ref, "ctt": f["ctt"] / kwh_ref, "impuestos_pct": e["impuestos_pct"],
        "tramo": f["tramo"], "kwh_ref": kwh_ref, "bloque_kwh": f["tope"] or 0.0,
    }


def costo_casa(kwh_casa: float, tarifas: dict, esc_id: str) -> dict:
    """Lo que gasta la casa por mes en Mi casa: cargo fijo + kWh × precio fijo.

    Es la suma exacta de lo que dice cada electrodoméstico (más el consumo de base y el cargo
    fijo): si un electrodoméstico sube $ 1.000, el total sube $ 1.000. La factura real de EDEA,
    con tramos, se calcula aparte con factura().
    """
    p = precio_kwh(tarifas, esc_id)
    energia = max(0.0, kwh_casa) * p["precio"]
    return {"total": p["cargo_fijo"] + energia, "cargo_fijo": p["cargo_fijo"], "energia": energia,
            "precio": p["precio"], "kwh": kwh_casa}


def factura(kwh: float, tarifas: dict, esc_id: str) -> dict:
    """Factura estimada de un mes.

    Con el cuadro real de EDEA (escenarios con "tramos") usa la facturación por tramos; con el
    esquema simplificado de la propuesta (precio pleno + tope) usa bloques.
    """
    e = tarifas["escenarios"].get(esc_id)
    if e and "tramos" in e:
        return _factura_edea(max(0.0, kwh), e)
    bl = bloques(tarifas, esc_id)
    piso, energia = 0.0, 0.0
    for b in bl:
        hasta = float("inf") if b["hasta_kwh"] is None else b["hasta_kwh"]
        cant = max(0.0, min(kwh, hasta) - piso)
        energia += cant * b["precio_kwh"]
        piso = hasta
    cargo = _num(tarifas.get("cargo_fijo"))
    subtotal = energia + cargo
    impuestos = subtotal * _num(tarifas.get("iva"))
    total = subtotal + impuestos
    tope = bl[0]["hasta_kwh"] if len(bl) > 1 else None
    return {
        "kwh": kwh, "energia": energia, "cargo_fijo": cargo, "subtotal": subtotal,
        "impuestos": impuestos, "total": total, "efectivo": total / kwh if kwh > 0 else 0.0,
        "tope": tope,
        "dentro": 0.0 if tope is None else min(kwh, tope),
        "fuera": 0.0 if tope is None else max(0.0, kwh - tope),
    }


# ---------- Simulación completa ----------

def simular(estado: dict) -> dict:
    """estado = {items: [...], base_w, tarifas, ajuste}. Devuelve meses, año y costos."""
    ajuste = _num(estado.get("ajuste"), 1) or 1
    tarifas = estado.get("tarifas") or tarifas_edea()
    items = []
    for inst in estado.get("items", []):
        errores = validar(inst)
        ok = not errores
        cero = [{"act": 0.0, "pas": 0.0, "total": 0.0}] * 12
        meses = mensual(inst) if ok else cero
        items.append({
            "uid": inst.get("uid"), "id": inst.get("id"), "errores": errores, "meses": meses,
            "min": mensual(inst, 0.75) if ok else cero, "max": mensual(inst, 1.25) if ok else cero,
            "anual": sum(m["total"] for m in meses),
        })
    base = base_mensual(estado.get("base_w", 0))
    meses = []
    for m, d in enumerate(DIAS_MES):
        act = sum(it["meses"][m]["act"] for it in items)
        pas = sum(it["meses"][m]["pas"] for it in items)
        lo = sum(it["min"][m]["total"] for it in items)
        hi = sum(it["max"][m]["total"] for it in items)
        meses.append({
            "act": act * ajuste, "pas": pas * ajuste, "base": base[m] * ajuste,
            "total": (act + pas + base[m]) * ajuste,
            "min": (lo + base[m]) * ajuste, "max": (hi + base[m]) * ajuste, "dias": d,
        })
    costos = {}
    for esc_id in tarifas["escenarios"]:
        por_mes = [factura(x["total"], tarifas, esc_id) for x in meses]
        costos[esc_id] = {"porMes": por_mes, "anual": sum(f["total"] for f in por_mes)}
    return {
        "items": items, "base": base, "meses": meses,
        "anual": sum(x["total"] for x in meses), "costos": costos, "ajuste": ajuste,
    }


def instancia(id_catalogo: str, **cambios) -> dict:
    """Crea una instancia con los valores por defecto del catálogo (útil para tests)."""
    c = next(x for x in datos()["CATALOGO"] if x["id"] == id_catalogo)
    inst = {
        "id": c["id"], "modo": c["modo"], "potencia_w": c.get("potencia_w", 0), "standby_w": c.get("standby_w", 0),
        "kwh_anio": c.get("kwh_anio", 0), "kwh_ciclo": c.get("kwh_ciclo", 0), "ciclo_h": c.get("ciclo_h", 1),
        "estacion": c["estacion"], "cantidad": 1, "conectado": 24, "uso": 1, "dias": 7, "ciclos": 0, "inicio": 0,
    }
    inst.update(c.get("def", {}))
    inst.update(cambios)
    return inst
