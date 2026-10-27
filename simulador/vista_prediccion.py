"""Paso 4 de Mi casa: «¿Mañana te pasás de la meta?» con los modelos entrenados.

Usa la regresión y el clasificador del trabajo (simulador/prediccion.py). Los datos de entrada
salen de la casa armada en los pasos anteriores o de la factura escaneada.
"""
import datetime as dt
from zoneinfo import ZoneInfo

import streamlit as st

from simulador import calculo as C
from simulador import estado as E
from simulador import prediccion as P
from simulador.estado import fmt

NOMBRE_FUENTE = {"casa": "🏠 Mi casa", "factura": "🧾 Mi factura"}


@st.cache_resource
def _modelos():
    return P.cargar()


def _explicacion() -> None:
    with st.container(border=True):
        p1, p2, p3 = st.columns(3, gap="medium")
        with p1:
            st.markdown("**① Tu consumo de hoy**")
            st.caption("Los kWh por día de la casa que armaste arriba, o los de tu factura (kWh ÷ días).")
        with p2:
            st.markdown("**② Dos modelos**")
            st.caption("**Regresión:** estima cuántos kWh vas a usar en las próximas 24 horas.  \n"
                       "**Clasificación:** responde directamente si te pasás de la meta, sí o no.")
        with p3:
            st.markdown("**③ El resultado**")
            st.caption("Las dos respuestas se comparan con la **meta diaria de 25,9 kWh**.  \n"
                       "🟢 no te pasás · 🟡 estás cerca o no coinciden · 🔴 te pasás")


