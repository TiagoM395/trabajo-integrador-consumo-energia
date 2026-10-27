"""Piezas de interfaz reutilizables: estilos, encabezado, tarjeta de artefacto y catálogo."""
from __future__ import annotations

import html

import streamlit as st

from simulador import calculo as C
from simulador import variantes as V
from simulador import estado as E
from simulador.estado import COLOR, COLOR_CAT, DIAS, MESES, MESES_LARGO, MODO_TXT, fmt

ESTILOS = """
<style>
/* Navbar propio: fijo arriba, nombre a la izquierda y las pestañas siempre visibles al centro */
header[data-testid="stHeader"]{display:none}
.stMainBlockContainer{padding-top:5.2rem !important}
.st-key-navbar{position:fixed;top:0;left:0;right:0;z-index:999990;display:grid !important;
  grid-template-columns:1fr auto 1fr;align-items:center;gap:8px;padding:10px 24px;
  background:linear-gradient(90deg,#0b1230,#1e1b4b);box-shadow:0 8px 24px -12px rgba(15,23,42,.7);
  border-bottom:1px solid rgba(255,255,255,.06)}
.st-key-navbar > div{width:auto !important}
.nav-marca{color:#fff;font-weight:800;font-size:1.08rem;letter-spacing:-.01em;white-space:nowrap}
.st-key-nav-links{display:flex !important;flex-direction:row !important;flex-wrap:wrap !important;
  justify-content:center;gap:4px}
.st-key-nav-links > div{width:auto !important}
.st-key-nav-links a{border-radius:999px;padding:4px 14px !important;transition:background .15s;text-decoration:none}
.st-key-nav-links a,.st-key-nav-links a *{color:rgba(238,242,255,.78) !important;white-space:nowrap}
.st-key-nav-links a:hover{background:rgba(255,255,255,.08) !important}
.st-key-nav-on a{background:rgba(16,185,129,.28) !important}
.st-key-nav-on a *{color:#fff !important}
@media (max-width: 640px){
  .st-key-navbar{grid-template-columns:1fr;justify-items:center;row-gap:4px;padding:8px 8px 6px}
  .nav-marca{font-size:1rem}
  .st-key-nav-links a{padding:2px 8px !important}
  .st-key-nav-links a p{font-size:.9rem !important}
  .stMainBlockContainer{padding-top:8.4rem !important}
}
.hero{position:relative;overflow:hidden;border-radius:22px;padding:18px 20px;color:#eef2ff;
  background:radial-gradient(900px 300px at 90% -20%,rgba(16,185,129,.45),transparent 60%),
  radial-gradient(700px 300px at 0% 0%,rgba(59,130,246,.45),transparent 60%),linear-gradient(160deg,#0b1230,#1e1b4b);
  box-shadow:0 18px 40px -20px rgba(15,23,42,.6)}
.hero:after{content:"";position:absolute;inset:0;opacity:.16;pointer-events:none;
  background-image:linear-gradient(rgba(255,255,255,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.07) 1px,transparent 1px);
  background-size:28px 28px;-webkit-mask-image:linear-gradient(#000,transparent);mask-image:linear-gradient(#000,transparent)}
.hero-top{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;position:relative;z-index:1}
.hero-marca{display:flex;gap:12px;align-items:center}
.hero-logo{width:44px;height:44px;border-radius:14px;display:grid;place-items:center;font-size:1.4rem;
  background:linear-gradient(135deg,#10b981,#0ea5e9);box-shadow:0 0 0 4px rgba(16,185,129,.2),0 10px 26px -8px #10b981;animation:latido 3s ease-in-out infinite}
@keyframes latido{50%{box-shadow:0 0 0 9px rgba(16,185,129,.06),0 10px 36px -6px #10b981}}
.hero h1{font-size:1.25rem;margin:0;padding:0;color:#fff;font-weight:800}
.hero-marca p{margin:0;color:#a5b4fc;font-size:.82rem}
/* Resultado de la predicción (paso 4 de Mi casa): más grande y destacado */
.hero.pred{padding:26px 28px;border-radius:24px}
.hero.pred .hero-marca{gap:22px}
.hero.pred .hero-logo{width:84px;height:84px;border-radius:24px;font-size:2.6rem;flex:none;animation:none}
.hero.pred h1{font-size:2.1rem;line-height:1.15;letter-spacing:-.02em}
.hero.pred .hero-marca p{font-size:1.1rem;line-height:1.55;color:#c7d2fe;margin-top:8px}
.hero.pred .hero-marca p b{color:#fff;font-size:1.25rem}
@media (max-width:640px){.hero.pred h1{font-size:1.5rem}.hero.pred .hero-logo{width:60px;height:60px;font-size:1.9rem}}
.hero-chips{display:flex;gap:6px;flex-wrap:wrap}
.hero-chip{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18);border-radius:99px;padding:.2rem .7rem;font-size:.78rem;font-weight:700}
.hero-chip.warn{background:rgba(249,115,22,.25);border-color:rgba(249,115,22,.6);color:#fed7aa}
.kpis{display:grid;grid-template-columns:1.25fr 1.25fr 1fr 1fr;gap:10px;margin-top:14px;position:relative;z-index:1}
.kpi{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.13);border-radius:16px;padding:10px 13px;min-width:0}
.kpi span{display:block;font-size:.72rem;color:#a5b4fc;font-weight:700;text-transform:uppercase;letter-spacing:.05em}
.kpi b{display:block;font-size:1.5rem;font-weight:800;letter-spacing:-.02em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#fff}
.kpi.g b{font-size:2rem}
.kpi b em{font-style:normal;font-size:.85rem;color:#c7d2fe}
.kpi small{display:block;color:#c7d2fe;font-size:.75rem;line-height:1.3}
.kpi.acc{background:linear-gradient(135deg,rgba(16,185,129,.3),rgba(14,165,233,.18));border-color:rgba(52,211,153,.5)}
@media (max-width:900px){.kpis{grid-template-columns:1fr 1fr}.kpi.g{grid-column:span 2}}

.t-h{display:flex;gap:10px;align-items:center;min-width:0}
.t-ico{width:50px;height:50px;flex:none;border-radius:15px;display:grid;place-items:center;font-size:1.6rem}
/* El nombre del electrodoméstico es lo primero que se lee en la tarjeta */
.t-nombre{display:block;font-size:1.28rem;font-weight:800;line-height:1.2;letter-spacing:-.01em}
/* Nombre como desplegable de variantes: se ve como título, con la flecha para cambiarlo */
[class*="st-key-nom-"] [data-baseweb="select"] > div{font-size:1.2rem;font-weight:800;letter-spacing:-.01em;
  background:transparent !important;border-color:transparent !important;padding-left:2px}
[class*="st-key-nom-"] [data-baseweb="select"] > div:hover{border-color:rgba(127,127,127,.35) !important}
.t-h b{display:block;font-size:.98rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.t-badges{display:flex;gap:4px;flex-wrap:wrap;margin-top:2px}
.t-badge{font-size:.68rem;font-weight:700;padding:.05rem .5rem;border-radius:99px;border:1px solid rgba(127,127,127,.3);opacity:.85}
.t-num{text-align:right;line-height:1.1}
.t-num b{font-size:1.2rem;font-weight:700;display:block}
.t-num small{opacity:.6;font-size:.72rem;display:block}
.t-num span{display:block;font-weight:800;color:#059669;font-size:.85rem;margin-top:2px}
/* Explicación de los números de la tarjeta: que no se salga de la pantalla */
[data-testid="stPopoverBody"]{max-width:min(440px,92vw) !important}
/* Grilla de Mi casa: tarjetas de 280 px; el espacio que sobra se reparte entre ellas, así la
   fila ocupa todo el ancho de la columna sin dejar un hueco al final */
.st-key-grilla{display:grid !important;grid-template-columns:repeat(auto-fill,280px);justify-content:space-between;column-gap:12px !important;row-gap:16px !important;
}
@media (max-width:640px){.st-key-grilla{grid-template-columns:1fr}}
.st-key-grilla > *{width:auto !important;min-width:0;container-type:inline-size}
/* Tarjeta cuadrada: como mínimo tan alta como ancha, sin barra para bajar adentro */
[class*="st-key-gcard-"]{border:1.5px solid rgba(148,163,184,.45) !important;border-radius:16px !important;
  box-shadow:0 6px 18px -10px rgba(15,23,42,.45);padding:12px 14px !important;
  min-height:100cqw;height:100%;overflow:visible !important}
/* El espacio sobrante se reparte: kWh y $ al centro, pregunta y cantidad abajo */
[class*="st-key-gcard-"] > [data-testid="stElementContainer"]:has(> [data-testid="stSpace"]){flex:1 1 auto !important}
[class*="st-key-gcard-"] [data-testid="stWidgetLabel"] p{font-size:.82rem !important;opacity:.85}
/* Nombre grande, como título; los largos en dos renglones en vez de cortarse */
[class*="st-key-gcard-"] .t-nombre{font-size:1.3rem;line-height:1.2}
[class*="st-key-gcard-"] [data-baseweb="select"] > div{font-size:1.25rem !important;padding-left:0;
  height:auto !important;min-height:2.6rem;align-items:center}
[class*="st-key-gcard-"] [data-baseweb="select"] > div *{white-space:normal !important;text-overflow:clip !important;
  overflow:visible !important;line-height:1.25 !important;text-wrap:balance}
[class*="st-key-gcard-"] [data-testid="stPopoverButton"] div[aria-hidden="true"]{display:none}
.g-ico{width:44px;height:44px;flex:none;border-radius:13px;display:grid;place-items:center;font-size:1.45rem}
/* kWh y $: el dato principal de la tarjeta, centrado y grande */
.g-num{text-align:center;line-height:1.05}
.g-num b{font-size:2.6rem;font-weight:800;letter-spacing:-.03em}
.g-num small{opacity:.6;font-size:.9rem;margin-left:3px}
.g-num span{display:block;font-weight:800;color:#10b981;font-size:1.35rem;margin-top:4px}
/* Cantidad compacta, en una sola línea */
[class*="st-key-cant-"] p{font-size:.9rem;opacity:.8}
.tira{display:grid;grid-template-columns:repeat(24,1fr);gap:2px;margin:2px 0}
.tira i{height:9px;border-radius:3px;background:rgba(127,127,127,.2)}
.tira .u{background:#10b981}
.tira .s{background:repeating-linear-gradient(135deg,#f97316 0 3px,rgba(249,115,22,.4) 3px 6px)}
.tira .e{background:rgba(148,163,184,.5)}
.tira .c{background:linear-gradient(90deg,#38bdf8,#22d3ee)}
.tira-l{display:flex;justify-content:space-between;font-size:.66rem;opacity:.55;margin-top:1px}
.split{font-size:.76rem;opacity:.85;display:flex;flex-wrap:wrap;gap:2px 12px}
.split .bar{width:100%;height:6px;border-radius:99px;background:rgba(127,127,127,.2);display:flex;overflow:hidden}
.split .bar i{display:block;height:100%}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px}
.perfil-ico{font-size:1.8rem;line-height:1}
.tip-item{display:flex;gap:10px;align-items:flex-start;padding:10px 12px;border-radius:12px;background:rgba(127,127,127,.08);margin-bottom:8px;font-size:.9rem}
.tip-item span{font-size:1.2rem}
.cat-ico{font-size:2rem;line-height:1.1}
.esc-total{font-size:2rem;font-weight:800;letter-spacing:-.02em;line-height:1.1}
.comp{display:flex;height:8px;border-radius:99px;overflow:hidden;margin:4px 0}
.comp i{display:block}
</style>
"""


