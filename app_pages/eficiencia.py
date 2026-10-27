"""Eficiencia: explorar el dataset real de modelos (clases A–G, inverter) y aplicarlo a tu casa."""
import copy
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from simulador import calculo as C
from simulador import estado as E
from simulador.estado import fmt

RUTA = Path(__file__).parents[1] / "datos" / "electrodomesticos_eficiencia.csv"
URL_FUENTE = "https://data.gov.au/data/dataset/energy-rating-for-household-appliances"
CLASES = list("ABCDEFG")
COLOR_CLASE = {"A": "#15803d", "B": "#22c55e", "C": "#a3e635", "D": "#facc15", "E": "#fb923c", "F": "#f97316", "G": "#dc2626"}
CATS = {
    "aire": ("❄️ Aire acondicionado", "aire"), "heladera": ("🧊 Heladera", "heladera"), "freezer": ("❄️ Freezer", "freezer"),
    "lavarropas": ("🫧 Lavarropas", "lavarropas"), "secarropas": ("🌬️ Secarropas", "secarropas"),
    "lavavajillas": ("🍽️ Lavavajillas", "lavavajillas"), "tv": ("📺 Televisor", "tv"),
}


@st.cache_data
def cargar() -> pd.DataFrame:
    return pd.read_csv(RUTA)


df = cargar()
s = E.sim()
r = E.resultados()

st.space("small")
st.caption(f"**{fmt(len(df))} modelos reales** del registro oficial de etiquetas energéticas de Australia y Nueva Zelanda · "
           f"Fuente: [data.gov.au — Energy Rating for Household Appliances]({URL_FUENTE}) (CC BY 3.0 AU) · "
           "Detalle de columnas y limitaciones en `datos/FUENTES.md`.")

cat = st.segmented_control("Electrodoméstico", list(CATS), format_func=lambda k: CATS[k][0], default="aire",
                           required=True, key="ef-cat", label_visibility="collapsed")
d = df[df["categoria"] == cat]
es_aire, es_tv = cat == "aire", cat == "tv"
medida = "potencia_w" if (es_aire or es_tv) else "kwh_anio_etiqueta"
medida_txt = "Potencia de entrada (W)" if es_aire else "Potencia encendida (W)" if es_tv else "Consumo de etiqueta (kWh/año)"

# ---------- Filtros ----------
f1, f2, f3 = st.columns([1.2, 1.2, 1])
bandas = [b for b in d["banda"].dropna().unique()]
orden_bandas = sorted(bandas, key=lambda b: d.loc[d["banda"] == b, "capacidad"].median())
mas_comun = d["banda"].value_counts().idxmax()
banda = f1.selectbox("Tamaño", ["Todos"] + orden_bandas, index=1 + orden_bandas.index(mas_comun), key=f"ef-banda-{cat}")
tecnos = sorted(d["tecnologia"].dropna().unique())
tec = f2.multiselect("Tecnología", tecnos, default=tecnos, key=f"ef-tec-{cat}") if tecnos else []
marca = f3.text_input("Marca", placeholder="ej. Samsung", key=f"ef-marca-{cat}")
if banda != "Todos":
    d = d[d["banda"] == banda]
if tecnos and tec:
    d = d[d["tecnologia"].isin(tec)]
if marca:
    d = d[d["marca"].astype(str).str.contains(marca, case=False, na=False)]

if d.empty:
    st.info("No hay modelos con esos filtros.", icon=":material/filter_alt_off:")
    st.stop()

# ---------- KPIs ----------
k = st.columns(4)
k[0].metric("Modelos", fmt(len(d)), border=True)
k[1].metric(f"Mediana · {medida_txt}", fmt(d[medida].median()), border=True)
mejor = d.loc[d["indice_rel"].idxmin()]
peor = d.loc[d["indice_rel"].idxmax()]
k[2].metric("Clase A vs. clase G", f"{fmt((1 - d[d.clase_rel == 'A']['indice_rel'].median() / d[d.clase_rel == 'G']['indice_rel'].median()) * 100) if (d.clase_rel == 'A').any() and (d.clase_rel == 'G').any() else '—'} % menos",
            border=True, help="Cuánto menos consume la mediana de clase A respecto de la de clase G.")
