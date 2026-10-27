"""Arma el dataset de eficiencia de electrodomésticos a partir de datos abiertos oficiales.

Fuente: Energy Rating for Household Appliances — Gobierno de Australia (data.gov.au),
licencia Creative Commons Attribution 3.0 Australia. Es el registro de los modelos con
etiqueta energética vendidos en Australia y Nueva Zelanda (datos declarados por fabricantes
a partir de ensayos normalizados).

Uso:
    python datos/preparar_dataset.py            # descarga y procesa
    python datos/preparar_dataset.py --sin-descarga   # usa lo que ya está en datos/crudos/

Salida: datos/electrodomesticos_eficiencia.csv (una fila por modelo).

Columnas principales:
- categoria: heladera | freezer | aire | lavarropas | secarropas | lavavajillas | tv
- tecnologia: "Inverter" / "Velocidad fija" (aires), tipo de secado, tipo de pantalla, etc.
- capacidad + unidad: litros, kg, cubiertos, pulgadas o kW de frío.
- kwh_anio_etiqueta: consumo comparativo declarado en la etiqueta (kWh/año).
- potencia_w: aires = potencia eléctrica de entrada en frío; TV = potencia media encendida.
- indice_rel: consumo del modelo / mediana de su categoría y banda de tamaño (1 = típico).
  En aires: mediana de EER / EER del modelo (más alto = consume más).
- clase_rel: A (mejor) a G (peor) según los séptimos de indice_rel dentro de cada categoría.
  Es una clase ESTIMADA para comparar; no es la etiqueta IRAM argentina.
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).parent
CRUDOS = AQUI / "crudos"
SALIDA = AQUI / "electrodomesticos_eficiencia.csv"
API = "https://data.gov.au/data/api/3/action/package_show?id=energy-rating-for-household-appliances"
FUENTE = "data.gov.au · Energy Rating for Household Appliances (CC BY 3.0 AU)"
ARCHIVOS = {"ac": "Air Conditioners", "rf": "Fridges and Freezers", "cw": "Clothes Washers",
            "cd": "Clothes Dryers", "dw": "Dishwashers", "tv": "Televisions"}
CLASES = list("ABCDEFG")


def descargar() -> None:
    """Busca la URL vigente de cada CSV con la API del portal y lo guarda en datos/crudos/."""
    import json

    CRUDOS.mkdir(exist_ok=True)
    req = urllib.request.Request(API, headers={"User-Agent": "Mozilla/5.0"})
    recursos = json.load(urllib.request.urlopen(req, timeout=60))["result"]["resources"]
    for corto, nombre in ARCHIVOS.items():
        r = next(x for x in recursos if x["name"].strip().startswith(nombre) and x["format"].upper() == "CSV")
        print(f"Descargando {nombre}…")
        req = urllib.request.Request(r["url"], headers={"User-Agent": "Mozilla/5.0"})
        (CRUDOS / f"{corto}.csv").write_bytes(urllib.request.urlopen(req, timeout=120).read())


def _leer(corto: str) -> pd.DataFrame:
    return pd.read_csv(CRUDOS / f"{corto}.csv", low_memory=False, encoding="latin-1")


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def _vigentes(df: pd.DataFrame) -> pd.DataFrame:
    if "SubmitStatus" in df:
        df = df[df["SubmitStatus"].astype(str).str.lower() == "approved"]
    return df


def aires() -> pd.DataFrame:
    df = _vigentes(_leer("ac"))
    df = df[df["Configuration2"].isin(["Single Split System", "Window Wall", "Portable"])]
    frio = _num(df["C-Total Cool Rated"])
    entrada = _num(df["C-Power_Inp_Rated"])
    out = pd.DataFrame({
        "categoria": "aire", "marca": df["Brand"], "modelo": df["Model_No"],
        "tecnologia": df["Is variable speed"].map({"Yes": "Inverter", "No": "Velocidad fija"}),
        "subtipo": df["Configuration2"].map({"Single Split System": "Split", "Window Wall": "Ventana", "Portable": "Portátil"}),
        "capacidad": frio, "unidad": "kW frío", "kwh_anio_etiqueta": float("nan"),
        "potencia_w": entrada * 1000, "eer": frio / entrada,
        "estrellas": _num(df["Star2010_Cool"]), "standby_w": _num(df["avg_pwr_standby_mode"]),
        "frigorias": frio * 860,
    })
    out = out[(out["capacidad"] > 1) & (out["capacidad"] <= 10.5) & (out["eer"].between(1.5, 8))]
    out["banda"] = pd.cut(out["capacidad"], [0, 3, 4.2, 6, 8, 10.5],
                          labels=["hasta 2.600 frig", "3.000 frig", "4.500 frig", "6.000 frig", "más de 6.000 frig"])
    return out


def heladeras() -> pd.DataFrame:
    df = _vigentes(_leer("rf"))
    designacion = df["Designation"].astype(str).str.lower()
    cat = designacion.map(lambda d: "freezer" if d.startswith("freezer") else "heladera")
    out = pd.DataFrame({
        "categoria": cat, "marca": df["Brand"], "modelo": df["Model No"],
        "tecnologia": df["Configuration"].map({"Upright": "Vertical", "Chest": "Horizontal (pozo)", "Side by Side": "Side by side"}),
        "subtipo": df["Designation"], "capacidad": _num(df["Tot Vol"]), "unidad": "litros",
        "kwh_anio_etiqueta": _num(df["Labelled energy consumption (kWh/year)"]), "potencia_w": float("nan"),
        "estrellas": _num(df["Star2009"]), "standby_w": float("nan"),
    })
    out = out[out["capacidad"].between(30, 1200) & out["kwh_anio_etiqueta"].between(50, 2000)]
    out["banda"] = pd.cut(out["capacidad"], [0, 150, 300, 450, 600, 1200],
                          labels=["hasta 150 L", "150–300 L", "300–450 L", "450–600 L", "más de 600 L"])
    return out


def _lavado(corto: str, categoria: str, unidad: str, bins, labels, tecnologia_col=None) -> pd.DataFrame:
    df = _vigentes(_leer(corto))
    out = pd.DataFrame({
        "categoria": categoria, "marca": df["Brand"], "modelo": df["Model No"],
        "tecnologia": df[tecnologia_col] if tecnologia_col else float("nan"),
        "subtipo": df.get("Type"), "capacidad": _num(df["Cap"]), "unidad": unidad,
        "kwh_anio_etiqueta": _num(df["Labelled energy consumption (kWh/year)"]), "potencia_w": float("nan"),
        "estrellas": _num(df["New Star"]), "standby_w": _num(df.get("standbyPowerUsage")),
    })
    out = out[(out["capacidad"] > 0) & (out["kwh_anio_etiqueta"] > 0)]
    out["banda"] = pd.cut(out["capacidad"], bins, labels=labels)
    return out


def televisores() -> pd.DataFrame:
    df = _vigentes(_leer("tv"))
    pulgadas = _num(df["screensize"]) / 2.54  # el registro informa la diagonal en cm
    out = pd.DataFrame({
        "categoria": "tv", "marca": df["Brand_Reg"], "modelo": df["Model_No"], "tecnologia": df["Screen_Tech"],
        "subtipo": float("nan"), "capacidad": pulgadas.round(0), "unidad": "pulgadas",
        "kwh_anio_etiqueta": _num(df["Labelled energy consumption (kWh/year)"]),
        "potencia_w": _num(df["Avg_mode_power"]), "estrellas": _num(df["Star"]), "standby_w": _num(df["Pasv_stnd_power"]),
    })
    out = out[out["capacidad"].between(15, 110) & (out["potencia_w"] > 0)]
    out["banda"] = pd.cut(out["capacidad"], [0, 40, 50, 60, 70, 110],
                          labels=["hasta 40\"", "41–50\"", "51–60\"", "61–70\"", "más de 70\""])
    return out


def clasificar(df: pd.DataFrame) -> pd.DataFrame:
    """indice_rel = consumo / mediana de su banda; clase_rel A–G por séptimos dentro de la categoría."""
    df = df.copy()
    df["banda"] = df["banda"].astype(str)
    if (df["categoria"] == "aire").any():
        base = df["eer"]
        med = df.groupby(["categoria", "banda"])["eer"].transform("median")
        df.loc[df["categoria"] == "aire", "indice_rel"] = (med / base)[df["categoria"] == "aire"]
    no_aire = df["categoria"] != "aire"
    medida = df["kwh_anio_etiqueta"].where(df["categoria"] != "tv", df["potencia_w"])
    med = medida.groupby([df["categoria"], df["banda"]]).transform("median")
    df.loc[no_aire, "indice_rel"] = (medida / med)[no_aire]
    df["clase_rel"] = df.groupby("categoria")["indice_rel"].transform(
        lambda s: pd.qcut(s.rank(method="first"), 7, labels=CLASES).astype(str))
    return df


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sin-descarga", action="store_true", help="usar los CSV que ya están en datos/crudos/")
    args = p.parse_args()
    if not args.sin_descarga:
        descargar()
    partes = [
        aires(), heladeras(),
        _lavado("cw", "lavarropas", "kg", [0, 6, 8, 10, 30], ["hasta 6 kg", "6–8 kg", "8–10 kg", "más de 10 kg"], "Loading"),
        _lavado("cd", "secarropas", "kg", [0, 6, 8, 10, 30], ["hasta 6 kg", "6–8 kg", "8–10 kg", "más de 10 kg"], "Type"),
        _lavado("dw", "lavavajillas", "cubiertos", [0, 9, 13, 30], ["hasta 9", "10–13", "14 o más"]),
        televisores(),
    ]
    df = clasificar(pd.concat(partes, ignore_index=True))
    df["fuente"] = FUENTE
    columnas = ["categoria", "marca", "modelo", "tecnologia", "subtipo", "capacidad", "unidad", "banda",
                "kwh_anio_etiqueta", "potencia_w", "eer", "frigorias", "estrellas", "standby_w",
                "indice_rel", "clase_rel", "fuente"]
    df = df[columnas].dropna(subset=["indice_rel"]).drop_duplicates(subset=["categoria", "marca", "modelo"])
    for c in ["capacidad", "kwh_anio_etiqueta", "potencia_w", "eer", "frigorias", "standby_w", "indice_rel"]:
        df[c] = df[c].round(3)
    df.to_csv(SALIDA, index=False, encoding="utf-8")
    print(f"Listo: {len(df)} modelos → {SALIDA}")
    print(df.groupby("categoria").size().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
