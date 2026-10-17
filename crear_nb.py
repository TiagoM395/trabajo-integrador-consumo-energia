import nbformat as nbf
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

cells = []

def md(t):
    cells.append(new_markdown_cell(t))

def code(t):
    cells.append(new_code_cell(t))

md("""# TP Integrador - Aprendizaje Automatico
## Prediccion de consumo electrico de un hogar

**Entrega 2 y 3 - Preparacion, baselines, regresion y clasificacion**

Dos tareas sobre el mismo dataset (UCI *Individual Household Electric Power Consumption*):
1. **Regresion:** energia activa de las proximas 24 h (kWh).
2. **Clasificacion:** `me_paso = 1` si esas proximas 24 h superan la meta diaria.

**Tarea complementaria:** comparador estacional que compara el mes de enero de los ultimos anios y estima el enero siguiente (2011).

Momento de la prediccion: cualquier hora del dia, usando solo lo medido hasta ese instante. Meta diaria = consumo diario promedio del conjunto de entrenamiento.""")

code("""# ============================================================
# Configuracion general
# ============================================================
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import joblib
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                             accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix)

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
matplotlib.rcParams["figure.figsize"] = (10, 4)

# Carpeta raiz del proyecto (funciona si el notebook se ejecuta desde notebooks/)
BASE = Path.cwd()
if not (BASE / "datos").exists() and (BASE.parent / "datos").exists():
    BASE = BASE.parent
print("Raiz del proyecto:", BASE)""")

code("""%matplotlib inline""")

md("""## 1. Carga de datos y control de calidad

El dataset original trae una medicion por minuto de un hogar en Sceaux (Francia), de diciembre 2006 a noviembre 2010. Los faltantes vienen codificados como `?`.""")

code("""DATA = BASE / "datos" / "household_power_consumption.txt"
raw = pd.read_csv(DATA, sep=";", na_values="?", low_memory=False)

# Timestamp
raw["datetime"] = pd.to_datetime(raw["Date"] + " " + raw["Time"],
                                 format="%d/%m/%Y %H:%M:%S", errors="coerce")

num_cols = ["Global_active_power", "Global_reactive_power", "Voltage",
            "Global_intensity", "Sub_metering_1", "Sub_metering_2", "Sub_metering_3"]
raw[num_cols] = raw[num_cols].apply(pd.to_numeric, errors="coerce")

print("Filas crudas:", len(raw))
print("Fechas invalidas:", raw["datetime"].isna().sum())
print("Timestamps duplicados:", raw["datetime"].duplicated().sum())
print("\\nFaltantes por columna (%):")
print((raw[num_cols].isna().mean() * 100).round(2))

raw = raw.dropna(subset=["datetime"]).sort_values("datetime").set_index("datetime")
print("\\nRango temporal:", raw.index.min(), "->", raw.index.max())""")

code("""# Valores imposibles / fuera de rango fisico
print("Voltage fuera de [180, 260]:", ((raw["Voltage"] < 180) | (raw["Voltage"] > 260)).sum())
print("Potencias negativas active:", (raw["Global_active_power"] < 0).sum())
print("Potencias negativas reactive:", (raw["Global_reactive_power"] < 0).sum())
print("Intensidad negativa:", (raw["Global_intensity"] < 0).sum())""")

md("""## 2. Agregacion horaria y energia

`Global_active_power` esta en kW (promedio por minuto). La energia de una hora es `potencia_media x 1 h` = **kWh**. La reactiva (`Global_reactive_power`, en kVAr) da **kVArh**. Los submedidores vienen en Wh por minuto, por lo que se **suman** y se dividen por 1000.

Solo se conservan las horas con al menos **75%** de minutos medidos (filtro de calidad).""")

code("""res = raw.resample("h")
count = res["Global_active_power"].count()

base = pd.DataFrame(index=count.index)
base["cobertura"] = count / 60.0
base["kwh_h"] = res["Global_active_power"].mean()          # kW medio x 1 h = kWh/h
base["kvarh_h"] = res["Global_reactive_power"].mean()      # kVArh de la hora
base["volt"] = res["Voltage"].mean()
base["sub1_kwh"] = res["Sub_metering_1"].sum() / 1000.0    # Wh -> kWh
base["sub2_kwh"] = res["Sub_metering_2"].sum() / 1000.0
base["sub3_kwh"] = res["Sub_metering_3"].sum() / 1000.0

print("Horas totales:", len(base))
base = base[base["cobertura"] >= 0.75]
print("Horas conservadas (cobertura >= 75%):", len(base))
print("Horas descartadas:", (count / 60.0 < 0.75).sum())
base = base.drop(columns="cobertura")""")

