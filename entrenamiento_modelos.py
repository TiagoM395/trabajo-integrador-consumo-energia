"""Entrenamiento y evaluación reproducibles para el trabajo integrador.

Uso:
    python entrenamiento_modelos.py

El dataset UCI se descarga en la caché del usuario. No se modifica ningún modelo
usado por la aplicación; el módulo informa la evaluación y conserva los candidatos
en memoria para que el notebook pueda inspeccionarlos.
"""
from __future__ import annotations

import io
import math
import urllib.request
import zipfile
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

ROOT = Path(__file__).resolve().parent
UCI_URL = (
    "https://archive.ics.uci.edu/static/public/235/"
    "individual+household+electric+power+consumption.zip"
)
CACHE = Path.home() / ".cache" / "trabajo-consumo-energia"
DATASET_FILE = "household_power_consumption.txt"
WEATHER_PATH = ROOT / "clima_sceaux.csv"
META_KWH = 25.917658045475125
FALSE_NEGATIVE_COST = 3
FALSE_POSITIVE_COST = 1
MINUTES_PER_HOUR = 45

FEATURES = [
    "kwh_h",
    "active_24",
    "active_prevweek",
    "reactive_24",
    "cosphi_24",
    "sub1_24",
    "sub2_24",
    "sub3_24",
    "volt_24",
    "hour",
    "dayofweek",
    "month",
    "is_weekend",
    "is_feriado",
    "temp_actual",
    "temp_next24",
]
RAW_COLUMNS = {
    "Global_active_power": "active",
    "Global_reactive_power": "reactive",
    "Voltage": "voltage",
    "Sub_metering_1": "sub1",
    "Sub_metering_2": "sub2",
    "Sub_metering_3": "sub3",
}


def _hour_key(date_text: str, time_text: str) -> int:
    """Encode local calendar hour as an integer, avoiding platform date parsers."""
    try:
        day_text, month_text, year_text = date_text.split("/")
        day = date(int(year_text), int(month_text), int(day_text))
        hour_text, minute_text, second_text = time_text.split(":")
        hour, minute, second = int(hour_text), int(minute_text), int(second_text)
        if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
            return -1
        return day.toordinal() * 24 + hour
    except (AttributeError, TypeError, ValueError):
        return -1


