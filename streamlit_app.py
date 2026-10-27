"""Simulador de consumo eléctrico hogareño — app de Streamlit.

Ejecutar:  streamlit run streamlit_app.py
"""
import streamlit as st

from simulador import estado as E
from simulador import guardado as G
from simulador import ui

st.set_page_config(page_title="¿Me paso o no me paso?", page_icon="⚡", layout="wide")

E.iniciar()
G.restaurar()  # al recargar la página, recupera la casa guardada (código en la dirección)
E.sincronizar()
ui.estilos()

paginas = [
    st.Page("app_pages/casa.py", title="Mi casa", icon=":material/home:", default=True),
    st.Page("app_pages/ambiente.py", title="Ambiente 3D", icon=":material/view_in_ar:"),
    st.Page("app_pages/factura.py", title="Factura", icon=":material/receipt_long:"),
    st.Page("app_pages/analisis.py", title="Análisis", icon=":material/analytics:"),
]
# Menú propio (ui.navbar) en lugar del de Streamlit, para que las pestañas se vean siempre.
pagina = st.navigation(paginas, position="hidden")
ui.navbar(paginas, pagina)

# El encabezado se completa al final, cuando ya se procesaron todos los cambios de la página.
encabezado = st.container()

pagina.run()

# El resumen de la casa no va en Análisis, que trata del dataset y no de la casa.
if pagina.title != "Análisis":
    with encabezado:
        ui.hero(E.resultados())

# Guarda lo elegido para que no se pierda al recargar la página.
G.guardar()