def estilos() -> None:
    st.html(ESTILOS)


def navbar(paginas: list, actual) -> None:
    """Barra de arriba: nombre de la app y las pestañas, siempre visibles (también en el celular)."""
    with st.container(key="navbar"):
        st.html("<div class='nav-marca'>⚡ ¿Me paso o no me paso?</div>")
        with st.container(key="nav-links", horizontal=True, horizontal_alignment="center", gap="xxsmall"):
            for i, p in enumerate(paginas):
                activa = p.url_path == actual.url_path
                with st.container(key="nav-on" if activa else f"nav-{i}", width="content"):
                    st.page_link(p)


# ---------- Encabezado con KPIs ----------

def hero(r: dict) -> None:
    s = E.sim()
    m = E.mes()
    esc = E.escenario()
    if not s["items"]:
        st.html("""
        <div class="hero">
          <div class="hero-top">
            <div class="hero-marca"><div class="hero-logo">⚡</div>
              <div><h1>Resumen de tu casa</h1>
              <p>Todavía no elegiste ningún electrodoméstico. Agregá el primero en <b>Mi casa</b>
                 con el botón <b>+ Agregar</b> y acá vas a ver cuánto consume y cuánto cuesta.</p></div></div>
          </div>
        </div>""")
        return
    tar = s["tarifas"]
    mm = r["meses"][m]
    # Lo mismo que el paso 3 de Mi casa: suma de los electrodomésticos + cargo fijo, a precio fijo por kWh.
    costo = {k: E.costo(r, k)["total"] for k in tar["escenarios"]}
    f = {"total": costo[esc]}
    sin = {"total": costo["sin_subsidio"]}
    fantasma = mm["pas"] + mm["base"]
    if esc == "sin_subsidio":
        otros = [(k, sin["total"] - costo[k]) for k in tar["escenarios"] if k != "sin_subsidio"]
        k_mejor, v = max(otros, key=lambda x: x[1]) if otros else ("", 0)
        ahorro_v = f"$ {fmt(v)}"
    else:
        ahorro_v = f"$ {fmt(sin['total'] - f['total'])}"
    n = len(s["items"])
    vig = '/'.join(reversed(tar['vigencia_desde'].split('-'))) if tar.get('vigencia_desde') else ''
    mes_txt = MESES_LARGO[m]
    if esc == "sin_subsidio":
        # Se compara con el subsidio nacional (SEF), el más común.
        ref = "sef" if "sef" in tar["escenarios"] else k_mejor
        ahorro_v = f"$ {fmt(sin['total'] - costo[ref])}"
        ahorro_lbl = "Si tuvieras subsidio nacional (SEF)"
        ahorro_sub = "pagarías esto menos por mes"
    else:
        ahorro_lbl = "Lo que te ahorra tu subsidio"
        ahorro_sub = f"por mes, con {tar['escenarios'][esc]['nombre'].lower()}"
    aviso = ""
    if abs(s["ajuste"] - 1) > 1e-6:
        aviso = f"<span class='hero-chip warn'>Ajustado a tu factura ×{fmt(s['ajuste'], 2)}</span>"
    st.html(f"""
    <div class="hero">
      <div class="hero-top">
        <div class="hero-marca"><div class="hero-logo">⚡</div>
          <div><h1>Resumen de tu casa</h1>
          <p>Calculado con los {n} electrodomésticos que elegiste en <b>Mi casa</b> ·
             tarifa: <b>{tar['escenarios'][esc]['nombre'].lower()}</b> ·
             cuadro tarifario oficial de EDEA (consumos desde el {vig})</p></div></div>
        <div class="hero-chips">{aviso}</div>
      </div>
      <div class="kpis">
        <div class="kpi g"><span>Electricidad que usás por mes</span><b>{fmt(mm['total'])} <em>kWh</em></b>
          <small>suma de tus {n} electrodomésticos</small></div>
        <div class="kpi g acc"><span>Lo que pagarías por mes</span><b>$ {fmt(f['total'])}</b>
          <small>suma de tus electrodomésticos · con cargo fijo e impuestos</small></div>
        <div class="kpi"><span>{ahorro_lbl}</span><b>{ahorro_v}</b><small>{ahorro_sub}</small></div>
        <div class="kpi"><span>Gasto sin usar nada</span><b>{fmt(fantasma)} <em>kWh</em></b>
          <small>equipos en espera y siempre enchufados</small></div>
      </div>
    </div>""")
    with st.expander("¿De dónde salen estos números?", icon=":material/help:"):
        st.markdown(f"""
**No son mediciones de tu casa: son una cuenta** hecha con los datos que cargás.

1. **Electricidad (kWh).** Para cada electrodoméstico de la pestaña *Mi casa* se multiplica
   su **potencia** por las **horas que lo usás** (por ejemplo, una TV de 80 W prendida 5 horas
   por día usa 0,4 kWh por día, unos 12 kWh por mes). Después se suman todos.
2. **Los valores iniciales** (potencia, horas de uso) son **típicos**, sacados de la tabla de
   consumo estándar de la propuesta. Cambialos en cada tarjeta para que se parezcan a tu casa.
3. **La plata ($).** Sale del **cuadro tarifario oficial** de EDEA, aprobado por la
   {tar['resolucion']} y publicado por el OCEBA (consumos desde el {vig}):
   - cada kWh se paga a un **precio fijo** según tu subsidio: el de una casa típica de 300 kWh por
     mes (tramo R3), con el **Cargo Transición Tarifaria** y los **impuestos** (36,5 %) incluidos;
   - cada electrodoméstico vale sus kWh × ese precio, y **cambiar uno no cambia a los demás**;
   - lo que pagarías por mes es la **suma** de tus electrodomésticos y del consumo de base, más el
     **cargo fijo**.
   La factura real de EDEA cambia el precio según el **tramo** (R1 hasta 100 kWh, R2 hasta 200,
   R3 hasta 400…): ese número está abajo del total, en el paso 3 de *Mi casa*.
4. **Subsidios.** Elegí tu situación arriba de todo en *Mi casa*: con el **subsidio nacional (SEF)**
   los primeros 150 kWh salen más baratos; con la **tarifa social provincial** bajan los cargos y
   hay un descuento fijo por mes. Las fuentes con sus links están en `datos/FUENTES.md`.
5. **Gasto sin usar nada.** Lo que consumen los equipos enchufados aunque estén apagados
   (la lucecita de la TV, el decodificador, el router) más el consumo de base de la casa.

La tarifa y el consumo de base se cambian **arriba de todo en *Mi casa***.
Cuánto da tu consumo real lo dice tu factura: podés compararla en *Factura*.
""")