def _download_archive() -> bytes:
    """Download the public UCI archive once and reuse the per-user cache."""
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / "uci-household-power.zip"
    if not cached.exists():
        request = urllib.request.Request(
            UCI_URL, headers={"User-Agent": "trabajo-integrador-consumo-energia"}
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
        if not zipfile.is_zipfile(io.BytesIO(data)):
            raise ValueError("La descarga de UCI no es un archivo ZIP válido.")
        cached.write_bytes(data)
    return cached.read_bytes()


def load_raw_data(archive: bytes | None = None) -> tuple[pd.DataFrame, dict]:
    """Read UCI in chunks, aggregate it to hours, and audit raw data quality."""
    archive = archive if archive is not None else _download_archive()
    sums_and_counts = None
    raw_rows = missing_cells = invalid_timestamps = duplicate_timestamps = 0
    impossible_rows = 0
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        if DATASET_FILE not in zipped.namelist():
            raise ValueError(f"No se encontró {DATASET_FILE} en el archivo UCI.")
        with zipped.open(DATASET_FILE) as source:
            chunks = pd.read_csv(
                source,
                sep=";",
                usecols=["Date", "Time", *RAW_COLUMNS],
                na_values=["?"],
                low_memory=False,
                chunksize=100_000,
            )
            measurements = list(RAW_COLUMNS)
            for chunk in chunks:
                raw_rows += len(chunk)
                chunk[measurements] = chunk[measurements].apply(pd.to_numeric, errors="coerce")
                missing_cells += int(chunk[measurements].isna().sum().sum())
                clock = np.fromiter(
                    (_hour_key(d, t) for d, t in zip(chunk["Date"], chunk["Time"])),
                    dtype=np.int64,
                    count=len(chunk),
                )
                chunk.index = clock
                invalid_timestamps += int((chunk.index < 0).sum())
                chunk = chunk.loc[chunk.index >= 0]
                duplicate_rows = chunk.duplicated(
                    subset=["Date", "Time", *measurements], keep="last"
                )
                duplicate_timestamps += int(duplicate_rows.sum())
                chunk = chunk.loc[~duplicate_rows]
                impossible = (
                    (chunk["Global_active_power"] < 0)
                    | (chunk["Global_active_power"] > 15)
                    | (chunk["Global_reactive_power"] < 0)
                    | (chunk["Voltage"] <= 0)
                    | (
                        chunk[
                            ["Sub_metering_1", "Sub_metering_2", "Sub_metering_3"]
                        ]
                        < 0
                    ).any(axis=1)
                )
                impossible_rows += int(impossible.sum())
                chunk.loc[impossible, measurements] = np.nan
                hourly = chunk.groupby(chunk.index)[measurements].agg(["sum", "count"])
                sums_and_counts = (
                    hourly
                    if sums_and_counts is None
                    else sums_and_counts.add(hourly, fill_value=0)
                )

    if sums_and_counts is None:
        raise ValueError("El dataset UCI no contiene mediciones utilizables.")
    all_hours = pd.Index(
        range(int(sums_and_counts.index.min()), int(sums_and_counts.index.max()) + 1),
        name="hour_id",
    )
    sums_and_counts = sums_and_counts.reindex(all_hours)
    hourly = pd.DataFrame(index=sums_and_counts.index)
    counts = pd.DataFrame(index=sums_and_counts.index)
    for original, name in RAW_COLUMNS.items():
        hourly[name] = sums_and_counts[(original, "sum")] / sums_and_counts[(original, "count")]
        counts[name] = sums_and_counts[(original, "count")]
    for sub in ("sub1", "sub2", "sub3"):
        hourly[sub] = (
            sums_and_counts[(next(key for key, value in RAW_COLUMNS.items() if value == sub), "sum")]
            / 1000
            * MINUTES_PER_HOUR
            / counts[sub]
        )
    enough_data = counts.ge(MINUTES_PER_HOUR).all(axis=1)
    hourly.loc[~enough_data] = np.nan
    audit = {
        "Filas descargadas": raw_rows,
        "Celdas faltantes (antes de limpiar)": missing_cells,
        "Marcas de tiempo inválidas": invalid_timestamps,
        "Filas de medición duplicadas exactas (se conserva una)": duplicate_timestamps,
        "Horas con más de 60 mediciones en una variable": int((counts > 60).any(axis=1).sum()),
        "Filas con valores físicamente imposibles": impossible_rows,
    }
    return hourly, audit


def _french_holidays(year: int) -> set[date]:
    """French national public holidays, including Easter-dependent dates."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    easter = date(year, month, day)
    return {
        date(year, 1, 1),
        date(year, 5, 1),
        date(year, 5, 8),
        date(year, 7, 14),
        date(year, 8, 15),
        date(year, 11, 1),
        date(year, 11, 11),
        date(year, 12, 25),
        easter + timedelta(days=1),
        easter + timedelta(days=39),
        easter + timedelta(days=50),
    }


def _hourly_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate the hourly measurements produced by ``load_raw_data``."""
    expected = {"active", "reactive", "voltage", "sub1", "sub2", "sub3"}
    if not expected.issubset(raw.columns):
        raise ValueError(f"Faltan columnas horarias: {sorted(expected - set(raw.columns))}")
    return raw.sort_index()


def build_dataset(
    raw: pd.DataFrame, weather_path: Path = WEATHER_PATH
) -> tuple[pd.DataFrame, dict]:
    """Create one row per hourly forecast origin using only information available then."""
    hourly = _hourly_data(raw)
    weather_data = pd.read_csv(weather_path)
    weather = dict(zip(weather_data["date"], weather_data["temp_mean"]))
    dates = pd.Series(
        [date.fromordinal(int(hour_id) // 24) for hour_id in hourly.index],
        index=hourly.index,
    )
    prior_dates = dates.map(lambda d: (d - timedelta(days=1)).isoformat())
    prior_temperature = prior_dates.map(weather)

    history = {}
    for field in ("active", "reactive", "sub1", "sub2", "sub3"):
        history[field] = hourly[field].rolling(24, min_periods=24).sum()
    history["voltage"] = hourly["voltage"].rolling(24, min_periods=24).mean()
    previous_week = history["active"].shift(24 * 7)
    target_next24 = (
        hourly["active"]
        .shift(-1)
        .iloc[::-1]
        .rolling(24, min_periods=24)
        .sum()
        .iloc[::-1]
    )

    features = pd.DataFrame(index=hourly.index)
    features["kwh_h"] = hourly["active"]
    features["active_24"] = history["active"]
    features["active_prevweek"] = previous_week
    features["reactive_24"] = history["reactive"]
    features["cosphi_24"] = history["active"] / np.sqrt(
        history["active"].pow(2) + history["reactive"].pow(2)
    )
    for sub in ("sub1", "sub2", "sub3"):
        features[f"{sub}_24"] = history[sub]
    features["volt_24"] = history["voltage"]
    weekdays = dates.map(date.weekday)
    features["hour"] = hourly.index % 24
    features["dayofweek"] = weekdays.to_numpy()
    features["month"] = dates.map(lambda d: d.month).to_numpy()
    features["is_weekend"] = (weekdays >= 5).astype(int).to_numpy()
    years = sorted({d.year for d in dates})
    holiday_dates = set().union(*(_french_holidays(year) for year in years))
    features["is_feriado"] = dates.isin(holiday_dates).astype(int)
    # Daily weather observations are not forecasts. Persistence uses only the last
    # completed day, for both the current condition and the next-24-hour proxy.
    features["temp_actual"] = prior_temperature.to_numpy()
    features["temp_next24"] = prior_temperature.to_numpy()
    features["fecha_hora"] = [
        f"{date.fromordinal(int(hour_id) // 24).isoformat()} {int(hour_id) % 24:02d}:00"
        for hour_id in hourly.index
    ]
    features["target_kwh_next24"] = target_next24
    features["target_exceso"] = (target_next24 > META_KWH).astype("float")

    valid = features[FEATURES + ["target_kwh_next24"]].notna().all(axis=1)
    valid &= features["cosphi_24"].between(0, 1)
    dropped = int((~valid).sum())
    samples = features.loc[valid].copy()
    samples.loc[:, "target_exceso"] = (
        samples["target_kwh_next24"] > META_KWH
    ).astype(int)
    audit = {
        "Horas en la serie agregada": len(hourly),
        "Horas aceptadas (>= 45 de 60 minutos válidos por variable)": int(
            hourly.notna().all(axis=1).sum()
        ),
        "Filas supervisadas descartadas (historial/objetivo/clima incompletos)": dropped,
        "Casos supervisados finales": len(samples),
        "Umbral de exceso (kWh/24 h)": META_KWH,
        "Proporción de excesos": float(samples["target_exceso"].mean()),
    }
    return samples, audit


def chronological_split(samples: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Split by time and purge 24-hour target overlap at each boundary."""
    samples = samples.sort_index()
    first = int(len(samples) * 0.70)
    second = int(len(samples) * 0.85)
    boundary_1, boundary_2 = samples.index[first], samples.index[second]
    train = samples.loc[samples.index < boundary_1 - 24]
    validation = samples.loc[
        (samples.index >= boundary_1)
        & (samples.index < boundary_2 - 24)
    ]
    test = samples.loc[samples.index >= boundary_2]
    if min(len(train), len(validation), len(test)) == 0:
        raise ValueError("La separación temporal produjo un subconjunto vacío.")
    if train.index.max() + 24 >= validation.index.min():
        raise AssertionError("Hay solapamiento entre objetivos de entrenamiento y validación.")
    if validation.index.max() + 24 >= test.index.min():
        raise AssertionError("Hay solapamiento entre objetivos de validación y prueba.")
    return {"entrenamiento": train, "validación": validation, "prueba": test}


def _regressors() -> dict[str, object]:
    candidates: dict[str, object] = {
        "DummyRegressor (media)": DummyRegressor(strategy="mean"),
    }
    for depth in (3, 6, 12, None):
        candidates[f"DecisionTreeRegressor (profundidad={depth})"] = (
            DecisionTreeRegressor(max_depth=depth, random_state=42)
        )
    for neighbors in (5, 25, 50):
        candidates[f"KNeighborsRegressor (k={neighbors})"] = make_pipeline(
            StandardScaler(), KNeighborsRegressor(n_neighbors=neighbors, n_jobs=-1)
        )
    return candidates


def _classifiers() -> dict[str, object]:
    candidates: dict[str, object] = {
        "DummyClassifier (clase mayoritaria)": DummyClassifier(strategy="prior"),
    }
    for depth in (3, 6, 12, None):
        candidates[f"DecisionTreeClassifier (profundidad={depth})"] = (
            DecisionTreeClassifier(max_depth=depth, random_state=42)
        )
    for neighbors in (5, 25, 50):
        candidates[f"KNeighborsClassifier (k={neighbors})"] = make_pipeline(
            StandardScaler(), KNeighborsClassifier(n_neighbors=neighbors, n_jobs=-1)
        )
    candidates["GaussianNB"] = GaussianNB()
    return candidates


def _regression_metrics(y_true: pd.Series, predictions: np.ndarray) -> dict:
    residuals = np.asarray(y_true) - predictions
    return {
        "MAE (kWh)": mean_absolute_error(y_true, predictions),
        "RMSE (kWh)": math.sqrt(mean_squared_error(y_true, predictions)),
        "R²": r2_score(y_true, predictions),
        "Mediana error absoluto (kWh)": float(np.median(np.abs(residuals))),
        "P95 error absoluto (kWh)": float(np.quantile(np.abs(residuals), 0.95)),
    }


def _classification_metrics(y_true: pd.Series, predictions: np.ndarray) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1]).ravel()
    return {
        "Accuracy": accuracy_score(y_true, predictions),
        "Precision (exceso)": precision_score(y_true, predictions, zero_division=0),
        "Recall (exceso)": recall_score(y_true, predictions, zero_division=0),
        "F1 (exceso)": f1_score(y_true, predictions, zero_division=0),
        "TN": int(tn),
        "FP": int(fp),
        "FN": int(fn),
        "TP": int(tp),
        "Costo total (FN=3, FP=1)": int(
            FALSE_NEGATIVE_COST * fn + FALSE_POSITIVE_COST * fp
        ),
    }


def run_experiment() -> dict:
    """Fit all required candidates and evaluate them on common chronological cases."""
    raw, raw_audit = load_raw_data()
    samples, sample_audit = build_dataset(raw)
    splits = chronological_split(samples)
    x_train = splits["entrenamiento"][FEATURES]
    x_validation = splits["validación"][FEATURES]
    x_test = splits["prueba"][FEATURES]
    y_train = splits["entrenamiento"]["target_kwh_next24"]
    y_validation = splits["validación"]["target_kwh_next24"]
    y_test = splits["prueba"]["target_kwh_next24"]
    c_train = splits["entrenamiento"]["target_exceso"]
    c_validation = splits["validación"]["target_exceso"]
    c_test = splits["prueba"]["target_exceso"]

    reg_models = _regressors()
    reg_predictions = {}
    for name, model in reg_models.items():
        model.fit(x_train, y_train)
        reg_predictions[name] = {
            "validación": model.predict(x_validation),
            "prueba": model.predict(x_test),
        }
    reg_validation = pd.DataFrame(
        {
            name: _regression_metrics(y_validation, values["validación"])
            for name, values in reg_predictions.items()
        }
    ).T.sort_values("MAE (kWh)")
    reg_test = pd.DataFrame(
        {
            name: _regression_metrics(y_test, values["prueba"])
            for name, values in reg_predictions.items()
        }
    ).T.sort_values("MAE (kWh)")
    best_reg_name = reg_validation.index[0]

    clf_models = _classifiers()
    clf_predictions = {}
    for name, model in clf_models.items():
        model.fit(x_train, c_train)
        clf_predictions[name] = {
            "validación": model.predict(x_validation),
            "prueba": model.predict(x_test),
        }
    clf_validation = pd.DataFrame(
        {
            name: _classification_metrics(c_validation, values["validación"])
            for name, values in clf_predictions.items()
        }
    ).T.sort_values(["Costo total (FN=3, FP=1)", "F1 (exceso)"], ascending=[True, False])
    clf_test = pd.DataFrame(
        {
            name: _classification_metrics(c_test, values["prueba"])
            for name, values in clf_predictions.items()
        }
    ).T.sort_values(["Costo total (FN=3, FP=1)", "F1 (exceso)"], ascending=[True, False])
    best_clf_name = clf_validation.index[0]

    regression_alert = (reg_predictions[best_reg_name]["prueba"] > META_KWH).astype(int)
    direct_alert = clf_predictions[best_clf_name]["prueba"].astype(int)
    integrated = pd.DataFrame(
        {
            "Regresión + umbral": _classification_metrics(c_test, regression_alert),
            f"Clasificador directo ({best_clf_name})": _classification_metrics(
                c_test, direct_alert
            ),
        }
    ).T
    comparison = pd.DataFrame(
        {
            "real": c_test,
            "alerta_regresion": regression_alert,
            "alerta_clasificador": direct_alert,
            "kwh_real": y_test,
            "kwh_estimado": reg_predictions[best_reg_name]["prueba"],
            "fecha_hora": splits["prueba"]["fecha_hora"],
        },
        index=splits["prueba"].index,
    )
    comparison.loc[:, "coinciden"] = (
        comparison["alerta_regresion"] == comparison["alerta_clasificador"]
    )
    comparison.loc[:, "distancia_umbral_kwh"] = (
        comparison["kwh_real"] - META_KWH
    ).abs()

    residuals = y_test - reg_predictions[best_reg_name]["prueba"]
    error_cases = comparison.assign(
        residuo_kwh=residuals,
        error_absoluto_kwh=residuals.abs(),
    ).sort_values("error_absoluto_kwh", ascending=False)
    near_threshold = comparison.sort_values("distancia_umbral_kwh").head(10)
    false_negatives = comparison.loc[
        (comparison["real"] == 1) & (comparison["alerta_clasificador"] == 0)
    ].sort_values("distancia_umbral_kwh")
    false_positives = comparison.loc[
        (comparison["real"] == 0) & (comparison["alerta_clasificador"] == 1)
    ].sort_values("distancia_umbral_kwh")
    sizes = pd.DataFrame(
        {
            "Casos": {name: len(split) for name, split in splits.items()},
            "Excesos": {
                name: int(split["target_exceso"].sum()) for name, split in splits.items()
            },
            "Proporción de excesos": {
                name: split["target_exceso"].mean() for name, split in splits.items()
            },
        }
    )
    return {
        "raw_audit": raw_audit,
        "sample_audit": sample_audit,
        "split_sizes": sizes,
        "regression_validation": reg_validation,
        "regression_test": reg_test,
        "classification_validation": clf_validation,
        "classification_test": clf_test,
        "integrated_test": integrated,
        "best_regression": best_reg_name,
        "best_classifier": best_clf_name,
        "error_cases": error_cases.head(10),
        "near_threshold": near_threshold,
        "false_negatives": false_negatives.head(10),
        "false_positives": false_positives.head(10),
        "alert_agreement": float(comparison["coinciden"].mean()),
        "models_regression": reg_models,
        "models_classification": clf_models,
        "test_cases": comparison,
    }


def main() -> None:
    result = run_experiment()
    for heading, key in (
        ("Auditoría del dataset original", "raw_audit"),
        ("Preparación y objetivo", "sample_audit"),
    ):
        print(f"\n## {heading}")
        print(pd.Series(result[key]).to_string())
    print("\n## Particiones cronológicas")
    print(result["split_sizes"].to_string())
    print("\n## Regresión — validación")
    print(result["regression_validation"].round(3).to_string())
    print("\n## Regresión — prueba")
    print(result["regression_test"].round(3).to_string())
    print("\n## Clasificación — validación")
    print(result["classification_validation"].round(3).to_string())
    print("\n## Clasificación — prueba")
    print(result["classification_test"].round(3).to_string())
    print("\n## Comparación integrada sobre los mismos casos de prueba")
    print(result["integrated_test"].round(3).to_string())
    print(f"\nAcuerdo entre alertas: {result['alert_agreement']:.1%}")
    print("\n## 10 errores absolutos mayores del regresor elegido")
    print(result["error_cases"].round(3).to_string())
    print("\n## Casos reales más cercanos al umbral")
    print(result["near_threshold"].round(3).to_string())
    print("\n## Falsos negativos del clasificador elegido")
    print(result["false_negatives"].round(3).to_string())
    print("\n## Falsos positivos del clasificador elegido")
    print(result["false_positives"].round(3).to_string())


if __name__ == "__main__":
    main()
