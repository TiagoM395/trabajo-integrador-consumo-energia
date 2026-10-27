"""Tarifas: factura de EDEA con el cuadro tarifario oficial, según la situación de cada hogar."""
import pandas as pd
import streamlit as st

from simulador import calculo as C
from simulador import estado as E
from simulador import graficos as G
from simulador.estado import fmt

s = E.sim()
T = s["tarifas"]
r = E.resultados()
kwh = r["meses"][E.mes()]["total"]
vig = "/".join(reversed(T["vigencia_desde"].split("-")))

st.space("small")
st.info(
    f"**Cuadro tarifario oficial de EDEA** para consumos desde el **{vig}**, aprobado por la "
    f"{T['resolucion']} y publicado por el OCEBA ([ver cuadros tarifarios]({T['url_indice']})). "
    "Incluye cargo fijo, precio por kWh, Cargo Transición Tarifaria e impuestos. "
    "Los datos y sus links están en `datos/tarifas_edea.csv` y `datos/FUENTES.md`.",
    icon=":material/verified:",
)

if kwh <= 0:
    st.caption("Agregá electrodomésticos en **Mi casa** para ver cuánto pagarías.")
    st.stop()

st.markdown(f"#### Tu factura con {fmt(kwh)} kWh por mes, según tu situación")


def _elegir(esc_id: str):
    st.session_state.escenario = esc_id


sin = C.factura(kwh, T, "sin_subsidio")
cols = st.columns(len(T["escenarios"]))
for col, (esc_id, e) in zip(cols, T["escenarios"].items()):
    f = C.factura(kwh, T, esc_id)
    elegido = esc_id == E.escenario()
    color = G.ESC_COLOR.get(esc_id, "#64748b")
    with col.container(border=True, height="stretch"):
        st.markdown(f"**{e['icono']} {e['nombre']}**" + (" :green-badge[Tu situación]" if elegido else ""))
        st.html(f"<div class='esc-total' style='color:{color}'>$ {fmt(f['total'])}"
                f"<small style='font-size:.85rem;opacity:.6'> / mes</small></div>")
        if esc_id != "sin_subsidio":
            ahorro = sin["total"] - f["total"]
            pct = ahorro / sin["total"] * 100 if sin["total"] else 0
            st.markdown(f":green-badge[Ahorrás \\$ {fmt(ahorro)} ({fmt(pct)} %)]")
        conceptos = [
            (f"Cargo fijo (tramo {f['tramo']})", f["cargo_fijo"]),
            ("Energía", f["energia"]),
            ("Cargo Transición Tarifaria", f["ctt"]),
            ("Bonificación tarifa social", -f["bonificacion"]),
            ("Impuestos", f["impuestos"]),
        ]
        filas_html = "".join(
            f"<tr><td>{n}</td><td style='text-align:right;white-space:nowrap'>{'−' if v < 0 else ''}$ {fmt(abs(v))}</td></tr>"
            for n, v in conceptos if v)
        st.html(f"<table style='width:100%;font-size:.85rem;border-collapse:collapse'>{filas_html}"
                f"<tr style='font-weight:800;border-top:1px solid rgba(127,127,127,.4)'><td>Total</td>"
                f"<td style='text-align:right;white-space:nowrap'>$ {fmt(f['total'])}</td></tr></table>")
        if f.get("tope"):
            st.caption(f"Primeros {fmt(f['tope'])} kWh a precio bonificado"
                       + (f"; los otros {fmt(f['fuera'])} kWh, a precio pleno." if f["fuera"] > 0 else "."))
        else:
            st.caption(e["desc"])
        st.button("Elegida" if elegido else "Es mi situación", key=f"usar-{esc_id}", width="stretch",
                  type="primary" if elegido else "secondary", disabled=elegido, on_click=_elegir, args=(esc_id,))

c1, c2 = st.columns([1.3, 1], gap="medium")
with c1.container(border=True):
    st.markdown("**Cuánto pagás según cuánto consumís**")
    st.plotly_chart(G.costo_consumo(T, kwh, E.escenario(), C.factura), config={"displayModeBar": False})
    st.caption("Los saltos son los cambios de tramo: al pasar de 100, 200, 400… kWh cambian el cargo fijo y el "
               "precio de todos los kWh del mes.")
with c2.container(border=True):
    e = T["escenarios"][E.escenario()]
    st.markdown(f"**Cuadro de tu situación: {e['nombre'].lower()}**")
    con_bloque = any(x["bloque_kwh"] for x in e["tramos"])
    con_bonif = any(x["bonificacion_fija"] for x in e["tramos"])
    filas = []
    for t in e["tramos"]:
        hasta = f"{fmt(t['hasta'])} kWh" if t["hasta"] else "más"
        fila = {"Tramo": t["tramo"], "Consumo del mes": f"{fmt(t['desde'])} a {hasta}",
                "Cargo fijo ($/mes)": t["cargo_fijo"], "Precio ($/kWh)": t["cargo_variable"]}
        if con_bloque:
            fila["Primeros kWh ($/kWh)"] = t["cargo_variable_bloque"] or None
        if con_bonif:
            fila["Bonificación ($/mes)"] = t["bonificacion_fija"] or None
        filas.append(fila)
    st.dataframe(pd.DataFrame(filas), hide_index=True, column_config={
        "Cargo fijo ($/mes)": st.column_config.NumberColumn(format="%,.2f"),
        "Precio ($/kWh)": st.column_config.NumberColumn(format="%,.4f"),
        "Primeros kWh ($/kWh)": st.column_config.NumberColumn(format="%,.4f"),
        "Bonificación ($/mes)": st.column_config.NumberColumn(format="%,.0f"),
    })
    st.caption(f"Más Cargo Transición Tarifaria por kWh e impuestos del {fmt(e['impuestos_pct'], 3)} %. "
               f"Anexo {e['anexo']} · [ver PDF oficial]({e['fuente_url']})")
