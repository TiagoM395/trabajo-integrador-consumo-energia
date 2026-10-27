"""Estado de la sesión: artefactos cargados, muebles, tarifas y selección.

Cada artefacto es un dict ("instancia") con los campos que usa simulador/calculo.py.
Los widgets de cada tarjeta usan claves "<uid>-<campo>"; sincronizar() copia sus valores a
las instancias al principio de cada ejecución, así todos los números están al día.
"""
from __future__ import annotations

import copy
import datetime as dt
import uuid

import streamlit as st

from simulador import calculo as C

D = C.datos()
CAT = {c["id"]: c for c in D["CATALOGO"]}
MUEBLES = {m["id"]: m for m in D["MUEBLES"]}
AMB = {a["id"]: a for a in D["AMBIENTES"]}
CATEGORIAS = {c["id"]: c for c in D["CATEGORIAS"]}
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
MESES_LARGO = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
               "septiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
MODO_TXT = {"horas": "Por horas", "ciclos": "Por ciclos", "anual": "Etiqueta anual", "siempre": "Siempre encendido"}
COLOR_CAT = {
    "cocina": "#10b981", "clima": "#3b82f6", "agua": "#06b6d4", "lavado": "#6366f1",
    "ocio": "#f43f5e", "oficina": "#a855f7", "luz": "#eab308", "otros": "#64748b",
}
COLOR = {"act": "#10b981", "pas": "#f97316", "base": "#94a3b8"}
ANCHO, FONDO = 12, 10  # ambiente en baldosas de 0,5 m


def nuevo_uid(p: str) -> str:
    return p + uuid.uuid4().hex[:8]


def sim() -> dict:
    return st.session_state.sim


def iniciar() -> None:
    if "sim" in st.session_state:
        return
    st.session_state.sim = {
        "items": [], "base_w": 0, "tarifas": copy.deepcopy(C.tarifas_edea()),
        "muebles": [{"uid": nuevo_uid("m"), **m} for m in D["ESCENA_INICIAL"]],
        "ambiente": "living", "meta": 12.0, "ajuste": 1.0, "perfil": "vacio", "seleccion": None,
        "factura": {"kwh": 0, "dias": 30, "mes": dt.date.today().month - 1},
    }
    st.session_state.setdefault("escenario", "sin_subsidio")
    st.session_state.setdefault("mes", dt.date.today().month - 1)
    cargar_perfil("vacio")  # arranca vacía: solo cuenta lo que elige el usuario


# ---------- Ubicación en el ambiente ----------

def _forma(defn: dict) -> dict:
    return defn.get("iso", defn)


def huella(defn: dict, rot: int) -> tuple[float, float]:
    s = _forma(defn)
    return (s["d"], s["w"]) if rot % 2 else (s["w"], s["d"])


def es_pared(defn: dict) -> bool:
    return _forma(defn).get("montaje") == "pared"


def objetos_en(amb: str, excluir: str | None = None) -> list[tuple[float, float, float, float]]:
    s = sim()
    out = []
    for i in s["items"]:
        if i["amb"] == amb and i["uid"] != excluir and i.get("x", -99) >= 0:
            out.append((i["x"], i["y"], *huella(CAT[i["id"]], i.get("rot", 0))))
    for m in s["muebles"]:
        if m["amb"] == amb and m["uid"] != excluir:
            out.append((m["x"], m["y"], *huella(MUEBLES[m["tipo"]], m["rot"])))
    return out


def lugar_libre(defn: dict, rot: int, amb: str, excluir: str | None = None) -> tuple[float, float]:
    w, d = huella(defn, rot)
    ocupados = objetos_en(amb, excluir)
    pared = es_pared(defn)

    def choca(x, y):
        return any(x < ox + ow and x + w > ox and y < oy + od and y + d > oy for ox, oy, ow, od in ocupados)

    y = 0.0
    while y <= FONDO - d:
        x = 0.0
        while x <= ANCHO - w:
            if not choca(x, y):
                return x, y
            x += 0.5
        if pared:
            break
        y += 0.5
    return max(0.0, (ANCHO - w) / 2), 0.0 if pared else max(0.0, (FONDO - d) / 2)


