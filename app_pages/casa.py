"""Mi casa en 4 pasos: tu situación, armá tu casa, lo que gastás por mes y la predicción de mañana."""
import pandas as pd
import streamlit as st

from simulador import estado as E
from simulador import graficos as G
from simulador import ui
from simulador import vista_prediccion
from simulador.estado import MESES, MESES_LARGO, fmt

s = E.sim()
r = E.resultados()
m = E.mes()
# Precio de cada kWh de un equipo (tramo + impuestos, sin cargo fijo): las cards son independientes.
pk = E.precio_kwh(r)
ef = pk["precio"]
ss = st.session_state

# ---------- Tu situación: subsidio, consumo de base y reinicio ----------
# Los widgets usan claves propias ("w-…") y copian su valor a "escenario" y "base_w".
# Así la elección sigue vigente en las otras pestañas, donde estos controles no se dibujan.
escs = s["tarifas"]["escenarios"]
ss["w-escenario"] = E.escenario()
ss["w-base"] = s["base_w"]


def _set_escenario():
    if ss.get("w-escenario"):
        ss["escenario"] = ss["w-escenario"]


def _set_base():
    s["base_w"] = ss["base_w"] = ss["w-base"]


def _reiniciar():
    for k in list(ss.keys()):
        del ss[k]
    # Casa nueva con código nuevo: así no se recupera la casa guardada con el código anterior.
    import uuid
    ss["casa-codigo"] = uuid.uuid4().hex[:12]
    ss["casa-restaurada"] = True


st.markdown("### 1 · Tu situación")
with st.container(border=True):
    c1, c2, c3 = st.columns([1.7, 1, 0.5], gap="medium", vertical_alignment="bottom")
    c1.segmented_control(
        "¿Tenés algún subsidio en la luz?", list(escs), key="w-escenario", required=True,
        on_change=_set_escenario, width="stretch",
        format_func=lambda k: f"{escs[k]['icono']} {escs[k]['corto']}",
        help="Figura en tu factura de EDEA. El subsidio cambia el precio, no los kWh que consumís.",
    )
    c2.slider("Consumo de base de la casa (W)", 0, 60, key="w-base", on_change=_set_base,
              help="Lo que queda prendido con todo 'apagado': relojes, luces de standby y equipos que no cargaste.")
    c3.button("Reiniciar todo", icon=":material/restart_alt:", on_click=_reiniciar, type="tertiary")
    st.caption(f"{escs[E.escenario()]['desc']} Cálculo con el cuadro tarifario oficial de EDEA (OCEBA) y los "
               "consumos que cargás: no reemplaza la factura.")

# ---------- Perfiles ----------
# Solo se muestran mientras la casa está vacía (o si el usuario pide cambiar de perfil).
# Una vez elegido un perfil, desaparecen y queda una línea para cambiarlo.


def _usar_perfil(pid: str):
    E.cargar_perfil(pid)
    st.session_state["ver-perfiles"] = False
    p = E.D["PERFILES"][pid]
    st.toast(f"{p['icono']} Perfil \"{p['nombre']}\" cargado")


def _ver_perfiles(valor: bool):
    st.session_state["ver-perfiles"] = valor


st.space("small")
st.markdown("### 2 · Armá tu casa")
st.caption("Elegí tus electrodomésticos y cuánto los usás. Con eso se calcula lo que gastás por mes (paso 3) y se predice si mañana te pasás de la meta (paso 4).")
st.space("small")
if not s["items"] or st.session_state.get("ver-perfiles"):
    if s["items"]:
        with st.container(horizontal=True, vertical_alignment="center"):
            st.caption("Elegir otro perfil **reemplaza** los electrodomésticos que tenés cargados.")
            st.button("Cancelar", icon=":material/close:", type="tertiary", on_click=_ver_perfiles, args=(False,))
    else:
        st.markdown("**Elegí un perfil para empezar rápido**, o agregá tus electrodomésticos uno por uno.")
    perfiles = {k: v for k, v in E.D["PERFILES"].items() if k != "vacio"}
    cols = st.columns(len(perfiles))
    for col, (pid, p) in zip(cols, perfiles.items()):
        with col.container(border=True, height="stretch"):
            st.html(f"<div class='perfil-ico'>{p['icono']}</div><b>{p['nombre']}</b>")
            st.caption(f"{p['desc']} ({len(p['items'])} electrodomésticos)")
            st.button("Usar", key=f"perfil-{pid}", width="stretch", on_click=_usar_perfil, args=(pid,))
else:
    p = E.D["PERFILES"].get(s["perfil"])
    # Perfil en su propio recuadro, con los botones a la derecha
    with st.container(border=True, horizontal=True, vertical_alignment="center", gap="small"):
        if p and s["perfil"] != "vacio":
            st.markdown(f"{p['icono']} Partiste del perfil **{p['nombre']}**. Cambiá, quitá o agregá lo que quieras abajo.",
                        width="content")
        else:
            st.markdown("🏠 Tu casa, armada a tu manera.", width="content")
        st.space("stretch")
        st.button("Cambiar de perfil", icon=":material/swap_horiz:", type="tertiary", on_click=_ver_perfiles, args=(True,))
        st.button("Vaciar la casa", icon=":material/delete_sweep:", type="tertiary", on_click=_usar_perfil, args=("vacio",))

st.space("medium")

izq, der = st.columns([1.05, 1], gap="large")