# ---------- Tarjeta de artefacto ----------

def _v(key: str, valor, param: str = "value") -> dict:
    """Pasa el valor inicial solo si el widget todavía no tiene estado (evita advertencias)."""
    return {} if key in st.session_state else {param: valor}


def _sumar_cantidad(k: str, paso: int) -> None:
    """Flechas de la cantidad: suben o bajan de a uno, entre 1 y 20."""
    st.session_state[k] = min(20, max(1, int(st.session_state.get(k, 1)) + paso))


def _al_elegir_variante(u: str) -> None:
    """Elegir otra variante en el nombre carga su valor estándar."""
    inst = E.buscar(u)
    nombre = st.session_state.get(f"{u}-var")
    if inst and nombre and nombre != PERSONALIZADO:
        V.aplicar(inst, nombre)


PERSONALIZADO = "__personalizado__"


def _al_cambiar_uso(u: str) -> None:
    """Si las horas de uso superan las horas enchufado, sube también las horas enchufado."""
    uso = st.session_state.get(f"{u}-uso")
    inst = E.buscar(u)
    if inst is None or uso is None:
        return
    inst["uso"] = float(uso)
    if inst["conectado"] < uso:
        inst["conectado"] = float(uso)
        st.session_state[f"{u}-conectado"] = float(uso)


