"""Factura: escaneo de la factura de EDEA y calibración de la simulación."""
import streamlit as st

from simulador import estado as E
from simulador import factura as FAC
from simulador.estado import MESES_LARGO, fmt

s = E.sim()
r = E.resultados()

st.space("small")

# ---------- Escaneo de la factura ----------
CONF = {"alta": ":green-badge[confianza alta]", "media": ":orange-badge[confianza media]",
        "baja": ":orange-badge[confianza baja — revisalo]", "dudosa": ":red-badge[dudoso]",
        "no encontrado": ":red-badge[no encontrado]"}

with st.container(border=True):
    st.markdown("#### 📷 Escanear tu factura")
    st.caption("Subí el PDF o una foto de la factura de EDEA, o sacala con la cámara. Se leen el texto y el código QR: "
               "consumo, período, importe, vencimiento y subsidio. Se procesa en memoria y no se guarda; nombre, "
               "dirección y NIS se descartan.")
    st.caption("📱 En el celular, el botón para subir el archivo también ofrece la cámara del teléfono, que saca la foto "
               "con más calidad. Factura sobre una mesa, con buena luz, derecha y sin sombras.")
    n = st.session_state.setdefault("factura-n", 0)
    archivo = st.file_uploader("Factura (PDF, JPG, PNG o WebP · hasta 10 MB)", type=["pdf", "jpg", "jpeg", "png", "webp"],
                               key=f"factura-archivo-{n}")

    # La cámara se enciende solo cuando se aprieta el botón (no al entrar a la pestaña).
    def _camara(abrir: bool):
        st.session_state["factura-camara"] = abrir

    foto = None
    if st.session_state.get("factura-camara"):
        foto = st.camera_input("Encuadrá la parte de la factura con el consumo y el total", key=f"factura-foto-{n}")
        st.button("Cerrar la cámara", icon=":material/videocam_off:", type="tertiary", on_click=_camara, args=(False,))
    else:
        st.button("Sacar foto con la cámara", icon=":material/photo_camera:", on_click=_camara, args=(True,))
    fuente = archivo or foto
    if fuente is not None and st.button("Leer factura", icon=":material/document_scanner:", type="primary"):
        with st.spinner("Leyendo la factura…"):
            try:
                datos, nombre = fuente.getvalue(), getattr(fuente, "name", "foto.jpg")
                texto, metodo = FAC.leer(datos, nombre)
                cods = FAC.codigos(datos, nombre)
                if cods:
                    metodo += f" + {len(cods)} código{'s' if len(cods) > 1 else ''} QR/de barras"
                st.session_state["factura-detectada"] = {**FAC.extraer(texto, cods), "metodo": metodo}
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
            escs = s["tarifas"]["escenarios"]
            esc_det = det.get("escenario") if det.get("escenario") in escs else E.escenario()
            a, b = st.columns(2)
            mes_ok = a.selectbox("Mes del período", range(12), index=mes_det if mes_det is not None else s["factura"]["mes"],
                                 format_func=lambda i: MESES_LARGO[i])
            with b:
                esc_ok = st.selectbox("Subsidio", list(escs), index=list(escs).index(esc_det),
                                      format_func=lambda k: f"{escs[k]['icono']} {escs[k]['nombre']}")
                st.markdown(CONF[det.get("escenario_conf", "no encontrado")])
            if st.form_submit_button("Usar estos datos", icon=":material/check:", type="primary"):
                s["factura"].update({"kwh": kwh_ok, "dias": dias_ok, "mes": mes_ok, "importe": imp_ok})
                st.session_state["escenario"] = esc_ok  # el subsidio de la factura pasa a toda la app
                st.session_state.pop("factura-detectada", None)
                st.session_state["factura-n"] = n + 1  # vacía el archivo subido: la imagen no queda en la sesión
                st.session_state["factura-camara"] = False  # y apaga la cámara
                st.toast("Datos de la factura cargados", icon=":material/check_circle:")
                st.rerun()


# ---------- Calibración con la factura ----------
with st.container(border=True):
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
