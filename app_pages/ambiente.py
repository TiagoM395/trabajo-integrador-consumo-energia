"""Ambiente 3D: escena isométrica con muebles y artefactos arrastrables."""
import streamlit as st

from simulador import escena as ESC
from simulador import estado as E
from simulador import ui
from simulador.estado import fmt

s = E.sim()
r = E.resultados()
ef = E.efectivo(r)


def _cambiar_ambiente():
    valor = st.session_state.get("amb-sel")
    if valor in E.AMB:
        s["ambiente"] = valor
        s["seleccion"] = None


def _mover_a(uid: str):
    inst = E.buscar(uid)
    destino = st.session_state[f"mover-{uid}"]
    if inst and destino != inst["amb"]:
        inst["amb"], inst["rot"] = destino, 0
        E.ubicar(inst)
        s["ambiente"] = destino
        st.session_state["amb-sel"] = destino


def _agregar_mueble(tipo: str):
    defn = E.MUEBLES[tipo]
    x, y = E.lugar_libre(defn, 0, s["ambiente"])
    mu = {"uid": E.nuevo_uid("m"), "tipo": tipo, "amb": s["ambiente"], "x": x, "y": y, "rot": 0}
    s["muebles"].append(mu)
    s["seleccion"] = "m:" + mu["uid"]


def _quitar_mueble(uid: str):
    s["muebles"] = [m for m in s["muebles"] if m["uid"] != uid]
    s["seleccion"] = None


def _reiniciar_ambiente():
    amb = s["ambiente"]
    s["muebles"] = [m for m in s["muebles"] if m["amb"] != amb] + [
        {"uid": E.nuevo_uid("m"), **m} for m in E.D["ESCENA_INICIAL"] if m["amb"] == amb]
    for inst in s["items"]:
        if inst["amb"] == amb:
            inst["rot"], inst["x"], inst["y"] = 0, -99, -99
    for inst in s["items"]:
        if inst["amb"] == amb:
            E.ubicar(inst)
    s["seleccion"] = None


def _seleccionar(key):
    s["seleccion"] = key


if s.get("ambiente") not in E.AMB:
    s["ambiente"] = "living"
if st.session_state.get("amb-sel") not in E.AMB:
    st.session_state["amb-sel"] = s["ambiente"]
st.space("small")
# El texto de cada opción es fijo: si cambiara (por ejemplo, con la cantidad de artefactos),
# Streamlit podría perder la relación entre el texto y el valor.
st.segmented_control(
    "Ambiente", [a["id"] for a in E.D["AMBIENTES"]], key="amb-sel", required=True, label_visibility="collapsed",
    format_func=lambda a: f"{E.AMB[a]['icono']} {E.AMB[a]['nombre']}" if a in E.AMB else str(a),
    on_change=_cambiar_ambiente,
)

izq, der = st.columns([1.75, 1], gap="medium")
with izq:
    with st.container(border=True):
        ESC.escena(r)

with der:
    sel = s.get("seleccion")
    obj = None
    if sel:
        tipo, uid = sel.split(":", 1)
        obj = E.buscar(uid) if tipo == "i" else next((m for m in s["muebles"] if m["uid"] == uid), None)
        if obj is None or (tipo == "i" and obj["amb"] != s["ambiente"]):
            obj = None
    if obj and sel.startswith("i:"):
        with st.container(horizontal=True, vertical_alignment="bottom"):
            st.button("Rotar", icon=":material/rotate_right:", on_click=ESC.rotar, args=(sel,))
            st.selectbox("Mover a", [a["id"] for a in E.D["AMBIENTES"]], key=f"mover-{obj['uid']}",
                         index=[a["id"] for a in E.D["AMBIENTES"]].index(obj["amb"]),
                         format_func=lambda a: E.AMB[a]["nombre"], on_change=_mover_a, args=(obj["uid"],))
            st.button("", icon=":material/close:", on_click=_seleccionar, args=(None,), type="tertiary", help="Cerrar")
        ui.tarjeta(obj, r, ef)
    elif obj:
        defn = E.MUEBLES[obj["tipo"]]
        with st.container(border=True):
            st.markdown(f"### {defn['icono']} {defn['nombre']}")
            st.caption("Mueble decorativo: no consume energía. Sirve para recrear el ambiente.")
            with st.container(horizontal=True):
                st.button("Rotar", icon=":material/rotate_right:", on_click=ESC.rotar, args=(sel,))
                st.button("Quitar", icon=":material/delete:", on_click=_quitar_mueble, args=(obj["uid"],))
                st.button("", icon=":material/close:", on_click=_seleccionar, args=(None,), type="tertiary", help="Cerrar")
    else:
        with st.container(border=True):
            st.markdown("**Artefactos de este ambiente**")
            arts = [i for i in s["items"] if i["amb"] == s["ambiente"]]
            if not arts:
                st.caption("Todavía no hay artefactos acá. Sumá uno desde el catálogo.")
            for i in arts:
                kwh = E.kwh_item(r, i["uid"])
                st.button(f"{i['icono']} {i['nombre']} · {fmt(kwh, 1)} kWh/mes", key=f"sel-{i['uid']}",
                          on_click=_seleccionar, args=("i:" + i["uid"],), type="tertiary")
            st.caption("Tocá un objeto de la escena para editarlo.")

    with st.container(border=True):
        st.markdown("**Sumar al ambiente**")
        if st.button("Electrodoméstico", icon=":material/add:", type="primary", width="stretch"):
            ui.catalogo(s["ambiente"])
        cols = st.columns(3)
        for n, m in enumerate(E.D["MUEBLES"]):
            cols[n % 3].button(f"{m['icono']} {m['nombre']}", key=f"mueble-{m['id']}", width="stretch",
                               on_click=_agregar_mueble, args=(m["id"],))
        st.button("Reiniciar muebles de este ambiente", icon=":material/restart_alt:", on_click=_reiniciar_ambiente,
                  type="tertiary")
