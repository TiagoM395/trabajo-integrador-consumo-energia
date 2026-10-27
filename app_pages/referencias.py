"""Referencias: calibración con la factura, conexión con el modelo de ML, tabla estándar y fórmulas."""
import pandas as pd
import streamlit as st

from simulador import estado as E
from simulador import factura as FAC
from simulador import graficos as G
from simulador import ui
from simulador.estado import DIAS, MESES_LARGO, MODO_TXT, fmt

s = E.sim()
r = E.resultados()

st.space("small")

# ---------- Escaneo de la factura ----------
CONF = {"alta": ":green-badge[confianza alta]", "media": ":orange-badge[confianza media]",
        "baja": ":orange-badge[confianza baja — revisalo]", "dudosa": ":red-badge[dudoso]",
        "no encontrado": ":red-badge[no encontrado]"}

with st.container(border=True):
    st.markdown("#### 📷 Escanear tu factura")
    st.caption("Subí el PDF o una foto de la factura de EDEA. Se procesa en memoria, no se guarda, y solo se usan "
               "los números (kWh, período, importe): nombre, dirección y NIS se descartan.")
    n = st.session_state.setdefault("factura-n", 0)
    t_archivo, t_camara = st.tabs([":material/upload_file: Subir PDF o foto", ":material/photo_camera: Sacar foto"])
    with t_archivo:
        archivo = st.file_uploader("Factura (PDF, JPG, PNG o WebP · hasta 10 MB)", type=["pdf", "jpg", "jpeg", "png", "webp"],
                                   key=f"factura-archivo-{n}")
    with t_camara:
        foto = st.camera_input("Encuadrá la parte de la factura con el consumo y el total", key=f"factura-foto-{n}")
    fuente = archivo or foto
    if fuente is not None and st.button("Leer factura", icon=":material/document_scanner:", type="primary"):
        with st.spinner("Leyendo la factura…"):
            try:
                texto, metodo = FAC.leer(fuente.getvalue(), getattr(fuente, "name", "foto.jpg"))
                st.session_state["factura-detectada"] = {**FAC.extraer(texto), "metodo": metodo}
            except ValueError as e:
                st.session_state.pop("factura-detectada", None)
                st.error(str(e), icon=":material/error:")
            except Exception:
                st.session_state.pop("factura-detectada", None)
                st.error("No pudimos leer el archivo. Probá con otra foto (bien iluminada y derecha) o cargá los datos a mano.",
                         icon=":material/error:")

    det = st.session_state.get("factura-detectada")
    if det:
        st.markdown(f"**Esto encontramos** ({det['metodo']}). Revisalo y corregilo antes de usarlo:")
        for aviso in det["avisos"]:
            st.warning(aviso, icon=":material/info:")
        with st.form("factura-confirmar", border=False):
            a, b, c = st.columns(3)
            with a:
                kwh_ok = st.number_input("Consumo del período (kWh)", 0, 2000, value=int(round(det["kwh"] or 0)))
                st.markdown(CONF[det["kwh_conf"]])
            with b:
                dias_ok = st.number_input("Días del período", 25, 65, value=int(det["dias"] or 30))
                st.markdown(CONF[det["periodo_conf"]] + (f" {det['desde']:%d/%m/%Y} → {det['hasta']:%d/%m/%Y}" if det["desde"] else ""))
            with c:
                imp_ok = st.number_input("Importe total ($)", 0.0, value=float(det["importe"] or 0), step=100.0)
                st.markdown(CONF[det["importe_conf"]] + (f" · vence {det['vencimiento']:%d/%m/%Y}" if det["vencimiento"] else ""))
            mes_det = FAC.mes_del_periodo(det["desde"], det["hasta"])
            mes_ok = st.selectbox("Mes del período", range(12), index=mes_det if mes_det is not None else s["factura"]["mes"],
                                  format_func=lambda i: MESES_LARGO[i])
            if st.form_submit_button("Usar estos datos", icon=":material/check:", type="primary"):
                s["factura"].update({"kwh": kwh_ok, "dias": dias_ok, "mes": mes_ok, "importe": imp_ok})
                st.session_state.pop("factura-detectada", None)
                st.session_state["factura-n"] = n + 1  # vacía el archivo subido: la imagen no queda en la sesión
                st.toast("Datos de la factura cargados", icon=":material/check_circle:")
                st.rerun()

izq, der = st.columns(2, gap="medium")

