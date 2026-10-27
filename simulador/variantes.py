"""Variantes de cada electrodoméstico: el nombre de la tarjeta es un desplegable con las más comunes.

Elegir una variante carga su valor estándar (potencia, consumo por ciclo o consumo anual).

Fuentes (ver datos/FUENTES.md):
- "dataset": mediana de los modelos reales de datos/electrodomesticos_eficiencia.csv (registro de
  etiquetas de Australia y Nueva Zelanda, data.gov.au), agrupados por tamaño.
- "típico": valor típico de la tabla de consumo estándar de la propuesta (sección 7) o del rango
  habitual del equipo. Es un supuesto.
"""
from __future__ import annotations

# id del catálogo: lista de (nombre, cambios, texto del valor estándar). La primera marcada con
# "por_defecto" es la que trae el catálogo.
VARIANTES: dict[str, list[dict]] = {
    "heladera": [
        {"nombre": "Heladera chica", "cambios": {"kwh_anio": 240},
         "estandar": "240 kWh por año: mediana de 442 heladeras con freezer reales de hasta 300 L"},
        {"nombre": "Heladera mediana", "cambios": {"kwh_anio": 320},
         "estandar": "320 kWh por año: mediana de 688 heladeras con freezer reales de 300 a 450 L"},
        {"nombre": "Heladera grande", "cambios": {"kwh_anio": 410},
         "estandar": "410 kWh por año: mediana de 866 heladeras con freezer reales de más de 450 L"},
    ],
    "freezer": [
        {"nombre": "Freezer chico", "cambios": {"kwh_anio": 200},
         "estandar": "200 kWh por año: mediana de 305 freezers reales de hasta 200 L"},
        {"nombre": "Freezer mediano", "cambios": {"kwh_anio": 260},
         "estandar": "260 kWh por año: mediana de 230 freezers reales de 200 a 350 L"},
        {"nombre": "Freezer grande", "cambios": {"kwh_anio": 370},
         "estandar": "370 kWh por año: mediana de 212 freezers reales de más de 350 L"},
    ],
    "aire": [
        {"nombre": "Aire 2.250 frigorías", "cambios": {"potencia_w": 550},
         "estandar": "550 W: mediana de 352 aires split reales de unas 2.250 frigorías"},
        {"nombre": "Aire 3.000 frigorías", "cambios": {"potencia_w": 870},
         "estandar": "870 W: mediana de 335 aires split reales de unas 3.000 frigorías"},
        {"nombre": "Aire 4.500 frigorías", "cambios": {"potencia_w": 1400},
         "estandar": "1.400 W: mediana de 622 aires split reales de unas 4.500 frigorías"},
        {"nombre": "Aire 6.000 frigorías", "cambios": {"potencia_w": 1970},
         "estandar": "1.970 W: mediana de 769 aires split reales de unas 6.000 frigorías"},
    ],
    "tv": [
        {"nombre": 'TV 32"', "cambios": {"potencia_w": 31, "standby_w": 0.4},
         "estandar": "31 W: mediana de 294 televisores reales de 32 pulgadas"},
        {"nombre": 'TV 43"', "cambios": {"potencia_w": 63, "standby_w": 0.4},
         "estandar": "63 W: mediana de 406 televisores reales de 43 pulgadas"},
        {"nombre": 'TV 50"', "cambios": {"potencia_w": 75, "standby_w": 0.4},
         "estandar": "75 W: mediana de 429 televisores reales de 50 pulgadas"},
        {"nombre": 'TV 55"', "cambios": {"potencia_w": 92, "standby_w": 0.4},
         "estandar": "92 W: mediana de 778 televisores reales de 55 pulgadas"},
        {"nombre": 'TV 65"', "cambios": {"potencia_w": 119, "standby_w": 0.4},
         "estandar": "119 W: mediana de 867 televisores reales de 65 pulgadas"},
    ],
    "termotanque": [
        {"nombre": "Termotanque 50 L", "cambios": {"potencia_w": 1500}, "estandar": "1.500 W (valor típico)"},
        {"nombre": "Termotanque 80 L", "cambios": {"potencia_w": 2000}, "estandar": "2.000 W (valor típico)"},
        {"nombre": "Termotanque 120 L", "cambios": {"potencia_w": 2500}, "estandar": "2.500 W (valor típico)"},
    ],
    "lavarropas": [
        {"nombre": "Lavarropas 6 kg", "cambios": {"kwh_ciclo": 0.7}, "estandar": "0,7 kWh por lavado (valor típico)"},
        {"nombre": "Lavarropas 8 kg", "cambios": {"kwh_ciclo": 0.9}, "estandar": "0,9 kWh por lavado (valor típico)"},
        {"nombre": "Lavarropas 10 kg", "cambios": {"kwh_ciclo": 1.1}, "estandar": "1,1 kWh por lavado (valor típico)"},
    ],
    "secarropas": [
        {"nombre": "Secarropas centrífugo", "cambios": {"potencia_w": 300, "kwh_ciclo": 0.05, "ciclo_h": 0.2},
         "estandar": "0,05 kWh por uso: 300 W durante unos 10 minutos (valor típico)"},
        {"nombre": "Secarropas por calor", "cambios": {"potencia_w": 2200, "kwh_ciclo": 2.5, "ciclo_h": 1.2},
         "estandar": "2,5 kWh por secado (valor típico)"},
    ],
    "lavavajillas": [
        {"nombre": "Lavavajillas 6 cubiertos", "cambios": {"kwh_ciclo": 0.8},
         "estandar": "0,8 kWh por lavado (valor típico)"},
        {"nombre": "Lavavajillas 12 cubiertos", "cambios": {"kwh_ciclo": 1.3},
         "estandar": "1,3 kWh por lavado (valor típico)"},
    ],
    "microondas": [
        {"nombre": "Microondas 20 L", "cambios": {"potencia_w": 800}, "estandar": "800 W (valor típico)"},
        {"nombre": "Microondas 25 L", "cambios": {"potencia_w": 1000}, "estandar": "1.000 W (valor típico)"},
        {"nombre": "Microondas 30 L", "cambios": {"potencia_w": 1200}, "estandar": "1.200 W (valor típico)"},
    ],
    "horno": [
        {"nombre": "Horno eléctrico de mesa", "cambios": {"potencia_w": 1500}, "estandar": "1.500 W (valor típico)"},
        {"nombre": "Horno eléctrico grande", "cambios": {"potencia_w": 2400}, "estandar": "2.400 W (valor típico)"},
    ],
    "calefactor": [
        {"nombre": "Calefactor eléctrico 1.000 W", "cambios": {"potencia_w": 1000}, "estandar": "1.000 W"},
        {"nombre": "Calefactor eléctrico 1.500 W", "cambios": {"potencia_w": 1500}, "estandar": "1.500 W"},
        {"nombre": "Calefactor eléctrico 2.000 W", "cambios": {"potencia_w": 2000}, "estandar": "2.000 W"},
    ],
    "ventilador": [
        {"nombre": "Ventilador de pie", "cambios": {"potencia_w": 60}, "estandar": "60 W (valor típico)"},
        {"nombre": "Ventilador de techo", "cambios": {"potencia_w": 75}, "estandar": "75 W (valor típico)"},
        {"nombre": "Turbo ventilador", "cambios": {"potencia_w": 100}, "estandar": "100 W (valor típico)"},
    ],
    "notebook": [
        {"nombre": "Notebook", "cambios": {"potencia_w": 65}, "estandar": "65 W (valor típico)"},
        {"nombre": "Notebook gamer", "cambios": {"potencia_w": 150}, "estandar": "150 W (valor típico)"},
    ],
    "pc": [
        {"nombre": "PC de escritorio + monitor", "cambios": {"potencia_w": 250}, "estandar": "250 W (valor típico)"},
        {"nombre": "PC gamer + monitor", "cambios": {"potencia_w": 450}, "estandar": "450 W (valor típico)"},
    ],
    "led": [
        {"nombre": "Lámpara LED 7 W", "cambios": {"potencia_w": 7}, "estandar": "7 W"},
        {"nombre": "Lámpara LED 9 W", "cambios": {"potencia_w": 9}, "estandar": "9 W"},
        {"nombre": "Lámpara LED 12 W", "cambios": {"potencia_w": 12}, "estandar": "12 W"},
    ],
    "halogena": [
        {"nombre": "Lámpara halógena 35 W", "cambios": {"potencia_w": 35}, "estandar": "35 W"},
        {"nombre": "Lámpara halógena 50 W", "cambios": {"potencia_w": 50}, "estandar": "50 W"},
    ],
    "bomba": [
        {"nombre": "Bomba de agua ½ HP", "cambios": {"potencia_w": 370}, "estandar": "370 W (½ HP)"},
        {"nombre": "Bomba de agua ¾ HP", "cambios": {"potencia_w": 550}, "estandar": "550 W (¾ HP)"},
        {"nombre": "Bomba de agua 1 HP", "cambios": {"potencia_w": 750}, "estandar": "750 W (1 HP)"},
    ],
}

