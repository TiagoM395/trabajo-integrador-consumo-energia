"""Mi día: curva de carga de 24 h y agenda de uso de cada artefacto."""
import pandas as pd
import streamlit as st

from simulador import calculo as C
from simulador import estado as E
from simulador import graficos as G
from simulador.estado import MESES_LARGO, fmt, hhmm

s = E.sim()
m = E.mes()

st.space("small")
kpis = st.container()
graficos = st.container()

# ---------- Horarios editables (se procesan antes de dibujar los gráficos) ----------
editables = [i for i in s["items"] if i["modo"] in ("horas", "ciclos")]
with st.container(border=True):
    st.markdown("**Cambiá los horarios** y mirá cómo se mueve el pico")
    df = pd.DataFrame([{
        "uid": i["uid"], "Artefacto": f"{i['icono']} {i['nombre']}", "Empieza": hhmm(i["inicio"]),
        "Horas de uso": float(i["uso"]) if i["modo"] == "horas" else float(i["ciclo_h"]),
        "Conectado (h)": float(i["conectado"]), "modo": i["modo"],
    } for i in editables])
    if len(df):
        nuevo = st.data_editor(
            df, hide_index=True, key="agenda-editor", column_order=["Artefacto", "Empieza", "Horas de uso", "Conectado (h)"],
            disabled=["Artefacto"],
            column_config={
                "Empieza": st.column_config.SelectboxColumn(options=E.HORARIOS, required=True),
                "Horas de uso": st.column_config.NumberColumn(min_value=0.0, max_value=24.0, step=0.25, format="%.2f h",
                                                              help="En lavarropas y similares es la duración del ciclo."),
                "Conectado (h)": st.column_config.NumberColumn(min_value=0.0, max_value=24.0, step=0.25, format="%.2f h"),
            },
        )
        for _, fila in nuevo.iterrows():
            inst = E.buscar(fila["uid"])
            if not inst:
                continue
            hh, mm_ = fila["Empieza"].split(":")
            inst["inicio"] = int(hh) + int(mm_) / 60
            inst["conectado"] = float(fila["Conectado (h)"])
            if inst["modo"] == "horas":
                inst["uso"] = min(float(fila["Horas de uso"]), 24.0)
                inst["conectado"] = max(inst["conectado"], inst["uso"])
            else:
                inst["ciclo_h"] = max(0.1, float(fila["Horas de uso"]))
            for campo in ("uso", "inicio", "conectado"):  # que las tarjetas tomen el valor nuevo
                st.session_state.pop(f"{inst['uid']}-{campo}", None)
    else:
        st.caption("No hay artefactos con horario (por horas o por ciclos).")
    st.caption("La heladera y los equipos siempre encendidos consumen todo el día, por eso no aparecen acá.")

# ---------- Gráficos ----------
r = E.resultados()
curva = C.curva_dia(s["items"], s["base_w"], m, r["ajuste"])
pico = max(curva["total"])
h_pico = curva["total"].index(pico)
valle = min(curva["total"])
h_valle = curva["total"].index(valle)

with graficos:
    hora = st.slider("Hora del día", 0.0, 23.75, value=20.5, step=0.25, key="hora-dia", format="%.2f h")
    h = min(23, int(hora))
    c1, c2 = st.columns([1.6, 1], gap="medium")
    with c1.container(border=True):
        st.markdown(f"**Curva de carga de un día de {MESES_LARGO[m]}**")
        st.plotly_chart(G.curva(curva, s["items"], hora), config={"displayModeBar": False})
        st.caption("Potencia media de un día típico del mes. La tarifa residencial no cambia por horario: la curva "
                   "sirve para entender el pico y conecta con el modelo de ML, que trabaja con mediciones horarias.")
    with c2.container(border=True):
        st.markdown(f"**Qué consume a las {hhmm(hora)}**")
        ahora = sorted(((i, ser["valores"][h] * 1000) for i, ser in zip(s["items"], curva["series"])), key=lambda p: -p[1])
        ahora = [(i, w) for i, w in ahora if w > 0.5]
        if curva["base"][0] > 0:
            ahora.append(({"icono": "🏠", "nombre": "Base de la casa"}, curva["base"][0] * 1000))
        wmax = max((w for _, w in ahora), default=1)
        for i, w in ahora[:10]:
            a, b = st.columns([0.7, 0.3], vertical_alignment="center")
            a.progress(min(1.0, w / wmax), text=f"{i['icono']} {i['nombre']}")
            b.markdown(f"**{fmt(w)} W**")
        if not ahora:
            st.caption("Nada consume a esta hora.")
    with st.container(border=True):
        st.markdown("**Agenda del día**")
        st.plotly_chart(G.agenda(s["items"], C.ventanas, hora), config={"displayModeBar": False})

with kpis:
    c = st.columns(4)
    c[0].metric("Pico del día", f"{fmt(pico * 1000)} W", border=True, help=f"{hhmm(h_pico)}–{hhmm(h_pico + 1)}")
    c[1].metric("Energía del día", f"{fmt(sum(curva['total']), 1)} kWh", border=True,
                help=f"Día típico de {MESES_LARGO[m]}")
    c[2].metric("Hora más tranquila", f"{fmt(valle * 1000)} W", border=True, help=f"{hhmm(h_valle)}–{hhmm(h_valle + 1)}")
    hora_sel = st.session_state.get("hora-dia", 20.5)
    hs = min(23, int(hora_sel))
    c[3].metric(f"A las {hhmm(hora_sel)}", f"{fmt(curva['total'][hs] * 1000)} W", border=True,
                delta=f"{fmt(curva['total'][hs] / pico * 100 if pico else 0)} % del pico", delta_color="off",
                chart_data=[v * 1000 for v in curva["total"]], chart_type="area")