def ubicar(inst: dict) -> None:
    inst["x"], inst["y"] = lugar_libre(CAT[inst["id"]], inst.get("rot", 0), inst["amb"], inst["uid"])


def limitar(obj: dict, defn: dict) -> None:
    """Mantiene el objeto dentro del ambiente (y pegado a la pared si va colgado)."""
    w, d = huella(defn, obj.get("rot", 0))
    obj["x"] = min(max(0.0, obj["x"]), ANCHO - w)
    obj["y"] = min(max(0.0, obj["y"]), FONDO - d)
    if es_pared(defn):
        if obj.get("rot", 0) == 3:
            obj["x"] = 0.0
        else:
            obj["y"] = 0.0


# ---------- Artefactos ----------

def nueva_inst(id_cat: str, cambios: dict | None = None, amb: str | None = None) -> dict:
    c = CAT[id_cat]
    inst = {
        "uid": nuevo_uid("a"), "id": id_cat, "nombre": c["nombre"], "icono": c["icono"], "cat": c["cat"],
        "modo": c["modo"], "potencia_w": c.get("potencia_w", 0), "standby_w": c.get("standby_w", 0),
        "kwh_anio": c.get("kwh_anio", 0), "kwh_ciclo": c.get("kwh_ciclo", 0), "ciclo_h": c.get("ciclo_h", 1),
        "estacion": "todo", "cantidad": 1, "conectado": 24, "uso": 1, "dias": 7, "ciclos": 0, "inicio": 0,
    }
    inst.update(copy.deepcopy(c.get("def", {})))
    inst.update(cambios or {})
    inst["factores"] = list(D["ESTACIONES"].get(inst["estacion"], D["ESTACIONES"]["todo"]))
    inst["dias_sel"] = DIAS[: int(inst["dias"])]
    inst["amb"] = amb or inst.get("amb") or c["amb"]
    inst["rot"] = 0
    inst["x"] = inst["y"] = -99
    ubicar(inst)
    return inst


def cargar_perfil(pid: str) -> None:
    p = D["PERFILES"][pid]
    s = sim()
    s["perfil"] = pid
    s["base_w"] = p["base_w"]
    st.session_state["base_w"] = p["base_w"]
    s["items"] = []
    for id_cat, cambios in p["items"]:
        s["items"].append(nueva_inst(id_cat, cambios))
    s["seleccion"] = None


def agregar(id_cat: str, amb: str | None = None) -> dict:
    inst = nueva_inst(id_cat, amb=amb)
    sim()["items"].append(inst)
    sim()["perfil"] = "custom"
    return inst


def quitar(uid: str) -> None:
    s = sim()
    s["items"] = [i for i in s["items"] if i["uid"] != uid]
    if s.get("seleccion") == "i:" + uid:
        s["seleccion"] = None


def duplicar(uid: str) -> None:
    s = sim()
    i = next(k for k, x in enumerate(s["items"]) if x["uid"] == uid)
    copia = copy.deepcopy(s["items"][i])
    copia["uid"] = nuevo_uid("a")
    ubicar(copia)
    s["items"].insert(i + 1, copia)


def buscar(uid: str) -> dict | None:
    return next((i for i in sim()["items"] if i["uid"] == uid), None)


# ---------- Sincronización widgets → instancias ----------

def _horas(inst, v):
    inst["uso"], inst["conectado"] = float(v[0]), float(v[1])


def _dias(inst, v):
    v = [d for d in DIAS if d in (v or [])] or inst.get("dias_sel") or DIAS
    inst["dias_sel"], inst["dias"] = v, len(v)


def _estacion(inst, v):
    if v:
        if v == "custom" and inst["estacion"] != "custom":
            inst["factores"] = list(C.factores(inst))
        inst["estacion"] = v


def _inicio(inst, v):
    h, m = v.split(":")
    inst["inicio"] = int(h) + int(m) / 60


def _nombre(inst, v):
    inst["nombre"] = v.strip() or CAT[inst["id"]]["nombre"]


