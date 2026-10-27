"""Ambiente isométrico interactivo como componente de Streamlit (Custom Components v2).

El dibujo y el arrastre corren en el navegador (componentes/escena.js). Cuando el usuario
suelta un objeto, lo toca o lo rota, el componente avisa a Python con un "trigger" y Python
actualiza el estado de la sesión.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from simulador import calculo as C
from simulador import estado as E

_DIR = Path(__file__).parent / "componentes"
_JS = (_DIR / "escena.js").read_text(encoding="utf-8") + "\n" + (_DIR / "escena_glue.js").read_text(encoding="utf-8")
_CSS = (_DIR / "escena.css").read_text(encoding="utf-8")

NOMBRE = "simulador_escena"
_HTML = """
<div class="sim-escena"></div>
"""


def _registrar():
    return st.components.v2.component(NOMBRE, html=_HTML, css=_CSS, js=_JS)


_ESCENA = _registrar()


def _montador():
    """Devuelve el componente, registrándolo de nuevo si el servidor lo olvidó (por ejemplo,
    después de una recarga). Así la pantalla no falla con "Component ... is not registered"."""
    global _ESCENA
    try:
        from streamlit.components.v2.get_bidi_component_manager import get_bidi_component_manager

        if get_bidi_component_manager().get(NOMBRE) is None:
            _ESCENA = _registrar()
    except ImportError:
        pass
    return _ESCENA


CLAVE = "escena-ambiente"


def _obj_de(key: str | None):
    if not key:
        return None, None
    tipo, uid = key.split(":", 1)
    s = E.sim()
    if tipo == "i":
        o = next((i for i in s["items"] if i["uid"] == uid), None)
        return o, (E.CAT[o["id"]] if o else None)
    o = next((m for m in s["muebles"] if m["uid"] == uid), None)
    return o, (E.MUEBLES[o["tipo"]] if o else None)


def rotar(key: str | None) -> None:
    o, defn = _obj_de(key)
    if not o:
        return
    if E.es_pared(defn):
        o["rot"] = 3 if o.get("rot", 0) == 0 else 0
    else:
        o["rot"] = (o.get("rot", 0) + 1) % 4
    E.limitar(o, defn)


def _al_mover():
    ev = (st.session_state.get(CLAVE) or {}).get("mover")
    if not ev:
        return
    o, defn = _obj_de(ev.get("key"))
    if o:
        o["x"], o["y"] = float(ev["x"]), float(ev["y"])
        E.limitar(o, defn)
        E.sim()["seleccion"] = ev["key"]


def _al_seleccionar():
    ev = (st.session_state.get(CLAVE) or {}).get("seleccion")
    if ev is not None:
        E.sim()["seleccion"] = ev.get("key")


def _al_rotar():
    ev = (st.session_state.get(CLAVE) or {}).get("rotar")
    if ev:
        rotar(ev.get("key"))


def escena(r: dict) -> None:
    """Dibuja el ambiente actual con los artefactos y muebles que contiene."""
    s = E.sim()
    if s.get("ambiente") not in E.AMB:
        s["ambiente"] = "living"
    amb = E.AMB[s["ambiente"]]
    m = E.mes()
    ef = E.efectivo(r)
    objetos = []
    total_amb = 0.0
    for inst in s["items"]:
        if inst["amb"] != amb["id"]:
            continue
        c = E.CAT[inst["id"]]
        ok = not r["por_uid"][inst["uid"]]["errores"]
        perfil = [v * r["ajuste"] for v in C.horaria(inst, m)] if ok else [0.0] * 24
        kwh = E.kwh_item(r, inst["uid"])
        total_amb += kwh
        objetos.append({
            "key": "i:" + inst["uid"], "tipo": "art", "def": {"iso": c["iso"]},
            "x": inst["x"], "y": inst["y"], "rot": inst.get("rot", 0), "label": inst["nombre"],
            "icono": inst["icono"], "kwh": kwh, "costo": kwh * ef, "perfil": perfil, "color": E.COLOR_CAT[inst["cat"]],
        })
    for mu in s["muebles"]:
        if mu["amb"] != amb["id"]:
            continue
        defn = E.MUEBLES[mu["tipo"]]
        objetos.append({
            "key": "m:" + mu["uid"], "tipo": "mueble", "def": defn,
            "x": mu["x"], "y": mu["y"], "rot": mu["rot"], "label": defn["nombre"],
        })
    _montador()(
        key=CLAVE,
        data={
            "ambiente": amb, "objetos": objetos, "seleccion": s.get("seleccion"),
            "base_kw": s["base_w"] / 1000 * r["ajuste"], "hora": 13.0,
            "resumen": f"{E.fmt(total_amb)} kWh/mes · $ {E.fmt(total_amb * ef)}",
        },
        on_mover_change=_al_mover,
        on_seleccion_change=_al_seleccionar,
        on_rotar_change=_al_rotar,
    )