# Variante que trae el catálogo al agregar el electrodoméstico.
POR_DEFECTO = {
    "heladera": "Heladera mediana", "freezer": "Freezer mediano", "aire": "Aire 3.000 frigorías",
    "tv": 'TV 50"', "termotanque": "Termotanque 50 L", "lavarropas": "Lavarropas 8 kg",
    "secarropas": "Secarropas por calor", "lavavajillas": "Lavavajillas 12 cubiertos",
    "microondas": "Microondas 25 L", "horno": "Horno eléctrico grande",
    "calefactor": "Calefactor eléctrico 2.000 W", "ventilador": "Ventilador de pie", "notebook": "Notebook",
    "pc": "PC de escritorio + monitor", "led": "Lámpara LED 9 W", "halogena": "Lámpara halógena 50 W",
    "bomba": "Bomba de agua 1 HP",
}


def actual(inst: dict) -> dict | None:
    """La variante cuyos valores coinciden con los del electrodoméstico (o None si fue cambiado)."""
    for v in VARIANTES.get(inst["id"], []):
        if all(abs(float(inst.get(k, 0)) - float(x)) < 1e-9 for k, x in v["cambios"].items()):
            return v
    return None


def aplicar(inst: dict, nombre: str) -> None:
    v = next((x for x in VARIANTES.get(inst["id"], []) if x["nombre"] == nombre), None)
    if v:
        inst.update({k: float(x) for k, x in v["cambios"].items()})
        inst["nombre"] = v["nombre"]
