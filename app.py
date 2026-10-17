"""Aplicacion Flask - Asistente de consumo electrico del hogar.

Carga los Pipelines ya entrenados (no reentrena en cada solicitud) y ejecuta
predict. Responde las dos preguntas del trabajo:
  - regresion: cuanto consumire en las proximas 24 h (kWh)
  - clasificacion: me paso de mi meta diaria? (si/no)
mas el coseno phi (indicador medido) y el costo estimado.
"""
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request

BASE = Path(__file__).resolve().parent
MOD = BASE / "modelos"

app = Flask(__name__, static_folder="public", static_url_path="/static")

# ---------------------------------------------------------------- modelos
reg = joblib.load(MOD / "reg_24h.pkl")
clf = joblib.load(MOD / "clf_me_paso.pkl")
FEATURES = reg["features"]
META = float(reg["meta"])
MAE = float(reg.get("mae", 0.0))
TARIFA_DEFAULT = 150.0
try:
    enero_tabla = pd.read_csv(MOD / "enero_resumen.csv", index_col="anio")
except Exception:
    enero_tabla = None

FERIADOS_FIJOS = {(1, 1), (5, 1), (5, 8), (7, 14), (8, 15), (11, 1), (11, 11), (12, 25)}


def franja_cosphi(c):
    if c >= 0.95:
        return ("Sin recargo", 0.0)
    if c >= 0.85:
        return ("Recargo (aprox. 10%)", 0.10)
    if c >= 0.75:
        return ("Recargo mayor (aprox. 20%)", 0.20)
    return ("Recargo maximo (aprox. 30%)", 0.30)


def f(x, defecto=0.0):
    try:
        return float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return defecto


CAMPOS_NUM = ["hora", "kwh_ultima_hora", "kwh_24h", "kwh_semana", "kvarh_24h",
              "sub1", "sub2", "sub3", "volt", "temp_actual", "temp_prev", "tarifa"]


def validar(g, fallidos):
    errores = []
    for c in fallidos:
        errores.append(f"El campo '{c}' debe ser un numero.")
    if errores:
        return errores
    for c in CAMPOS_NUM:
        if c in ("temp_actual", "temp_prev"):
            continue
        if g[c] < 0:
            errores.append(f"El campo '{c}' no puede ser negativo.")
    if g["kwh_24h"] <= 0:
        errores.append("La energia de las ultimas 24 h debe ser mayor que 0.")
    if g["kwh_ultima_hora"] > g["kwh_24h"]:
        errores.append("La energia de la ultima hora no puede superar la de las ultimas 24 h.")
    if (g["sub1"] + g["sub2"] + g["sub3"]) > g["kwh_24h"] + 1e-9:
        errores.append("La suma de los submedidores no puede superar la energia total de 24 h.")
    if not (-30 <= g["temp_actual"] <= 50) or not (-30 <= g["temp_prev"] <= 50):
        errores.append("Las temperaturas deben estar entre -30 y 50 grados C.")
    if not (0 <= g["hora"] <= 23):
        errores.append("La hora debe estar entre 0 y 23.")
    return errores


def predecir(g):
    d = g["fecha"]
    fila = {
        "kwh_h": g["kwh_ultima_hora"],
        "active_24": g["kwh_24h"],
        "active_prevweek": g["kwh_semana"],
        "reactive_24": g["kvarh_24h"],
        "cosphi_24": g["cosphi"],
        "sub1_24": g["sub1"],
        "sub2_24": g["sub2"],
        "sub3_24": g["sub3"],
        "volt_24": g["volt"],
        "hour": g["hora"],
        "dayofweek": d.weekday(),
        "month": d.month,
        "is_weekend": int(d.weekday() >= 5),
        "is_feriado": int((d.month, d.day) in FERIADOS_FIJOS or g["feriado"]),
        "temp_actual": g["temp_actual"],
        "temp_next24": g["temp_prev"],
    }
    X = pd.DataFrame([fila])[FEATURES]

    yhat = float(reg["modelo"].predict(X)[0])
    alerta_reg = bool(yhat > META)
    alerta_clf = bool(clf["modelo"].predict(X)[0])

    franja, pct = franja_cosphi(g["cosphi"])
    energia = max(yhat, 0.0) * g["tarifa"]
    recargo = energia * pct
    zona_gris = abs(yhat - META) <= MAE

    subs = {"Cocina": g["sub1"], "Lavadero": g["sub2"], "Termotanque/Aire": g["sub3"]}
    total_sub = sum(subs.values())
    mayor = max(subs, key=subs.get)
    parte = (subs[mayor] / total_sub * 100) if total_sub > 0 else 0

    return {
        "kwh": yhat, "mae": MAE,
        "kwh_min": yhat - MAE, "kwh_max": yhat + MAE,
        "meta": META,
        "diferencia": yhat - META,
        "alerta_reg": alerta_reg,
        "alerta_clf": alerta_clf,
        "coinciden": alerta_reg == alerta_clf,
        "zona_gris": zona_gris,
        "cosphi": g["cosphi"], "franja": franja, "recargo_pct": int(pct * 100),
        "costo_energia": energia, "costo_recargo": recargo, "costo_total": energia + recargo,
        "tarifa": g["tarifa"],
        "mayor": mayor, "parte": parte, "parte_kwh": subs[mayor],
    }


def leer_form():
    fecha_txt = request.form.get("fecha") or date.today().isoformat()
    try:
        d = date.fromisoformat(fecha_txt)
    except ValueError:
        d = date.today()

    bruto = {c: request.form.get(c) for c in CAMPOS_NUM}
    fallidos = [c for c, v in bruto.items() if f(v, None) is None and v not in (None, "")]

    g = {
        "fecha": d,
        "hora": int(f(bruto["hora"], 12)),
        "kwh_ultima_hora": f(bruto["kwh_ultima_hora"], 1.0),
        "kwh_24h": f(bruto["kwh_24h"], 25.0),
        "kwh_semana": f(bruto["kwh_semana"], 25.0),
        "kvarh_24h": f(bruto["kvarh_24h"], 8.0),
        "sub1": f(bruto["sub1"], 3.0),
        "sub2": f(bruto["sub2"], 4.0),
        "sub3": f(bruto["sub3"], 10.0),
        "volt": f(bruto["volt"], 235.0),
        "temp_actual": f(bruto["temp_actual"], 5.0),
        "temp_prev": f(bruto["temp_prev"], 4.0),
        "feriado": request.form.get("feriado") == "on",
        "tarifa": f(bruto["tarifa"], TARIFA_DEFAULT),
    }
    den = np.sqrt(g["kwh_24h"] ** 2 + g["kvarh_24h"] ** 2)
    g["cosphi"] = g["kwh_24h"] / den if den > 0 else 0.0
    return g, fallidos


@app.route("/", methods=["GET", "POST"])
def index():
    errores, resultado, g = [], None, None
    if request.method == "POST":
        g, fallidos = leer_form()
        errores = validar(g, fallidos)
        if not errores:
            resultado = predecir(g)
    if enero_tabla is not None:
        df = enero_tabla.reset_index()
        enero = df.where(pd.notnull(df), None).to_dict("records")
    else:
        enero = []
    return render_template("index.html", errores=errores, r=resultado, g=g,
                           enero=enero, meta=META, mae=MAE, tarifa_default=TARIFA_DEFAULT)


if __name__ == "__main__":
    app.run(debug=True)