def _al_cambiar_conectado(u: str) -> None:
    """Si las horas enchufado bajan de las horas de uso, baja también las horas de uso."""
    conn = st.session_state.get(f"{u}-conectado")
    inst = E.buscar(u)
    if inst is None or conn is None:
        return
    inst["conectado"] = float(conn)
    if inst["modo"] == "horas" and inst["uso"] > conn:
        inst["uso"] = float(conn)
        st.session_state[f"{u}-uso"] = float(conn)


def _quitar(u: str) -> None:
    inst = E.buscar(u)
    E.quitar(u)
    if inst:
        st.toast(f"{inst['icono']} {inst['nombre']} quitado", icon=":material/delete:")


def _de_donde(inst: dict, kwh: float, act: float, pas: float, ef: float, precio: dict | None = None) -> str:
    """Explicación de los kWh y la plata de la tarjeta, con los números del electrodoméstico.

    Con `precio` (cards de Mi casa) explica el precio por kWh del tramo; sin él (Ambiente 3D), el
    precio promedio de la factura.
    """
    q = int(inst.get("cantidad", 1))
    por_q = f" × {q} equipos" if q > 1 else ""
    dias = int(inst.get("dias", 7))
    por_dias = f" × {dias} de 7 días" if inst["modo"] == "horas" and dias < 7 else ""
    modo = inst["modo"]
    if modo == "horas":
        cuenta = (f"{fmt(inst['potencia_w'])} W × {_horas_uso_txt(inst['uso'])} por día{por_dias}{por_q} × 30 días "
                  f"= **{fmt(act, 1)} kWh** mientras lo usás")
    elif modo == "ciclos":
        cuenta = (f"{fmt(inst['kwh_ciclo'], 2)} kWh por uso × {int(inst['ciclos'])} veces por semana ÷ 7 días"
                  f"{por_q} × 30 días = **{fmt(act, 1)} kWh**")
    elif modo == "anual":
        cuenta = f"{fmt(inst['kwh_anio'])} kWh por año{por_q} × 30 días ÷ 365 días = **{fmt(act, 1)} kWh**"
    else:
        cuenta = f"{fmt(inst['potencia_w'])} W × 24 horas{por_q} × 30 días = **{fmt(act, 1)} kWh**"
    espera = (f" + **{fmt(pas, 1)} kWh** enchufado sin usar (standby)" if pas >= 0.05 else "")
    salto = "  \n"
    ps = "\\$"  # el $ escapado, para que el texto no se tome como fórmula
    kwh_txt = (f"**{fmt(kwh, 1)} kWh por mes:** la electricidad que usa este equipo en 30 días.{salto}"
               f"{cuenta}{espera}.\n\n")
    if precio and precio.get("tramo"):
        bloque = (f", con los primeros {fmt(precio['bloque_kwh'])} kWh a precio subsidiado"
                  if precio.get("bloque_kwh") else "")
        return (kwh_txt +
                f"**{ps} {fmt(kwh * ef)}:** lo que te cuesta la electricidad de este equipo por mes.{salto}"
                f"{fmt(kwh, 1)} kWh × {ps} {fmt(ef, 2)} por kWh = {ps} {fmt(kwh * ef)}.{salto}"
                f"Los {ps} {fmt(ef, 2)} por kWh son un precio fijo: lo que cuesta cada kWh en una casa típica "
                f"de {fmt(precio['kwh_ref'])} kWh por mes (tramo {precio['tramo']} de EDEA{bloque}): energía "
                f"({ps} {fmt(precio['energia'], 2)}) + Cargo Transición Tarifaria ({ps} {fmt(precio['ctt'], 2)}) "
                f"+ impuestos ({fmt(precio['impuestos_pct'], 1)} %). "
                f"Por ser fijo, este número **no cambia cuando cambiás otros equipos**, y el total del paso 3 es "
                f"la suma de todos más el cargo fijo. Solo cambia si elegís otro subsidio en el paso 1.")
    return (kwh_txt +
            f"**{ps} {fmt(kwh * ef)}:** lo que suma a tu factura de EDEA por mes.{salto}"
            f"{fmt(kwh, 1)} kWh × {ps} {fmt(ef)} por kWh = {ps} {fmt(kwh * ef)}.{salto}"
            f"Los {ps} {fmt(ef)} por kWh salen de dividir el total de tu factura (con cargo fijo e impuestos) "
            f"por los kWh de toda tu casa. Cambian según el subsidio que elegiste en el paso 1.")