md("""## 3. Variables predictoras y control de fugas

**Disponibles al momento de la consulta (hora t):** energia de la ultima hora, energia de las ultimas 24 h, mismas 24 h de la semana anterior, reactiva y cos Ï† de las ultimas 24 h, submedidores de las ultimas 24 h, voltaje medio, calendario y temperatura.

**Descartadas por fuga:**
- `Global_intensity` = potencia / voltaje (objetivo disfrazado).
- Potencia, reactiva y submedidores de las horas **futuras** (son el objetivo).
- Fecha como numero continuo (no generaliza).

Cos Ï† del periodo = P / sqrt(P^2 + Q^2) con las **energias sumadas** (como factura la distribuidora).""")

code("""h = base.copy()

h["active_24"] = h["kwh_h"].rolling(24).sum()
h["active_prevweek"] = h["kwh_h"].rolling(24).sum().shift(168)   # mismas 24 h, semana anterior
h["reactive_24"] = h["kvarh_h"].rolling(24).sum()
for s in [1, 2, 3]:
    h[f"sub{s}_24"] = h[f"sub{s}_kwh"].rolling(24).sum()
h["volt_24"] = h["volt"].rolling(24).mean()

den = np.sqrt(h["active_24"] ** 2 + h["reactive_24"] ** 2)
h["cosphi_24"] = np.where(den > 0, h["active_24"] / den, np.nan)
print("Horas:", len(h))""")

code("""# Calendario
h["hour"] = h.index.hour
h["dayofweek"] = h.index.dayofweek
h["month"] = h.index.month
h["is_weekend"] = (h.index.dayofweek >= 5).astype(int)
feriados_fijos = {(1, 1), (5, 1), (5, 8), (7, 14), (8, 15), (11, 1), (11, 11), (12, 25)}
h["is_feriado"] = [(m, d) in feriados_fijos for m, d in zip(h.index.month, h.index.day)]

# Temperatura (Open-Meteo, archivo historico diario)
clima = pd.read_csv(BASE / "datos" / "clima_sceaux.csv", parse_dates=["date"]).set_index("date")
temp_diaria = clima["temp_mean"]
dias = h.index.normalize()
h["temp_actual"] = temp_diaria.reindex(dias).values
h["temp_next24"] = temp_diaria.reindex(dias + pd.Timedelta(days=1)).values

# Variable objetivo: energia de las proximas 24 h (t+1 .. t+24)
h["y_reg"] = h["kwh_h"].rolling(24).sum().shift(-24)
print("Filas con objetivo:", h["y_reg"].notna().sum())
h[["kwh_h", "active_24", "cosphi_24", "temp_actual", "y_reg"]].tail()""")

md("""### 3.1 Separacion cronologica (regla 4 y 7)

Las ventanas de 24 h se superponen: la consulta de las 19:00 y la de las 20:00 comparten 23 de 24 horas. Un split al azar filtraria el test en el entrenamiento. Por eso se separa **por tiempo**, con un **hueco de 48 h** entre bloques, y el test se reserva para el final.""")

code("""FEATURES = ["kwh_h", "active_24", "active_prevweek", "reactive_24", "cosphi_24",
            "sub1_24", "sub2_24", "sub3_24", "volt_24",
            "hour", "dayofweek", "month", "is_weekend", "is_feriado",
            "temp_actual", "temp_next24"]

data = h.dropna(subset=FEATURES + ["y_reg"]).copy()
print("Registros utiles:", len(data), "| predictores:", len(FEATURES))

def split_cronologico(frame, frac_train=0.70, frac_val=0.15, gap=48):
    n = len(frame)
    i1 = int(n * frac_train)
    i2 = int(n * (frac_train + frac_val))
    train = frame.iloc[:i1].copy()
    val = frame.iloc[i1 + gap:i2].copy()
    test = frame.iloc[i2 + gap:].copy()
    return train, val, test

train, val, test = split_cronologico(data)
print("train:", train.index.min(), "->", train.index.max(), len(train))
print("val  :", val.index.min(), "->", val.index.max(), len(val))
print("test :", test.index.min(), "->", test.index.max(), len(test))""")