CAMPOS = {
    "horas": _horas, "dias": _dias, "estacion": _estacion, "inicio": _inicio, "nombre": _nombre,
    "uso": lambda i, v: i.__setitem__("uso", float(v)),
    "ciclos": lambda i, v: i.__setitem__("ciclos", int(v)),
    "conectado": lambda i, v: i.__setitem__("conectado", float(v)),
    "kwh_anio": lambda i, v: i.__setitem__("kwh_anio", float(v)),
    "potencia_w": lambda i, v: i.__setitem__("potencia_w", float(v)),
    "standby_w": lambda i, v: i.__setitem__("standby_w", float(v)),
    "kwh_ciclo": lambda i, v: i.__setitem__("kwh_ciclo", float(v)),
    "cantidad": lambda i, v: i.__setitem__("cantidad", int(v)),
}


def sincronizar() -> None:
    """Copia los valores de los widgets a cada artefacto (antes de calcular)."""
    ss = st.session_state
    s = sim()
    for inst in s["items"]:
        u = inst["uid"]
        for campo, fn in CAMPOS.items():
            k = f"{u}-{campo}"
            if k in ss and ss[k] is not None:
                fn(inst, ss[k])
        if inst["modo"] == "horas" and inst["uso"] > inst["conectado"]:
            inst["conectado"] = inst["uso"]  # no puede usarse más horas de las que está enchufado
        # Sin época del año: cada artefacto gasta lo que dicen las horas que eligió el usuario.
        inst["estacion"] = "todo"
        inst["factores"] = [1.0] * 12
    # Sesiones abiertas antes del cambio a las tarifas reales de EDEA: se actualizan.
    if any("tramos" not in e for e in s["tarifas"]["escenarios"].values()):
        s["tarifas"] = copy.deepcopy(C.tarifas_edea())
    if ss.get("escenario") not in s["tarifas"]["escenarios"]:
        ss["escenario"] = "sin_subsidio"
    if "base_w" in ss:
        s["base_w"] = ss["base_w"]


def hhmm(h: float) -> str:
    t = round((h % 24) * 60)
    return f"{(t // 60) % 24:02d}:{t % 60:02d}"


# Horarios elegibles: cada 30 minutos (14:00, 14:30, 15:00…).
HORARIOS = [hhmm(q / 2) for q in range(48)]


def hhmm30(h: float) -> str:
    """Hora redondeada a la media hora más cercana, como figura en HORARIOS."""
    return hhmm(round((h % 24) * 2) / 2)


# ---------- Resultados ----------

def resultados() -> dict:
    """Simula con el estado actual y agrega accesos rápidos por uid."""
    s = sim()
    r = C.simular({"items": s["items"], "base_w": s["base_w"], "tarifas": s["tarifas"], "ajuste": s["ajuste"]})
    r["por_uid"] = {it["uid"]: it for it in r["items"]}
    return r


def escenario() -> str:
    return st.session_state.get("escenario") or "sin_subsidio"


# El simulador calcula UN mes con lo que elige el usuario. Se usa un mes de 30 días
# (abril en la tabla de días) como "mes tipo"; no depende de la fecha ni de la época.
MES_TIPO = 3


def mes() -> int:
    return MES_TIPO


def kwh_item(r: dict, uid: str, m: int | None = None) -> float:
    it = r["por_uid"].get(uid)
    return it["meses"][mes() if m is None else m]["total"] * r["ajuste"] if it else 0.0


def efectivo(r: dict, m: int | None = None) -> float:
    return r["costos"][escenario()]["porMes"][mes() if m is None else m]["efectivo"]


def precio_kwh(r: dict | None = None, esc: str | None = None) -> dict:
    """Precio fijo por kWh de Mi casa según el subsidio (ver calculo.precio_kwh).

    No depende del consumo de la casa: cada card es independiente de las demás.
    """
    return C.precio_kwh(sim()["tarifas"], esc or escenario())


def costo(r: dict, esc: str | None = None) -> dict:
    """Lo que gasta la casa por mes en Mi casa: cargo fijo + kWh × precio fijo (suma de las cards)."""
    return C.costo_casa(r["meses"][mes()]["total"], sim()["tarifas"], esc or escenario())


def fmt(v: float, dec: int = 0) -> str:
    """Número con formato argentino: 1.234,5"""
    s = f"{v:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")
