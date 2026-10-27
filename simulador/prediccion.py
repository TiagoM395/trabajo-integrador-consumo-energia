"""Predicción con los modelos del trabajo «¿Me paso o no me paso?».

Carga los Pipelines ya entrenados (modelos/*.pkl) y solo ejecuta predict: no entrena nada.
Arma las 16 variables que pide el modelo a partir de lo que la persona cargó en Mi casa o en
Factura, aplicando los ajustes documentados en explicaciones/README_ANALISIS.md (sección 3).
"""
from __future__ import annotations

import datetime as dt
import math
from pathlib import Path

import joblib
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
MODELOS = RAIZ / "modelos"

# Feriados nacionales de Argentina con fecha fija.
FERIADOS_AR = {(1, 1), (3, 24), (4, 2), (5, 1), (5, 25), (6, 20), (7, 9), (12, 8), (12, 25)}

# Submedidores del dataset (UCI): qué electrodomésticos del catálogo caen en cada uno.
SUBMEDIDOR = {
    "sub1": {"microondas", "horno", "pava", "lavavajillas"},                                       # cocina
    "sub2": {"heladera", "freezer", "lavarropas", "secarropas", "plancha", "led", "halogena"},     # lavadero, heladera y luz
    "sub3": {"termotanque", "aire", "calefactor"},                                                 # agua caliente y clima
}
NOMBRE_SUB = {"sub1": "Cocina", "sub2": "Lavadero, heladera y luces", "sub3": "Termotanque y clima"}

VOLT_DATASET = 240.0  # tensión media medida en el dataset
COSPHI_TIPICO = 0.95  # factor de potencia típico de un hogar (sin medición propia)


def cargar() -> tuple[dict, dict]:
    reg = joblib.load(MODELOS / "reg_24h.pkl")
    clf = joblib.load(MODELOS / "clf_me_paso.pkl")
    return reg, clf


def mes_modelo(mes_ar: int) -> int:
    """Mes de Argentina (1-12) → mes equivalente en el hemisferio norte (estaciones invertidas)."""
    return (mes_ar + 5) % 12 + 1


def submedidores(items: list[dict], kwh_dia_item: dict[str, float]) -> dict[str, float]:
    out = {k: 0.0 for k in SUBMEDIDOR}
    for inst in items:
        for k, ids in SUBMEDIDOR.items():
            if inst["id"] in ids:
                out[k] += kwh_dia_item.get(inst["uid"], 0.0)
    return out


def armar_entrada(*, kwh_dia: float, kwh_hora: float, subs: dict[str, float], fecha: dt.date, hora: int,
                  temp_hoy: float, temp_manana: float, feriado: bool) -> tuple[dict, list[dict]]:
    """Devuelve (fila para el modelo, lista de ajustes aplicados para mostrar en Análisis)."""
    tan = math.tan(math.acos(COSPHI_TIPICO))
    mes_m = mes_modelo(fecha.month)
    fila = {
        "kwh_h": kwh_hora,
        "active_24": kwh_dia,
        "active_prevweek": kwh_dia,
        "reactive_24": kwh_dia * tan,
        "cosphi_24": COSPHI_TIPICO,
        "sub1_24": subs["sub1"],
        "sub2_24": subs["sub2"],
        "sub3_24": subs["sub3"],
        "volt_24": VOLT_DATASET,
        "hour": hora,
        "dayofweek": fecha.weekday(),
        "month": mes_m,
        "is_weekend": int(fecha.weekday() >= 5),
        "is_feriado": int(feriado or (fecha.month, fecha.day) in FERIADOS_AR),
        "temp_actual": temp_hoy,
        "temp_next24": temp_manana,
    }
    ajustes = [
        {"Dato": "Mes", "Lo que hay en la app": fecha.strftime("%m"), "Lo que recibe el modelo": str(mes_m),
         "Motivo": "Estaciones invertidas: se corre 6 meses al hemisferio norte"},
        {"Dato": "Consumo de la semana anterior", "Lo que hay en la app": "—",
         "Lo que recibe el modelo": f"{kwh_dia:.2f} kWh", "Motivo": "No hay historial: se usa el mismo consumo diario"},
        {"Dato": "Energía reactiva y cos φ", "Lo que hay en la app": "—",
         "Lo que recibe el modelo": f"{kwh_dia * tan:.2f} kVArh · cos φ {COSPHI_TIPICO}",
         "Motivo": "Sin medidor que la registre: cos φ típico de un hogar"},
        {"Dato": "Voltaje", "Lo que hay en la app": "220 V (red argentina)",
         "Lo que recibe el modelo": f"{VOLT_DATASET:.0f} V", "Motivo": "Sin medición: se usa la media del dataset"},
        {"Dato": "Submedidores", "Lo que hay en la app": "Electrodomésticos de Mi casa",
         "Lo que recibe el modelo": " · ".join(f"{NOMBRE_SUB[k]} {v:.2f} kWh" for k, v in subs.items()),
         "Motivo": "Se agrupan como en el dataset (cocina / lavadero / termotanque y aire)"},
    ]
    return fila, ajustes


def predecir(reg: dict, clf: dict, fila: dict) -> dict:
    X = pd.DataFrame([fila])[reg["features"]]
    kwh = float(reg["modelo"].predict(X)[0])
    meta, mae = float(reg["meta"]), float(reg["mae"])
    alerta_reg = kwh > meta
    alerta_clf = bool(clf["modelo"].predict(X)[0])
    return {
        "kwh": kwh, "mae": mae, "meta": meta, "diferencia": kwh - meta,
        "alerta_reg": alerta_reg, "alerta_clf": alerta_clf, "coinciden": alerta_reg == alerta_clf,
        "zona_gris": abs(kwh - meta) <= mae,
        "reg_nombre": reg.get("nombre", ""), "clf_nombre": clf.get("nombre", ""),
    }
