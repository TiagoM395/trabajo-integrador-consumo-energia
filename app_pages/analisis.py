"""Análisis: el trabajo con el dataset y los modelos, paso a paso.

El contenido sale de explicaciones/README_ANALISIS.md (una sola fuente para los números). En la sección de
ajustes se suma lo que recibió el modelo en la última predicción.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

TEXTO = (Path(__file__).resolve().parent.parent / "explicaciones" / "README_ANALISIS.md").read_text(encoding="utf8")

# Solo las secciones numeradas ("## 1. Datos", "## 2. Variables", …).
secciones = []
for bloque in TEXTO.split("\n## ")[1:]:
    titulo, _, cuerpo = bloque.partition("\n")
    if titulo[:1].isdigit():
        secciones.append((titulo.strip(), cuerpo.strip().rstrip("-").strip()))

st.space("small")
st.markdown("#### 🔬 Análisis del dataset y de los modelos")
st.caption("Cómo se prepararon los datos, cómo se entrenaron y evaluaron los modelos de **¿Me paso o no me paso?** "
           "y en qué se equivocan. Datos: UCI *Individual Household Electric Power Consumption*.")

for titulo, cuerpo in secciones:
    with st.container(border=True):
        st.markdown(f"##### {titulo}")
        st.markdown(cuerpo)
        if titulo.startswith("3."):
            ult = st.session_state.get("pred-ultima")
            st.markdown("**Última predicción: lo que recibió el modelo**")
            if ult:
                st.dataframe(pd.DataFrame(ult["ajustes"]), hide_index=True)
                with st.expander("Las 16 variables tal como entran al modelo", icon=":material/table_view:"):
                    st.dataframe(pd.DataFrame([ult["fila"]]).T.rename(columns={0: "valor"}))
            else:
                st.caption("Todavía no se hizo ninguna predicción. Armá tu casa en *Mi casa* (paso 4) y volvé.")