# ---------- Calibración con la factura ----------
with izq.container(border=True, height="stretch"):
    st.markdown("#### 🧾 Calibrar con tu factura")
    st.caption("Escaneala arriba o copiá el consumo del período a mano. No se piden datos personales.")
    fac = s["factura"]
    a, b, c = st.columns(3)
    fac["kwh"] = a.number_input("Consumo del período (kWh)", 0, 2000, value=int(fac["kwh"]), step=1)
    fac["dias"] = b.number_input("Días del período", 25, 65, value=int(fac["dias"]), step=1)
    fac["mes"] = c.selectbox("Mes del período", range(12), index=int(fac["mes"]), format_func=lambda i: MESES_LARGO[i])
    simulado = r["meses"][fac["mes"]]["total"] / r["ajuste"] / E.C.DIAS_MES[fac["mes"]] * fac["dias"]
    if fac["kwh"] > 0 and simulado > 0:
        factor = fac["kwh"] / simulado
        m1, m2, m3 = st.columns(3)
        m1.metric("Factura", f"{fmt(fac['kwh'])} kWh")
        m2.metric(f"Simulado ({fac['dias']} días)", f"{fmt(simulado)} kWh")
        m3.metric("Factor", f"× {fmt(factor, 2)}", delta=f"{fmt((factor - 1) * 100, 0)} %", delta_color="off")
        if abs(factor - 1) > 0.15:
            st.warning(f"Tu factura es {fmt(factor, 2)}× la simulación. Revisá en este orden: **horas de uso**, "
                       "**potencias** y **cantidad de artefactos**.", icon=":material/tune:")
        else:
            st.success("La simulación está cerca de tu factura (±15 %). ¡Bien cargado!", icon=":material/check_circle:")

        def _ajustar(f=factor):
            s["ajuste"] = f

        def _quitar():
            s["ajuste"] = 1.0

        with st.container(horizontal=True):
            st.button(f"Ajustar la simulación × {fmt(factor, 2)}", icon=":material/auto_fix_high:", type="primary", on_click=_ajustar)
            if abs(s["ajuste"] - 1) > 1e-6:
                st.button("Quitar ajuste", on_click=_quitar)
        st.caption("El ajuste escala todos los resultados; no modifica el catálogo.")
        if fac.get("importe"):
            from simulador import calculo as Ccalc
            kwh_mes = fac["kwh"] / fac["dias"] * Ccalc.DIAS_MES[fac["mes"]]
            est = Ccalc.factura(kwh_mes, s["tarifas"], E.escenario())["total"] * fac["dias"] / Ccalc.DIAS_MES[fac["mes"]]
            st.caption(f"Control de importe: la factura dice **\\$ {fmt(fac['importe'])}**; con las tarifas cargadas y "
                       f"{fmt(fac['kwh'])} kWh el simulador estima **\\$ {fmt(est)}**. Si difieren mucho, actualizá las tarifas.")
    else:
        st.caption("Completá el consumo del período para comparar.")

# ---------- Conexión con el modelo de ML ----------
with der.container(border=True, height="stretch"):
    st.markdown("#### 🤖 Conexión con el modelo de ML")
    st.caption("El simulador es una **estimación determinista** con tus supuestos: no es una predicción de aprendizaje "
               "automático. La alerta del TP la dan el **clasificador directo** y la **regresión + umbral**.")
    s["meta"] = st.slider("Meta diaria (mismo umbral del clasificador), kWh/día", 2.0, 40.0, value=float(s["meta"]), step=0.5)
    st.plotly_chart(G.meta_diaria(r, s["meta"]), config={"displayModeBar": False})
    sobre = sum(1 for x in r["meses"] if x["total"] / x["dias"] > s["meta"])
    st.markdown(f"**{sobre} de 12 meses** superan la meta en promedio. Los días reales varían alrededor del "
                "promedio: por eso el clasificador puede alertar aunque el promedio esté debajo.")

# ---------- Tabla estándar ----------
with st.container(border=True):
    st.markdown("#### 📋 Tabla de consumo estándar")
    filas = []
    for c in E.D["CATALOGO"]:
        d = c["def"]
        uso = (f"{fmt(c['kwh_anio'])} kWh/año" if c["modo"] == "anual" else f"{d.get('ciclos')} ciclos/semana"
               if c["modo"] == "ciclos" else "24 h" if c["modo"] == "siempre" else f"{fmt(d.get('uso', 0), 2)} h/día")
        filas.append({
            "": c["icono"], "Artefacto": c["nombre"], "Modo": MODO_TXT[c["modo"]],
            "Potencia (W)": None if c["modo"] == "anual" else c["potencia_w"], "Standby (W)": c.get("standby_w") or None,
            "Uso típico": uso, "Típico (kWh/mes)": ui.tipico(c["id"]), "Referencia": c["rango"],
        })
    st.dataframe(pd.DataFrame(filas), hide_index=True, column_config={
        "": st.column_config.TextColumn(width=40),
        "Típico (kWh/mes)": st.column_config.NumberColumn(format="%.1f", help="Promedio anual con los valores por defecto"),
        "Potencia (W)": st.column_config.NumberColumn(format="%.0f"),
    })
    a, b = st.columns([0.7, 0.3], vertical_alignment="bottom")
    elegido = a.selectbox("Agregar a mi casa", [c["id"] for c in E.D["CATALOGO"]],
                          format_func=lambda i: f"{E.CAT[i]['icono']} {E.CAT[i]['nombre']}")
    if b.button("Agregar", icon=":material/add:", width="stretch"):
        inst = E.agregar(elegido)
        st.toast(f"{inst['icono']} {inst['nombre']} agregado", icon=":material/check_circle:")
        st.rerun()
    st.caption("Valores de arranque, no universales: verificalos con la etiqueta, el manual o un wattímetro.")

# ---------- Fórmulas ----------
with st.container(border=True):
    st.markdown("#### 📐 Cómo calcula")
    c1, c2 = st.columns(2)
    c1.markdown("**Por horas**")
    c1.latex(r"E_{activo} = \frac{P}{1000}\cdot h_{uso}\cdot\frac{d}{7} \qquad E_{standby} = \frac{P_{sb}}{1000}\cdot(h_{conectado}-h_{uso})\cdot\frac{d}{7}")
    c1.markdown("**Por ciclos**")
    c1.latex(r"E_{activo} = kWh_{ciclo}\cdot\frac{ciclos}{7}")
    c2.markdown("**Etiqueta anual (heladera)**")
    c2.latex(r"kWh_{mes} = kWh_{año}\cdot\frac{f_m\cdot d_m}{\sum_k f_k\cdot d_k}")
    c2.markdown("**Mes y factura**")
    c2.latex(r"kWh_{mes} = E_{activo}\cdot f_m\cdot d_m + E_{standby}\cdot d_m + base")
    c2.latex(r"\$ = \sum_{bloques} kWh\cdot precio + cargo\ fijo + impuestos")
    st.caption(f"Días de la semana: {', '.join(DIAS)}. Costo por artefacto = kWh del artefacto × costo efectivo ($/kWh) del mes.")