# Horas de uso por día: de a 30 minutos, con 15 minutos al principio para los equipos que se usan
# un ratito (pava, microondas, secador…).
HORAS_USO = [0.0, 0.25] + [x / 2 for x in range(1, 49)]


def _a_horas_uso(h: float) -> float:
    """El valor de HORAS_USO más cercano."""
    return min(HORAS_USO, key=lambda x: abs(x - float(h)))


def _horas_uso_txt(h: float) -> str:
    if h == 0:
        return "0 h"
    hs, mins = int(h), round((h - int(h)) * 60)
    if hs == 0:
        return f"{mins} min"
    return f"{hs} h" + (f" {mins} min" if mins else "")


def _horas_txt(h: float) -> str:
    return f"{fmt(h, 0 if h == int(h) else 2)} h"


def tarjeta(inst: dict, r: dict, ef: float) -> None:
    """Tarjeta simple: el nombre es un desplegable de variantes; debajo, la pregunta principal y la cantidad."""
    u = inst["uid"]
    res = r["por_uid"][u]
    m = E.mes()
    c = E.CAT[inst["id"]]
    kwh = res["meses"][m]["total"] * r["ajuste"]
    act, pas = res["meses"][m]["act"] * r["ajuste"], res["meses"][m]["pas"] * r["ajuste"]
    color = COLOR_CAT[inst["cat"]]
    with st.container(border=True, key=f"card-{u}"):
        # Encabezado: nombre, consumo, plata y quitar
        a, b, acc = st.columns([0.64, 0.24, 0.12], vertical_alignment="center")
        variantes = V.VARIANTES.get(inst["id"])
        if variantes:
            ico, sel = a.columns([0.2, 0.8], vertical_alignment="center", gap="small")
            ico.html(f"<span class='t-ico' style='background:{color}22'>{inst['icono']}</span>")
            v_actual = V.actual(inst)
            opciones = [x["nombre"] for x in variantes]
            if v_actual is None:
                opciones = [PERSONALIZADO] + opciones
            k = f"{u}-var"
            st.session_state[k] = v_actual["nombre"] if v_actual else PERSONALIZADO
            with sel.container(key=f"nom-{u}"):
                st.selectbox("Electrodoméstico", opciones, key=k, label_visibility="collapsed",
                             on_change=_al_elegir_variante, args=(u,),
                             format_func=lambda n, nom=inst["nombre"]: nom if n == PERSONALIZADO else n)
        else:
            a.html(f"""<div class="t-h"><span class="t-ico" style="background:{color}22">{inst['icono']}</span>
              <div style="min-width:0"><span class="t-nombre">{html.escape(inst['nombre'])}</span></div></div>""")
        b.html(f"<div class='t-num'><b>{fmt(kwh, 1 if kwh < 10 else 0)}</b><small>kWh por mes</small>"
               f"<span>$ {fmt(kwh * ef)}</span></div>")
        with acc.container(gap="xxsmall", horizontal_alignment="right"):
            with st.popover("", icon=":material/info:", type="tertiary", help="¿De dónde salen estos números?"):
                st.markdown(_de_donde(inst, kwh, act, pas, ef))
            st.button("", icon=":material/delete:", key=f"{u}-del", on_click=_quitar, args=(u,),
                      help="Quitar este electrodoméstico de la casa")

        _pregunta(inst, bool(variantes))
        if variantes and v_actual:
            st.caption(f"**Valor estándar:** {v_actual['estandar']}.")
        with st.container(horizontal=True, vertical_alignment="center", gap="small", key=f"cant-{u}"):
            _cantidad(inst)

        for e in res["errores"]:
            st.error(e, icon=":material/error:")