code("""# Meta diaria = consumo diario promedio de ENTRENAMIENTO (queda fija)
meta = train["y_reg"].mean()
print(f"Meta diaria (umbral): {meta:.3f} kWh")

for nombre, sub in [("train", train), ("val", val), ("test", test)]:
    sub["me_paso"] = (sub["y_reg"] > meta).astype(int)
    print(f"{nombre}: me_paso=1 -> {sub['me_paso'].mean()*100:.1f}%")""")

md("""## 4. Baselines (DummyRegressor y DummyClassifier)

Todo modelo debe compararse contra un baseline tonto. La regla de oro del problema es el **baseline estacional** de la tarea complementaria: 'manana consumo lo mismo que hace un ano'.""")

code("""X_train, y_train = train[FEATURES], train["y_reg"]
X_val, y_val = val[FEATURES], val["y_reg"]
X_test, y_test = test[FEATURES], test["y_reg"]

clf_train, clf_val, clf_test = train["me_paso"], val["me_paso"], test["me_paso"]

def metricas_reg(y, yp):
    return {"MAE": mean_absolute_error(y, yp),
            "RMSE": np.sqrt(mean_squared_error(y, yp)),
            "R2": r2_score(y, yp)}

dummy_reg = DummyRegressor(strategy="mean").fit(X_train, y_train)
print("DummyRegressor (validacion):", {k: round(v, 3) for k, v in metricas_reg(y_val, dummy_reg.predict(X_val)).items()})

dummy_clf = DummyClassifier(strategy="stratified", random_state=RANDOM_STATE).fit(X_train, clf_train)
pc = dummy_clf.predict(X_val)
print("DummyClassifier (validacion): acc=%.3f prec=%.3f rec=%.3f f1=%.3f" % (
    accuracy_score(clf_val, pc), precision_score(clf_val, pc, zero_division=0),
    recall_score(clf_val, pc, zero_division=0), f1_score(clf_val, pc, zero_division=0)))""")

md("""## 5. Regresion: energia de las proximas 24 h

Se comparan los modelos obligatorios: DummyRegressor, DecisionTreeRegressor y KNeighborsRegressor con StandardScaler dentro de un Pipeline. Se prueban distintas profundidades y valores de k, y se elige con **validacion** (nunca con el test).""")

code("""candidatos_reg = {"DummyRegressor(media)": DummyRegressor(strategy="mean")}
for depth in [3, 5, 8, 12, None]:
    candidatos_reg[f"DecisionTree depth={depth}"] = DecisionTreeRegressor(
        max_depth=depth, random_state=RANDOM_STATE)
for k in [5, 15, 25]:
    candidatos_reg[f"KNN k={k}"] = Pipeline([
        ("scaler", StandardScaler()),
        ("model", KNeighborsRegressor(n_neighbors=k, n_jobs=-1))])

filas = []
for nombre, modelo in candidatos_reg.items():
    modelo.fit(X_train, y_train)
    filas.append({"modelo": nombre, **metricas_reg(y_val, modelo.predict(X_val))})
reg_tabla = pd.DataFrame(filas).sort_values("MAE").reset_index(drop=True)
best_reg_name = reg_tabla.iloc[0]["modelo"]
print(reg_tabla.round(3).to_string(index=False))""")

code("""# Reentreno del mejor con train + validacion y evaluacion final en test
best_reg = candidatos_reg[best_reg_name]
X_trval = pd.concat([X_train, X_val])
y_trval = pd.concat([y_train, y_val])
best_reg.fit(X_trval, y_trval)

pred_test = best_reg.predict(X_test)
reg_test = metricas_reg(y_test, pred_test)
print("Mejor regresor:", best_reg_name)
print("Test:", {k: round(v, 3) for k, v in reg_test.items()})

residuos = y_test - pred_test
print("\\nResiduos: media=%.3f  desvio=%.3f  p5=%.2f  p95=%.2f" % (
    residuos.mean(), residuos.std(), residuos.quantile(0.05), residuos.quantile(0.95)))

fig, ax = plt.subplots()
ax.scatter(pred_test, y_test, s=6, alpha=0.3)
lim = [y_test.min(), y_test.max()]
ax.plot(lim, lim, "r--", lw=1)
ax.set_xlabel("Predicho (kWh/24h)"); ax.set_ylabel("Real (kWh/24h)")
ax.set_title("Regresion - test"); plt.tight_layout(); plt.show()""")

