"""Guarda lo que elige cada persona para que no se pierda al recargar la página.

Cada casa tiene un código corto que va en la dirección de la página (?casa=a3f9c21b). Al final de
cada ejecución se guarda la casa en sesiones/<código>.json; si la página se recarga, la sesión de
Streamlit arranca vacía, lee el código de la dirección y recupera la casa.

Se guarda solo lo elegido en la app (electrodomésticos, cantidades, horas, consumo de base,
subsidio, factura cargada a mano o escaneada, ajuste y muebles del Ambiente 3D). Ningún dato
personal: la factura escaneada ya llega sin nombre, dirección ni NIS.
"""
from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path

import streamlit as st

CARPETA = Path(__file__).resolve().parents[1] / "sesiones"
DIAS_VIGENCIA = 30  # las casas sin usar por más de 30 días se borran
CLAVE_URL = "casa"
# Partes de la casa que se guardan (las tarifas no: se leen siempre del cuadro oficial vigente).
CAMPOS_SIM = ("items", "base_w", "perfil", "ajuste", "factura", "meta", "muebles", "ambiente", "seleccion")
_CODIGO_OK = re.compile(r"^[0-9a-f]{8,32}$")


def _archivo(codigo: str) -> Path:
    return CARPETA / f"{codigo}.json"


def _codigo() -> str:
    """Código de esta casa: el de la sesión, el de la dirección o uno nuevo."""
    ss = st.session_state
    if "casa-codigo" not in ss:
        de_url = st.query_params.get(CLAVE_URL, "")
        ss["casa-codigo"] = de_url if _CODIGO_OK.match(de_url or "") else uuid.uuid4().hex[:12]
    return ss["casa-codigo"]


def restaurar() -> None:
    """Al abrir o recargar la página: si la dirección trae el código de una casa guardada, la recupera.

    Se llama una sola vez por sesión, justo después de estado.iniciar().
    """
    ss = st.session_state
    codigo = _codigo()
    if ss.get("casa-restaurada"):
        return
    ss["casa-restaurada"] = True
    _limpiar_viejas()
    arch = _archivo(codigo)
    if not arch.exists():
        return
    try:
        datos = json.loads(arch.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    sim = ss.sim
    for campo in CAMPOS_SIM:
        if campo in datos.get("sim", {}):
            sim[campo] = datos["sim"][campo]
    if datos.get("escenario") in sim["tarifas"]["escenarios"]:
        ss["escenario"] = datos["escenario"]
    ss["base_w"] = sim["base_w"]


def guardar() -> None:
    """Al final de cada ejecución: guarda la casa y deja el código en la dirección de la página."""
    ss = st.session_state
    if "sim" not in ss:
        return
    codigo = _codigo()
    # El código vuelve a la dirección en cada ejecución (al cambiar de pestaña Streamlit la limpia).
    if st.query_params.get(CLAVE_URL) != codigo:
        st.query_params[CLAVE_URL] = codigo
    datos = {
        "sim": {c: ss.sim.get(c) for c in CAMPOS_SIM},
        "escenario": ss.get("escenario"),
    }
    try:
        CARPETA.mkdir(exist_ok=True)
        tmp = _archivo(codigo).with_suffix(".tmp")
        tmp.write_text(json.dumps(datos, ensure_ascii=False, default=str), encoding="utf-8")
        tmp.replace(_archivo(codigo))
    except OSError:
        pass  # si no se puede escribir (disco de solo lectura), la app sigue funcionando igual


def _limpiar_viejas() -> None:
    """Borra las casas que nadie abrió en los últimos DIAS_VIGENCIA días."""
    limite = time.time() - DIAS_VIGENCIA * 86400
    try:
        for f in CARPETA.glob("*.json"):
            if f.stat().st_mtime < limite:
                f.unlink(missing_ok=True)
    except OSError:
        pass