def _pregunta(inst: dict, con_variantes: bool) -> None:
    """Control principal de la tarjeta: uno solo, según el tipo de equipo."""
    u = inst["uid"]
    if inst["modo"] == "horas":
        k = f"{u}-uso"
        st.select_slider("¿Cuántas horas por día lo usás?", HORAS_USO, key=k, format_func=_horas_uso_txt,
                         on_change=_al_cambiar_uso, args=(u,), **_v(k, _a_horas_uso(inst["uso"])))
    elif inst["modo"] == "ciclos":
        k = f"{u}-ciclos"
        st.slider("¿Cuántas veces por semana lo usás?", 0, 14, key=k, **_v(k, int(inst["ciclos"])))
    elif inst["modo"] == "anual" and not con_variantes:
        k = f"{u}-kwh_anio"
        st.slider("Consumo que dice la etiqueta (kWh por año)", 50.0, 1200.0, step=5.0, key=k,
                  **_v(k, float(inst["kwh_anio"])),
                  help="Está en la etiqueta de eficiencia pegada en el equipo.")
    elif inst["modo"] == "siempre":
        k = f"{u}-potencia_w"
        st.slider("Potencia (W) — está prendido las 24 horas", 1.0, 60.0, step=1.0, key=k,
                  **_v(k, float(inst["potencia_w"])))