md("""## 6. Clasificacion: me paso de la meta

Modelos obligatorios: DummyClassifier, DecisionTreeClassifier, KNeighborsClassifier (Pipeline + StandardScaler) y GaussianNB. Metricas: accuracy, precision, recall, F1 y matriz de confusion.""")

code("""candidatos_clf = {"DummyClassifier(estratificado)": DummyClassifier(strategy="stratified", random_state=RANDOM_STATE)}
for depth in [3, 5, 8, 12, None]:
    candidatos_clf[f"DecisionTree depth={depth}"] = DecisionTreeClassifier(
        max_depth=depth, random_state=RANDOM_STATE)
for k in [5, 15, 25]:
    candidatos_clf[f"KNN k={k}"] = Pipeline([
        ("scaler", StandardScaler()),
        ("model", KNeighborsClassifier(n_neighbors=k, n_jobs=-1))])
candidatos_clf["GaussianNB"] = GaussianNB()

def metricas_clf(y, yp):
    return {"accuracy": accuracy_score(y, yp),
            "precision": precision_score(y, yp, zero_division=0),
            "recall": recall_score(y, yp, zero_division=0),
            "f1": f1_score(y, yp, zero_division=0)}

filas = []
for nombre, modelo in candidatos_clf.items():
    modelo.fit(X_train, clf_train)
    filas.append({"modelo": nombre, **metricas_clf(clf_val, modelo.predict(X_val))})
clf_tabla = pd.DataFrame(filas).sort_values("f1", ascending=False).reset_index(drop=True)
best_clf_name = clf_tabla.iloc[0]["modelo"]
print(clf_tabla.round(3).to_string(index=False))""")

code("""best_clf = candidatos_clf[best_clf_name]
clf_trval = pd.concat([clf_train, clf_val])
best_clf.fit(X_trval, clf_trval)
pred_clf_test = best_clf.predict(X_test)
print("Mejor clasificador:", best_clf_name)
print({k: round(v, 3) for k, v in metricas_clf(clf_test, pred_clf_test).items()})
print("\\nMatriz de confusion (filas=real, col=predicho):")
print(confusion_matrix(clf_test, pred_clf_test))""")

md("""## 7. Integracion: clasificador directo vs regresion + umbral

Mismos casos de test para ambos sistemas:

| Sistema | Procedimiento |
|---|---|
| Clasificador directo | predice 0/1 directamente |
| Regresion + umbral | predice kWh y luego aplica `> meta` |

Esquema de costos 3:1 - un **falso negativo** (dijo 'no te pasas' y se paso) cuesta 3 veces mas que un **falso positivo** (dijo 'te pasas' y no se paso), porque el exceso se paga a precio pleno y agrava el recargo por cos Ï†.""")

code("""alerta_reg = (best_reg.predict(X_test) > meta).astype(int)
alerta_clf = best_clf.predict(X_test)
y_true = clf_test.values

def sistema(y, yp):
    tn, fp, fn, tp = confusion_matrix(y, yp).ravel()
    return {"accuracy": accuracy_score(y, yp),
            "precision": precision_score(y, yp, zero_division=0),
            "recall": recall_score(y, yp, zero_division=0),
            "f1": f1_score(y, yp, zero_division=0),
            "FP": fp, "FN": fn, "costo (3*FN+FP)": 3 * fn + fp}

integradora = pd.DataFrame({
    "Clasificador directo": sistema(y_true, alerta_clf),
    "Regresion + umbral": sistema(y_true, alerta_reg),
}).T
print(integradora.round(3).to_string())""")

code("""# Casos cercanos al umbral = zona gris
mae_test = reg_test["MAE"]
cerca = (best_reg.predict(X_test) - meta).__abs__() <= mae_test
desacuerdo = (alerta_clf != alerta_reg)
print(f"Zona gris (|pred - meta| <= MAE={mae_test:.2f}): {cerca.mean()*100:.1f}% de los casos")
print(f"Desacuerdos entre sistemas: {desacuerdo.sum()} ({desacuerdo.mean()*100:.1f}%)")
print(f"De esos desacuerdos, {100*(cerca & desacuerdo).sum()/max(desacuerdo.sum(),1):.0f}% cae en la zona gris")""")