if es_aire and d["tecnologia"].nunique() > 1:
    inv = d[d.tecnologia == "Inverter"]["eer"].median()
    fij = d[d.tecnologia == "Velocidad fija"]["eer"].median()
    k[3].metric("Inverter vs. velocidad fija", f"{fmt((1 - fij / inv) * 100)} % menos",
                border=True, help="Diferencia de potencia para el mismo frío, según la mediana de EER (a plena carga).")
else:
    k[3].metric("Más eficiente", f"{mejor['marca']}", delta=f"{fmt(mejor[medida])} {'W' if es_aire or es_tv else 'kWh/año'}",
                delta_color="off", border=True)

# ---------- Gráficos ----------
g1, g2 = st.columns(2, gap="medium")
with g1.container(border=True):
    st.markdown("**Consumo por clase de eficiencia (A = mejor)**")
    fig = px.box(d, x="clase_rel", y=medida, color="clase_rel", category_orders={"clase_rel": CLASES},
                 color_discrete_map=COLOR_CLASE, points=False, labels={"clase_rel": "Clase", medida: medida_txt})
    fig.update_layout(showlegend=False, height=330, margin=dict(l=8, r=8, t=10, b=8),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, config={"displayModeBar": False})
    st.caption("Clase relativa calculada con el dataset (7 grupos iguales). No es la etiqueta IRAM argentina.")
with g2.container(border=True):
    if es_aire:
        st.markdown("**Inverter vs. velocidad fija, por tamaño**")
        res = (df[(df.categoria == "aire") & (df["banda"].isin(orden_bandas if banda == "Todos" else [banda]))]
               .groupby(["banda", "tecnologia"], as_index=False)["potencia_w"].median())
        fig = px.bar(res, x="banda", y="potencia_w", color="tecnologia", barmode="group",
                     category_orders={"banda": orden_bandas},
                     color_discrete_map={"Inverter": "#10b981", "Velocidad fija": "#f97316"},
                     labels={"potencia_w": "Potencia de entrada (W, mediana)", "banda": "", "tecnologia": ""})
    else:
        st.markdown("**Tamaño vs. consumo de cada modelo**")
        fig = px.scatter(d.sample(min(len(d), 2500), random_state=1), x="capacidad", y=medida, color="clase_rel",
                         category_orders={"clase_rel": CLASES}, color_discrete_map=COLOR_CLASE, opacity=0.6,
                         hover_data=["marca", "modelo", "tecnologia"],
                         labels={"capacidad": d["unidad"].iloc[0].capitalize(), medida: medida_txt, "clase_rel": "Clase"})
    fig.update_xaxes(tickangle=0)
    fig.update_layout(height=330, margin=dict(l=8, r=8, t=10, b=8), legend=dict(orientation="h", y=1.08, title=None),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, config={"displayModeBar": False})
    if es_aire:
        st.caption("Potencia a plena carga. A carga parcial la ventaja del inverter es aún mayor.")