def _cantidad(inst: dict) -> None:
    """«Cantidad ⌄ 1 ⌃»: flechas para bajar y subir de a uno, entre 1 y 20."""
    u = inst["uid"]
    k = f"{u}-cantidad"
    if k not in st.session_state:
        st.session_state[k] = int(inst["cantidad"])
    cant = st.session_state[k]
    st.markdown("Cantidad", width="content")
    st.button("", icon=":material/keyboard_arrow_down:", key=f"{u}-menos", type="tertiary",
              disabled=cant <= 1, on_click=_sumar_cantidad, args=(k, -1), help="Uno menos")
    st.markdown(f"**{cant}**", width="content")
    st.button("", icon=":material/keyboard_arrow_up:", key=f"{u}-mas", type="tertiary",
              disabled=cant >= 20, on_click=_sumar_cantidad, args=(k, 1), help="Uno más")


def _nombre(inst: dict, variantes: list | None, v_actual: dict | None) -> None:
    """Nombre del equipo: desplegable de variantes, o texto fijo si no tiene."""
    u = inst["uid"]
    if not variantes:
        # Guion que no corta renglón: «Wi-Fi» no se parte en dos
        st.html(f"<span class='t-nombre'>{html.escape(inst['nombre']).replace('-', chr(0x2011))}</span>")
        return
    opciones = [x["nombre"] for x in variantes]
    if v_actual is None:
        opciones = [PERSONALIZADO] + opciones
    k = f"{u}-var"
    st.session_state[k] = v_actual["nombre"] if v_actual else PERSONALIZADO
    with st.container(key=f"nom-{u}"):
        st.selectbox("Electrodoméstico", opciones, key=k, label_visibility="collapsed",
                     on_change=_al_elegir_variante, args=(u,),
                     format_func=lambda n, nom=inst["nombre"]: nom if n == PERSONALIZADO else n)


def colores_grilla(items: list[dict]) -> None:
    """Franja de arriba de cada tarjeta, con el color de su categoría."""
    reglas = "".join(f".st-key-gcard-{i['uid']}{{border-top:5px solid {COLOR_CAT[i['cat']]} !important}}"
                     for i in items)
    st.html(f"<style>{reglas}</style>")


def tarjeta_grilla(inst: dict, r: dict, ef: float, precio: dict | None = None) -> None:
    """Tarjeta cuadrada de la grilla de Mi casa, de arriba hacia abajo:
    ícono y nombre · kWh y $ (al centro) · la pregunta · cantidad, ⓘ y quitar."""
    u = inst["uid"]
    res = r["por_uid"][u]
    m = E.mes()
    kwh = res["meses"][m]["total"] * r["ajuste"]
    act, pas = res["meses"][m]["act"] * r["ajuste"], res["meses"][m]["pas"] * r["ajuste"]
    color = COLOR_CAT[inst["cat"]]
    variantes = V.VARIANTES.get(inst["id"])
    v_actual = V.actual(inst) if variantes else None
    with st.container(border=True, key=f"gcard-{u}", gap="xxsmall"):
        with st.container(horizontal=True, vertical_alignment="center", gap="small"):
            st.html(f"<span class='g-ico' style='background:{color}26'>{inst['icono']}</span>", width="content")
            with st.container(width="stretch"):
                _nombre(inst, variantes, v_actual)
        st.space("stretch")
        st.html(f"<div class='g-num'><b>{fmt(kwh, 1 if kwh < 10 else 0)}</b><small>kWh por mes</small>"
                f"<span>$ {fmt(kwh * ef)}</span></div>")
        st.space("stretch")
        _pregunta(inst, bool(variantes))
        for e in res["errores"]:
            st.error(e, icon=":material/error:")
        with st.container(horizontal=True, vertical_alignment="center", gap="xxsmall", key=f"cant-{u}"):
            _cantidad(inst)
            st.space("stretch")
            with st.popover("", icon=":material/info:", type="tertiary", help="¿De dónde salen estos números?"):
                st.markdown(_de_donde(inst, kwh, act, pas, ef, precio))
                if v_actual:
                    st.caption(f"**Valor estándar:** {v_actual['estandar']}.")
            st.button("", icon=":material/delete:", key=f"{u}-del", type="tertiary", on_click=_quitar, args=(u,),
                      help="Quitar este electrodoméstico de la casa")


# ---------- Catálogo ----------