# ---------- Lista de electrodomésticos ----------
with izq:
    st.markdown(f"#### Tus electrodomésticos · {len(s['items'])}")
    with st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="distribute"):
        orden = st.segmented_control("Orden", ["Carga", "Más consumo"], default="Carga", key="orden",
                                     label_visibility="collapsed", required=True)
        if st.button("Agregar", icon=":material/add:", type="primary"):
            ui.catalogo()

    items = list(s["items"])
    if orden == "Más consumo":
        items.sort(key=lambda i: -E.kwh_item(r, i["uid"]))
    if not items:
        with st.container(border=True, horizontal_alignment="center"):
            st.markdown("### 🔌")
            st.write("Tu casa está vacía. Agregá el primer electrodoméstico o elegí un perfil.")
    # Grilla de tarjetas cuadradas que ocupa todo el ancho de la columna (estilos en ui.ESTILOS).
    ui.colores_grilla(items)
    with st.container(key="grilla"):
        for inst in items:
            ui.tarjeta_grilla(inst, r, ef, pk)
    if items and st.button("Agregar electrodoméstico", icon=":material/add:", width="stretch", key="agregar-abajo"):
        ui.catalogo()

# ---------- Resumen ----------
with der:
    st.markdown("### 3 · Lo que gastás por mes")
    mm = r["meses"][m]
    esc = s["tarifas"]["escenarios"][E.escenario()]
    fac = r["costos"][E.escenario()]["porMes"][m]  # factura real de EDEA, con tramos (referencia)
    cc = E.costo(r)  # suma de las cards + consumo de base + cargo fijo
    with st.container(border=True):
        c1, c2 = st.columns(2, vertical_alignment="center")
        c1.metric("💲 Tu casa gasta por mes", f"$ {fmt(cc['total'])}", border=False)
        c2.metric("⚡ Energía por mes", f"{fmt(mm['total'], 1)} kWh", border=False)
        st.caption(f"Suma de tus electrodomésticos y del consumo de base: {fmt(mm['total'], 1)} kWh × "
                   f"\\$ {fmt(cc['precio'], 2)} = \\$ {fmt(cc['energia'])}, más el cargo fijo "
                   f"\\$ {fmt(cc['cargo_fijo'])} ({esc['corto']}, con impuestos).  \n"
                   f"Factura de EDEA con sus tramos: **\\$ {fmt(fac['total'])}** (tramo {fac.get('tramo', '—')}).")

    with st.container(border=True):
        c1, c2 = st.columns([0.45, 0.55], vertical_alignment="center")
        c1.plotly_chart(G.dona(mm["act"], mm["pas"], mm["base"], "un mes"), config={"displayModeBar": False})
        tot = mm["total"] or 1
        for k, nombre, v, desc in (("act", "Activo", mm["act"], "mientras lo usás"),
                                   ("pas", "Standby", mm["pas"], "enchufado sin usar"),
                                   ("base", "Base", mm["base"], "siempre prendido")):
            c2.html(f"<div style='margin:6px 0'><i class='dot' style='background:{E.COLOR[k]}'></i><b>{nombre}</b> · "
                    f"{fmt(v, 1)} kWh · {fmt(v / tot * 100)} %<br><small style='opacity:.6;margin-left:14px'>{desc}</small></div>")

    with st.container(border=True):
        st.markdown("**Qué te consume más**")
        filas = [{"": it_inst["icono"], "Artefacto": it_inst["nombre"], "kWh/mes": E.kwh_item(r, it_inst["uid"]),
                  "% del total": E.kwh_item(r, it_inst["uid"]) / tot * 100, "$ / mes": E.kwh_item(r, it_inst["uid"]) * ef}
                 for it_inst in s["items"]]
        filas.sort(key=lambda f: -f["kWh/mes"])
        if filas:
            st.dataframe(
                pd.DataFrame(filas[:8]), hide_index=True,
                column_config={
                    "": st.column_config.TextColumn(width=40),
                    "kWh/mes": st.column_config.NumberColumn(format="%.1f"),
                    "% del total": st.column_config.ProgressColumn(format="%.0f %%", min_value=0, max_value=100),
                    "$ / mes": st.column_config.NumberColumn(format="$ %,.0f"),
                },
            )
        else:
            st.caption("Agregá artefactos para ver el ranking.")

    with st.container(border=True):
        st.markdown("**👻 Consumo fantasma** · lo que gastás aunque no estés usando nada")
        fant = [(i["icono"], i["nombre"], r["por_uid"][i["uid"]]["meses"][m]["pas"] * r["ajuste"]) for i in s["items"]]
        fant.append(("🏠", "Base de la casa", mm["base"]))
        fant = sorted([f for f in fant if f[2] > 0.05], key=lambda f: -f[2])[:5]
        if fant:
            fmax = fant[0][2]
            for ico, nombre, v in fant:
                c1, c2 = st.columns([0.62, 0.38], vertical_alignment="center")
                c1.progress(v / fmax, text=f"{ico} {nombre}")
                c2.markdown(f"**{fmt(v, 1)} kWh** · \\$ {fmt(v * ef)}")
        else:
            st.caption("¡Nada! No tenés consumo fantasma cargado.")

    with st.container(border=True):
        st.markdown("**💡 Ideas para ahorrar**")
        for ico, texto in ui.consejos(r):
            with st.container(horizontal=True, vertical_alignment="top"):
                st.markdown(f"### {ico}", width="content")
                st.markdown(texto)

# ---------- Paso 4: predicción ----------
st.space("medium")
vista_prediccion.seccion()