def seccion() -> None:
    s = E.sim()
    r = E.resultados()
    m = E.mes()
    mm = r["meses"][m]
    fac = s["factura"]
    hay_casa = bool(s["items"]) and mm["total"] > 0
    hay_factura = fac.get("kwh", 0) > 0

    st.markdown("### 4 · ¿Mañana te pasás de la meta?")
    st.caption("Los pasos anteriores hacen la **cuenta** de lo que gastás. Este paso **predice**: dos modelos de "
               "aprendizaje automático, entrenados con 4 años de mediciones de un hogar real, estiman lo que vas a "
               "gastar **mañana**.")
    _explicacion()

    if not hay_casa and not hay_factura:
        with st.container(border=True, horizontal_alignment="center"):
            st.markdown("### 🔮")
            st.write("Agregá electrodomésticos en el paso 2, o escaneá tu factura, y acá aparece la predicción.")
            st.page_link("app_pages/factura.py", label="Escanear mi factura", icon=":material/receipt_long:")
        return

    # ---------- Datos de entrada ----------
    ahora = dt.datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
    opciones = [k for k, ok in (("casa", hay_casa), ("factura", hay_factura)) if ok]
    fuente = opciones[0]
    if len(opciones) > 1:
        fuente = st.segmented_control("¿Con qué consumo predecimos?", opciones, default=opciones[0], required=True,
                                      key="pred-fuente", format_func=NOMBRE_FUENTE.get)
    with st.expander("Día y clima de la predicción", icon=":material/tune:"):
        a, b, c, d = st.columns(4, vertical_alignment="bottom")
        fecha = a.date_input("Día de la consulta", value=ahora.date(), format="DD/MM/YYYY", key="pred-fecha")
        hora_txt = b.select_slider("Hora", E.HORARIOS, value=E.hhmm30(ahora.hour + ahora.minute / 60),
                                   key="pred-hora")
        hora = int(hora_txt.split(":")[0])  # el modelo usa la hora entera
        temp_hoy = c.number_input("Temperatura de hoy (°C)", -10.0, 45.0, value=20.0, step=1.0, key="pred-temp-hoy")
        temp_man = d.number_input("Temperatura de mañana (°C)", -10.0, 45.0, value=20.0, step=1.0,
                                  key="pred-temp-man")
        feriado = st.checkbox("Mañana es feriado", key="pred-feriado")

    # ---------- Consumo de las últimas 24 h ----------
    curva = C.curva_dia(s["items"], s["base_w"], m, r["ajuste"])["total"]
    casa_dia = mm["total"] / C.DIAS_MES[m]
    kwh_item = {i["uid"]: E.kwh_item(r, i["uid"]) / C.DIAS_MES[m] for i in s["items"]}
    subs = P.submedidores(s["items"], kwh_item)
    kwh_hora = curva[hora]
    if fuente == "factura":
        kwh_dia = fac["kwh"] / fac["dias"]
        k = kwh_dia / casa_dia if hay_casa else 0.0
        subs = {n: v * k for n, v in subs.items()}
        kwh_hora = kwh_hora * k if hay_casa else kwh_dia / 24
    else:
        kwh_dia = casa_dia

    fila, ajustes = P.armar_entrada(kwh_dia=kwh_dia, kwh_hora=kwh_hora, subs=subs, fecha=fecha, hora=hora,
                                    temp_hoy=temp_hoy, temp_manana=temp_man, feriado=feriado)
    reg, clf = _modelos()
    res = P.predecir(reg, clf, fila)
    st.session_state["pred-ultima"] = {"fila": fila, "ajustes": ajustes, "res": res}

    # ---------- Resultado ----------
    if res["alerta_reg"] and res["alerta_clf"]:
        color, icono, titulo = "#e11d48", "🔴", "Mañana te pasás de la meta"
    elif res["zona_gris"] or not res["coinciden"]:
        color, icono, titulo = "#ea580c", "🟡", "Mañana estás cerca de tu límite"
    else:
        color, icono, titulo = "#059669", "🟢", "Mañana no te pasás de la meta"

    st.html(f"""
    <div class="hero pred" style="margin-top:4px;border:2px solid {color};box-shadow:0 0 0 4px {color}33,0 18px 40px -20px rgba(15,23,42,.6)">
      <div class="hero-top"><div class="hero-marca">
        <div class="hero-logo" style="background:{color}2e;border:2px solid {color};box-shadow:0 0 0 6px {color}22">{icono}</div>
        <div><h1>{titulo}</h1>
        <p>Hoy tu casa usa <b>{fmt(kwh_dia, 1)} kWh</b> por día
           ({'según lo que armaste' if fuente == 'casa' else 'según tu factura'}).
           En las próximas 24 horas vas a usar unos <b>{fmt(res['kwh'], 1)} kWh</b> (± {fmt(res['mae'], 1)} kWh).
           La meta diaria es <b>{fmt(res['meta'], 1)} kWh</b>.</p></div></div></div>
    </div>""")

    izq, der = st.columns(2, gap="medium")
    with izq.container(border=True, height="stretch"):
        st.markdown("**Las dos respuestas**")
        a, b = st.columns(2)
        a.metric("Regresión + meta", "Te pasás" if res["alerta_reg"] else "No te pasás",
                 delta=f"{'+' if res['diferencia'] >= 0 else ''}{fmt(res['diferencia'], 1)} kWh vs. meta",
                 delta_color="inverse")
        b.metric("Clasificación", "Te pasás" if res["alerta_clf"] else "No te pasás")
        if res["coinciden"]:
            st.success("Los dos modelos coinciden.", icon=":material/check_circle:")
        else:
            st.warning("Los dos modelos **no se ponen de acuerdo**: estás justo en el límite, mañana podés "
                       "pasarte o no.", icon=":material/compare_arrows:")
        if res["zona_gris"]:
            st.info(f"Zona gris: la estimación está a menos de {fmt(res['mae'], 1)} kWh de la meta, que es el error "
                    "promedio del modelo.", icon=":material/blur_on:")
        st.caption(f"Regresión: {res['reg_nombre']} · Clasificación: {res['clf_nombre']}")

    with der.container(border=True, height="stretch"):
        st.markdown("**Qué significa**")
        if sum(subs.values()) > 0:
            mayor = max(subs, key=subs.get)
            st.markdown(f"- **{P.NOMBRE_SUB[mayor]}** es el {fmt(subs[mayor] / kwh_dia * 100)} % de tu consumo "
                        "diario: ahí está el mayor margen para ahorrar.")
        mes_kwh = max(res["kwh"], 0) * C.DIAS_MES[m]
        costo = C.factura(mes_kwh, s["tarifas"], E.escenario())["total"]
        st.markdown(f"- Si todos los días fueran como mañana, serían **{fmt(mes_kwh)} kWh por mes**: unos "
                    f"**\\$ {fmt(costo)}** con tu tarifa de EDEA.")
        st.markdown("- Cómo se entrenaron y evaluaron los modelos está en la pestaña **Análisis**.")

    with st.expander("Limitaciones", icon=":material/warning:"):
        st.markdown(
            "- Los modelos aprendieron con **un solo hogar** (Sceaux, Francia, 2006–2010). En otra casa la "
            "predicción es menos precisa.\n"
            "- La meta de 25,9 kWh por día es el consumo típico de ese hogar, más alto que el de muchos hogares "
            "de acá.\n"
            "- Algunos datos que el modelo necesita no los mide nadie en la casa (voltaje, energía reactiva, "
            "consumo de la semana anterior) y se completan con valores típicos.\n"
            "- Es una estimación: no reemplaza la medición del medidor ni la factura.")