md("""## 8. Tarea complementaria - comparador estacional de enero

Objetivo: comparar el gasto del mes de **enero** de los ultimos anios y estimar el **enero de 2011** (el siguiente al dataset, que termina el 26/11/2010).

Se trabaja a nivel **diario** con variables de calendario y un rezago largo:
- `kwh_year_ago`: consumo del **mismo dia del anio anterior** (disponible al predecir).
- `month`, `doy`, `dayofweek`, `is_weekend`.

No se usan rezagos cortos (ayer / semana pasada) porque para enero 2011 no hay diciembre 2010 medido.

**Validacion:** se entrena con todo lo anterior a enero 2010 y se valida en **enero 2010**, comparando contra dos baselines: DummyRegressor y el **estacional ingenuo** (repetir el mismo dia del ano anterior).""")

code("""# Serie diaria (min 20 horas validas por dia)
daily = pd.DataFrame({
    "kwh_day": base["kwh_h"].resample("D").sum(min_count=20),
})
daily = daily.join(temp_diaria.rename("temp_mean"))
idx = daily.index
daily["month"] = idx.month
daily["doy"] = idx.dayofyear
daily["dayofweek"] = idx.dayofweek
daily["is_weekend"] = (idx.dayofweek >= 5).astype(int)
daily["kwh_year_ago"] = daily["kwh_day"].reindex(idx - pd.DateOffset(years=1)).values

SEAS_FEAT = ["month", "doy", "dayofweek", "is_weekend", "kwh_year_ago"]
seas = daily.dropna(subset=SEAS_FEAT + ["kwh_day"]).copy()
print("Dias utiles:", len(seas), "| rango:", seas.index.min().date(), "->", seas.index.max().date())""")

code("""cut = pd.Timestamp("2010-01-01")
fin = pd.Timestamp("2010-02-01")
s_tr = seas[seas.index < cut]
s_val = seas[(seas.index >= cut) & (seas.index < fin)]
print("train:", len(s_tr), "| validacion (enero 2010):", len(s_val))

cand_seas = {"DummyRegressor(media)": DummyRegressor(strategy="mean"),
             "Regresion lineal": LinearRegression(),
             "DecisionTree depth=5": DecisionTreeRegressor(max_depth=5, random_state=RANDOM_STATE),
             "KNN k=5": Pipeline([("scaler", StandardScaler()),
                                  ("model", KNeighborsRegressor(n_neighbors=5))])}

res = []
for nombre, m in cand_seas.items():
    m.fit(s_tr[SEAS_FEAT], s_tr["kwh_day"])
    res.append({"modelo": nombre, **metricas_reg(s_val["kwh_day"], m.predict(s_val[SEAS_FEAT]))})

# Baseline estacional ingenuo: mismo dia del anio anterior
res.append({"modelo": "Estacional ingenuo (ano anterior)",
            **metricas_reg(s_val["kwh_day"], s_val["kwh_year_ago"])})

seas_tabla = pd.DataFrame(res).sort_values("MAE").reset_index(drop=True)
best_seas_name = seas_tabla.iloc[0]["modelo"]
print("Mejor modelo estacional:", best_seas_name)
print(seas_tabla.round(3).to_string(index=False))""")

code("""# Reentreno con todo el historico y pronostico de enero 2011
best_seas = cand_seas.get(best_seas_name)
if best_seas is None:  # si gana el estacional ingenuo, se usa ese como modelo
    best_seas = None
if best_seas is not None:
    best_seas.fit(seas[SEAS_FEAT], seas["kwh_day"])

fut = pd.date_range("2011-01-01", "2011-01-31")
jan11 = pd.DataFrame(index=fut)
jan11["month"] = fut.month
jan11["doy"] = fut.dayofyear
jan11["dayofweek"] = fut.dayofweek
jan11["is_weekend"] = (fut.dayofweek >= 5).astype(int)
jan11["kwh_year_ago"] = seas["kwh_day"].reindex(fut - pd.DateOffset(years=1)).values
# Si falta el mismo dia del ano anterior, se usa el promedio diario de enero
enero_medio = seas[seas.index.month == 1]["kwh_day"].mean()
jan11["kwh_year_ago"] = jan11["kwh_year_ago"].fillna(enero_medio)

rmse_val_seas = seas_tabla.loc[0, "RMSE"]
if best_seas is None:
    jan11["pred"] = jan11["kwh_year_ago"]
else:
    jan11["pred"] = best_seas.predict(jan11[SEAS_FEAT])

pred_jan11 = jan11["pred"].sum()
rmse_mes = rmse_val_seas * np.sqrt(len(jan11))
print(f"Enero 2011 estimado: {pred_jan11:.1f} kWh (+/- {rmse_mes:.1f} kWh)")
print(jan11[["pred", "kwh_year_ago"]].round(2).to_string())""")

