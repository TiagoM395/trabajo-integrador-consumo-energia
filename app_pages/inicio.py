"""Lobby principal para explorar las herramientas del simulador."""
import streamlit as st


with st.container(key="lobby"):
    with st.container(key="lobby-hero"):
        texto, visual = st.columns([1.15, 0.85], gap="large", vertical_alignment="center")
        with texto:
            st.html("""
            <div class="lobby-hero-copy">
              <div class="lobby-eyebrow"><span class="lobby-live-dot"></span> ENERGÍA INTELIGENTE PARA TU HOGAR</div>
              <h1>Tu energía,<br><span>bajo control.</span></h1>
              <p>Entendé cuánto consume tu casa, visualizá cada ambiente y encontrá nuevas formas de ahorrar.</p>
            </div>
            """)
            with st.container(horizontal=True, key="lobby-hero-links"):
                st.page_link(
                    "app_pages/casa.py",
                    label="Empezar con mi casa",
                    icon=":material/arrow_forward:",
                    width="stretch",
                )
                st.page_link(
                    "app_pages/ambiente.py",
                    label="Explorar en 3D",
                    icon=":material/view_in_ar:",
                    width="stretch",
                )
            st.html("""
            <div class="lobby-trust"><span>⚡</span> Datos claros · Decisiones más inteligentes</div>
            """)
        with visual:
            st.html("""
            <div class="lobby-visual" aria-hidden="true">
              <div class="lobby-orbit lobby-orbit-one"></div>
              <div class="lobby-orbit lobby-orbit-two"></div>
              <div class="lobby-energy-core"><span>⚡</span></div>
              <div class="lobby-float lobby-float-top"><span>⌂</span> Tu hogar</div>
              <div class="lobby-float lobby-float-bottom"><span>↘</span> Consumo consciente</div>
              <div class="lobby-visual-caption">ENERGÍA EN EQUILIBRIO</div>
            </div>
            """)

    st.html("""
    <div class="lobby-section-heading">
      <div>
        <span class="lobby-section-kicker">TU CENTRO DE CONTROL</span>
        <h2>¿Qué querés explorar?</h2>
      </div>
      <p>Cuatro herramientas conectadas para entender y mejorar el consumo de tu hogar.</p>
    </div>
    """)

    izquierda, derecha = st.columns(2, gap="large")
    with izquierda:
        with st.container(key="lobby-card-casa"):
            st.html("""
            <div class="lobby-card-top">
              <span class="lobby-card-icon">⌂</span>
              <span class="lobby-card-index">01 / CONFIGURAR</span>
            </div>
            <h3>Mi casa</h3>
            <p>Armá tu hogar, elegí tus electrodomésticos y conocé el gasto estimado de cada uno.</p>
            """)
            st.page_link(
                "app_pages/casa.py",
                label="Configurar mi casa",
                icon=":material/arrow_forward:",
                width="stretch",
            )
    with derecha:
        with st.container(key="lobby-card-ambiente"):
            st.html("""
            <div class="lobby-card-top">
              <span class="lobby-card-icon">◇</span>
              <span class="lobby-card-index">02 / VISUALIZAR</span>
            </div>
            <h3>Ambiente 3D</h3>
            <p>Recorré cada habitación, ubicá tus artefactos y explorá cómo se usa la energía.</p>
            """)
            st.page_link(
                "app_pages/ambiente.py",
                label="Explorar ambientes",
                icon=":material/arrow_forward:",
                width="stretch",
            )

    izquierda, derecha = st.columns(2, gap="large")
    with izquierda:
        with st.container(key="lobby-card-factura"):
            st.html("""
            <div class="lobby-card-top">
              <span class="lobby-card-icon">▤</span>
              <span class="lobby-card-index">03 / COMPARAR</span>
            </div>
            <h3>Mi factura</h3>
            <p>Revisá los datos de tu factura y comparalos con el consumo de tu casa.</p>
            """)
            st.page_link(
                "app_pages/factura.py",
                label="Revisar mi factura",
                icon=":material/arrow_forward:",
                width="stretch",
            )
    with derecha:
        with st.container(key="lobby-card-analisis"):
            st.html("""
            <div class="lobby-card-top">
              <span class="lobby-card-icon">⌁</span>
              <span class="lobby-card-index">04 / COMPRENDER</span>
            </div>
            <h3>Análisis</h3>
            <p>Conocé los datos, las variables y los modelos detrás de las estimaciones.</p>
            """)
            st.page_link(
                "app_pages/analisis.py",
                label="Ver el análisis",
                icon=":material/arrow_forward:",
                width="stretch",
            )

    st.html("""
    <div class="lobby-footer">
      <span class="lobby-footer-mark">⚡</span>
      <span>Pequeños cambios en casa. Una energía mejor para todos.</span>
      <span class="lobby-footer-line"></span>
      <span class="lobby-footer-note">SIMULADOR DE CONSUMO ELÉCTRICO</span>
    </div>
    """)