def tipico(id_cat: str) -> float:
    return sum(x["total"] for x in C.mensual(C.instancia(id_cat))) / 12


@st.dialog("Agregar electrodoméstico", width="large", icon=":material/add_circle:")
def catalogo(amb: str | None = None) -> None:
    q = st.text_input("Buscar", placeholder="heladera, aire, router…", label_visibility="collapsed",
                      icon=":material/search:")
    cats = ["todas"] + list(E.CATEGORIAS)
    cat = st.pills("Categoría", cats, default="todas", required=True, label_visibility="collapsed",
                   format_func=lambda k: "✨ Todas" if k == "todas" else f"{E.CATEGORIAS[k]['icono']} {E.CATEGORIAS[k]['nombre']}")

    def norm(t: str) -> str:
        import unicodedata
        return "".join(ch for ch in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(ch) != "Mn")

    lista = [c for c in E.D["CATALOGO"] if (cat == "todas" or c["cat"] == cat) and (not q or norm(q) in norm(c["nombre"]))]
    if not lista:
        st.caption("No encontramos ese artefacto.")
    cols = st.columns(3)
    for i, c in enumerate(lista):
        with cols[i % 3].container(border=True):
            st.html(f"<div class='cat-ico'>{c['icono']}</div><b>{c['nombre']}</b>")
            ya = sum(1 for x in E.sim()["items"] if x["id"] == c["id"])
            st.caption(f"≈ **{fmt(tipico(c['id']), 1)} kWh/mes** · {MODO_TXT[c['modo']]}" + (f" · ya tenés {ya}" if ya else ""))
            if st.button("Agregar", key=f"cat-{c['id']}", icon=":material/add:", width="stretch"):
                inst = E.agregar(c["id"], amb)
                if amb:
                    E.sim()["seleccion"] = "i:" + inst["uid"]
                st.toast(f"{inst['icono']} {inst['nombre']} agregado", icon=":material/check_circle:")
                st.rerun()


def consejos(r: dict) -> list[tuple[str, str]]:
    """Consejos calculados con la factura real del mes (tramos de EDEA)."""
    s = E.sim()
    m = E.mes()
    mm = r["meses"][m]
    tar = s["tarifas"]
    esc = E.escenario()
    kwh = mm["total"]
    f = C.factura(kwh, tar, esc)

    def ahorro_pesos(menos_kwh: float) -> float:
        """Ahorro en la factura real de EDEA (con tramos)."""
        return f["total"] - C.factura(max(0.0, kwh - menos_kwh), tar, esc)["total"]

    precio = C.precio_kwh(tar, esc)["precio"]  # el mismo precio fijo que usan las cards

    out = []
    # Apenas pasado de un tramo: bajar unos pocos kWh cambia el cargo fijo y el precio de todos los kWh
    if f.get("tramo_desde") and 0 < kwh - f["tramo_desde"] <= 30:
        exceso = kwh - f["tramo_desde"]
        out.append(("📉", f"Estás **{fmt(exceso)} kWh** por encima del límite del tramo ({fmt(f['tramo_desde'])} kWh). "
                          f"Si bajás eso, en la factura de EDEA pasás a un tramo más barato y pagás unos "
                          f"**\\$ {fmt(ahorro_pesos(exceso))}** menos por mes."))
    if f.get("tope") and f.get("fuera", 0) > 0:
        out.append(("🚨", f"Te pasás **{fmt(f['fuera'])} kWh** de los {fmt(f['tope'])} kWh con precio subsidiado: "
                          "esos kWh se pagan a precio pleno."))
    horas = [(it, it["meses"][m]["act"]) for it in r["items"]]
    horas = [(it, v) for it, v in horas if E.buscar(it["uid"]) and E.buscar(it["uid"])["modo"] == "horas"
             and E.buscar(it["uid"])["uso"] >= 1 and v > 0]
    if horas:
        it, v = max(horas, key=lambda p: p[1])
        inst = E.buscar(it["uid"])
        menos = v / inst["uso"] * r["ajuste"]
        out.append(("⏱️", f"Si usás **{inst['nombre']}** 1 hora menos por día, ahorrás **{fmt(menos, 1)} kWh** "
                          f"y unos **\\$ {fmt(menos * precio)}** por mes."))
    if mm["pas"] > 0.5:
        out.append(("🔌", f"El standby de tus equipos suma **{fmt(mm['pas'], 1)} kWh/mes** "
                          f"(\\$ {fmt(mm['pas'] * precio)}). Una zapatilla con interruptor lo corta de una sola vez."))
    if esc == "sin_subsidio":
        out.append(("🧾", "Si tu hogar tiene subsidio nacional o tarifa social, elegilo en el paso 1 de *Mi casa*."))
    return out[:4] or [("✅", "Tu consumo está equilibrado.")]