code("""TARIFA = 150.0  # $/kWh asumida (editable desde la app)

# Totales reales de enero por anio (se usa la serie diaria completa, incluye 2007)
m1 = daily[daily.index.month == 1]
eneros = m1.groupby(m1.index.year)["kwh_day"].agg(["count", "sum"])
eneros.columns = ["dias", "kwh"]
eneros["kwh_dia"] = eneros["kwh"] / eneros["dias"]
eneros["costo_$"] = eneros["kwh"] * TARIFA
eneros = eneros.astype({"dias": int})

resumen = eneros.copy()
resumen.loc[2011] = [len(jan11), pred_jan11, pred_jan11 / len(jan11), pred_jan11 * TARIFA]
resumen["var_%"] = resumen["kwh_dia"].pct_change() * 100
resumen = resumen[["dias", "kwh", "kwh_dia", "costo_$", "var_%"]]
resumen.index.name = "anio"
print("Tarifa asumida: %.0f $/kWh" % TARIFA)
print("2011 es estimado; var_% se calcula sobre el consumo diario promedio (kwh_dia).")
print(resumen.round(2).to_string())""")

code("""fig, ax = plt.subplots()
colores = ["#4C72B0"] * (len(resumen) - 1) + ["#DD8452"]
ax.bar(resumen.index.astype(str), resumen["kwh"], color=colores)
ax.errorbar(str(2011), pred_jan11, yerr=rmse_mes, fmt="none", ecolor="black", capsize=4)
ax.set_ylabel("kWh en enero"); ax.set_title("Gasto de enero: historico vs estimado 2011")
for i, (idx_, row) in enumerate(resumen.iterrows()):
    ax.text(i, row["kwh"] + 4, f"{row['kwh']:.0f}", ha="center", fontsize=9)
plt.tight_layout(); plt.show()""")

md("""## 9. Guardado de artefactos

Se guardan los Pipelines ya entrenados (no se reentrena en la app) y la lista de variables y el umbral.""")

code("""modelos_dir = BASE / "modelos"
modelos_dir.mkdir(exist_ok=True)

joblib.dump({"modelo": best_reg, "features": FEATURES, "meta": meta,
             "nombre": best_reg_name, "mae": reg_test["MAE"], "rmse": reg_test["RMSE"]},
            modelos_dir / "reg_24h.pkl")
joblib.dump({"modelo": best_clf, "features": FEATURES, "meta": meta,
             "nombre": best_clf_name}, modelos_dir / "clf_me_paso.pkl")
joblib.dump({"modelo": best_seas, "features": SEAS_FEAT, "nombre": best_seas_name,
             "tarifa_default": TARIFA, "rmse_mes": rmse_mes},
            modelos_dir / "reg_estacional.pkl")

# Tablas del comparador estacional para la app
resumen.to_csv(modelos_dir / "enero_resumen.csv")
jan11[["pred", "kwh_year_ago"]].to_csv(modelos_dir / "enero2011_diario.csv")

# Compatibilidad con la Entrega 2 (baselines)
joblib.dump(dummy_reg, modelos_dir / "dummy_reg.pkl")
joblib.dump(dummy_clf, modelos_dir / "dummy_clf.pkl")

print("Modelos guardados en", modelos_dir)
print(sorted(p.name for p in modelos_dir.iterdir()))""")

md("""## 10. Conclusiones y limitaciones

- El mejor regresor se compara contra el DummyRegressor y, en la tarea estacional, contra el baseline estacional ingenuo.
- El MAE se traduce al contexto: equivocarse +/- X kWh por dia equivale a +/- $Y con la tarifa asumida.
- Los desacuerdos entre el clasificador directo y la regresion + umbral se concentran cerca del umbral (zona gris).
- **Limitaciones:** un solo hogar (Sceaux, Francia 2006-2010); solo hay **4 eneros completos**, por lo que el pronostico de un mes entero es de baja confianza y se reporta con su rango de error; la temperatura se usa como valor real (simplificacion declarada); el costo en pesos depende de una tarifa asumida, no del dataset.
- **No usar** para otro hogar sin reentrenar, ni para reclamar formalmente un recargo (vale la medicion de la distribuidora).""")

nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata["language_info"] = {"name": "python"}

out = r"C:\Users\romin\Desktop\tpintegrador\notebooks\entrenamiento.ipynb"
with open(out, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("Notebook generado:", out, "| celdas:", len(cells))