# ---------- Aplicar a mi casa ----------
with st.container(border=True):
    st.markdown("#### 🔁 ¿Cuánto ahorrarías cambiando de equipo?")
    mios = [i for i in s["items"] if i["id"] == CATS[cat][1]]
    if not mios:
        st.caption(f"No tenés ningún {CATS[cat][0].split(' ', 1)[1].lower()} cargado en *Mi casa*. Agregalo para comparar.")
    else:
        a, b = st.columns([1, 1.4], vertical_alignment="bottom")
        etiquetas = {i["uid"]: f"{i['icono']} {i['nombre']}" for i in mios}
        if st.session_state.get(f"ef-mio-{cat}") not in etiquetas:
            st.session_state.pop(f"ef-mio-{cat}", None)
        uid_mio = a.selectbox("Tu equipo", list(etiquetas), key=f"ef-mio-{cat}",
                              format_func=lambda u: etiquetas.get(u, str(u)))
        inst = E.buscar(uid_mio) or mios[0]
        clase = b.segmented_control("Reemplazarlo por uno de clase", CLASES, default="A", required=True, key=f"ef-clase-{cat}")
        grupo = d[d["clase_rel"] == clase]
        if banda == "Todos":
            st.warning("Elegí arriba el **tamaño** de tu equipo para comparar contra modelos parecidos.", icon=":material/straighten:")
        if grupo.empty:
            st.caption("No hay modelos de esa clase con los filtros elegidos.")
        else:
            nuevo = copy.deepcopy(inst)
            if cat in ("heladera", "freezer"):
                campo, valor = "kwh_anio", float(grupo["kwh_anio_etiqueta"].median())
            elif es_aire or es_tv:
                campo, valor = "potencia_w", float(grupo["potencia_w"].median())
            else:
                base = E.CAT[inst["id"]].get("kwh_ciclo", inst["kwh_ciclo"])
                campo, valor = "kwh_ciclo", round(base * float(grupo["indice_rel"].median()), 3)
            nuevo[campo] = valor
            antes = sum(x["total"] for x in C.mensual(inst)) * s["ajuste"]
            despues = sum(x["total"] for x in C.mensual(nuevo)) * s["ajuste"]
            precio = r["costos"][E.escenario()]["anual"] / r["anual"] if r["anual"] else 0
            m1, m2, m3 = st.columns(3)
            m1.metric("Hoy", f"{fmt(antes)} kWh/año", border=True)
            m2.metric(f"Con clase {clase}", f"{fmt(despues)} kWh/año", delta=f"{fmt(despues - antes)} kWh",
                      delta_color="inverse", border=True)
            m3.metric("Ahorro estimado", f"$ {fmt((antes - despues) * precio)} / año", border=True,
                      help="Usa el costo efectivo promedio ($/kWh) del año con el escenario tarifario elegido.")
            unidad = {"kwh_anio": "kWh/año", "potencia_w": "W", "kwh_ciclo": "kWh por ciclo"}[campo]
            st.caption(f"Se toma la mediana de {fmt(len(grupo))} modelos de clase {clase}"
                       f"{' · ' + banda if banda != 'Todos' else ''}: **{fmt(valor, 2 if campo == 'kwh_ciclo' else 0)} {unidad}**.")

            def _aplicar(u=inst["uid"], c=campo, v=valor, cl=clase):
                obj = E.buscar(u)
                obj[c] = v
                st.session_state.pop(f"{u}-{c}", None)
                st.toast(f"{obj['icono']} {obj['nombre']}: ahora con un equipo de clase {cl}", icon=":material/eco:")

            st.button(f"Usar clase {clase} en mi casa", icon=":material/eco:", type="primary", on_click=_aplicar)

# ---------- Tabla ----------
with st.expander(f"Ver los {fmt(len(d))} modelos", icon=":material/table_view:"):
    cols = ["clase_rel", "marca", "modelo", "tecnologia", "capacidad", "unidad", medida, "estrellas", "standby_w"]
    if es_aire:
        cols.insert(7, "eer")
    st.dataframe(
        d.sort_values("indice_rel")[cols], hide_index=True,
        column_config={
            "clase_rel": st.column_config.TextColumn("Clase", width=60),
            medida: st.column_config.NumberColumn(medida_txt, format="%.0f"),
            "eer": st.column_config.NumberColumn("EER", format="%.2f"),
            "estrellas": st.column_config.NumberColumn("Estrellas (AU)", format="%.1f ⭐"),
            "standby_w": st.column_config.NumberColumn("Standby (W)", format="%.2f"),
        },
    )
