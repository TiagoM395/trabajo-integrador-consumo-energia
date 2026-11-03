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
.pred-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:18px}
.pred-stats > div{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:14px;
  padding:10px 14px;color:#e6e9f2}
.pred-stats span{display:block;font-size:.7rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;
  color:#a7f3d0}
.pred-stats b{display:block;font-size:1.35rem;color:#fff;font-variant-numeric:tabular-nums;margin:2px 0}
.pred-stats small{color:#c7d2fe;font-size:.78rem}
@media (max-width:900px){.pred-stats{grid-template-columns:1fr 1fr}}
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
/* La grilla se adapta al ancho disponible y mantiene tarjetas de tamaño uniforme. */
.st-key-grilla{
  display:grid !important;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));
  align-items:stretch;column-gap:16px !important;row-gap:18px !important
}
@media (max-width:640px){.st-key-grilla{grid-template-columns:1fr}}
.st-key-grilla > *{width:auto !important;min-width:0;container-type:inline-size}
/* Las tarjetas mantienen una altura consistente sin forzar una forma cuadrada. */
[class*="st-key-gcard-"]{border:1.5px solid rgba(148,163,184,.45) !important;border-radius:16px !important;
  box-shadow:0 6px 18px -10px rgba(15,23,42,.45);padding:12px 14px !important;
  min-height:320px;height:100%;overflow:visible !important}
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

/* El tema de Streamlit atenúa por defecto las ayudas y los textos secundarios. */
.stApp [data-testid="stCaptionContainer"]{
  color:#526874 !important;opacity:1 !important
}
.stApp [data-testid="stCaptionContainer"] *{color:inherit !important;opacity:1 !important}
.stApp label,.stApp [data-testid="stWidgetLabel"],
.stApp [data-testid="stWidgetLabel"] p{color:#263f4c}

/* Experiencia visual de la portada: conservar los componentes y sumar feedback visual. */
.stApp:has(.st-key-w-escenario){
  background:#fff;
  overflow-x:hidden
}
html:has(.st-key-w-escenario){scroll-padding-top:7.5rem;scroll-behavior:smooth}
.stApp:has(.st-key-w-escenario) [data-testid="stAppViewContainer"],
.stApp:has(.st-key-w-escenario) [data-testid="stMain"]{background:transparent}
.stApp:has(.st-key-w-escenario) .stMainBlockContainer{
  max-width:1480px;padding-top:1rem !important;padding-bottom:4rem;
  padding-left:clamp(1rem,3vw,2.5rem);padding-right:clamp(1rem,3vw,2.5rem)
}
.stApp:has(.st-key-w-escenario) .st-key-navbar{
  position:relative;top:auto;left:auto;right:auto;width:100%;margin:0 auto 1.25rem;
  grid-template-columns:1fr auto 1fr;padding:11px clamp(1rem,3vw,2.5rem);
  background:linear-gradient(90deg,#0b1230,#1e1b4b);
  border-bottom:1px solid rgba(255,255,255,.12);
  box-shadow:0 8px 24px -12px rgba(15,23,42,.7);
  backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px)
}
.stApp:has(.st-key-w-escenario) .nav-marca{
  display:flex;align-items:center;gap:.55rem;font-size:1.02rem;letter-spacing:-.025em
}
.stApp:has(.st-key-w-escenario) .st-key-nav-links{gap:6px}
.stApp:has(.st-key-w-escenario) .st-key-nav-links a{
  min-height:40px;padding:7px 14px !important;
  transition:background .18s ease,color .18s ease,transform .18s ease,box-shadow .18s ease
}
.stApp:has(.st-key-w-escenario) .st-key-nav-links a:hover,
.stApp:has(.st-key-w-escenario) .st-key-nav-links a:focus-visible{
  background:rgba(255,255,255,.13) !important;transform:translateY(-1px);
  outline:2px solid rgba(167,243,208,.72);outline-offset:2px
}
.stApp:has(.st-key-w-escenario) .st-key-nav-on a{
  background:linear-gradient(135deg,rgba(16,185,129,.42),rgba(34,211,238,.25)) !important;
  box-shadow:inset 0 0 0 1px rgba(209,250,229,.24),0 5px 16px -12px rgba(52,211,153,.85)
}
.stApp:has(.st-key-w-escenario) .hero{
  padding:clamp(20px,3vw,32px);border:1px solid rgba(255,255,255,.16);
  border-radius:26px;
  background:
    radial-gradient(900px 300px at 90% -20%,rgba(16,185,129,.45),transparent 60%),
    radial-gradient(700px 300px at 0% 0%,rgba(59,130,246,.45),transparent 60%),
    linear-gradient(160deg,#0b1230,#1e1b4b);
  box-shadow:0 18px 40px -20px rgba(15,23,42,.6);
  transition:box-shadow .22s ease,transform .22s ease
}
.stApp:has(.st-key-w-escenario) .hero:hover{box-shadow:0 28px 66px -38px rgba(8,68,76,.9)}
.stApp:has(.st-key-w-escenario) .hero-logo{
  background:linear-gradient(135deg,#34d399,#22d3ee);
  box-shadow:0 0 0 5px rgba(52,211,153,.17),0 14px 32px -13px rgba(34,211,238,.9)
}
.stApp:has(.st-key-w-escenario) .hero-marca p{color:#d0eeeb;line-height:1.65}
.stApp:has(.st-key-w-escenario) .hero-marca p b{color:#fff}
.stApp:has(.st-key-w-escenario) .kpis{gap:12px;margin-top:18px}
.stApp:has(.st-key-w-escenario) .kpi{
  padding:14px 16px;border:1px solid rgba(226,255,250,.19);border-radius:18px;
  background:rgba(255,255,255,.095);backdrop-filter:blur(10px);
  transition:transform .18s ease,background .18s ease,border-color .18s ease
}
.stApp:has(.st-key-w-escenario) .kpi:hover{
  transform:translateY(-2px);background:rgba(255,255,255,.14);border-color:rgba(226,255,250,.3)
}
.stApp:has(.st-key-w-escenario) .kpi span{color:#b8dcd9}
.stApp:has(.st-key-w-escenario) .kpi.acc{
  background:linear-gradient(135deg,rgba(16,185,129,.38),rgba(34,211,238,.2));
  border-color:rgba(110,231,183,.48)
}
.stApp:has(.st-key-w-escenario) .kpi.acc span{color:#d1fae5}
.stApp:has(.st-key-w-escenario) .stMarkdown h3,
.stApp:has(.st-key-w-escenario) .stMarkdown h4{
  color:#173847;letter-spacing:-.035em
}
.stApp:has(.st-key-w-escenario) .stMarkdown h3{font-size:1.35rem;font-weight:800}
.stApp:has(.st-key-w-escenario) .stMarkdown h4{font-size:1.08rem;font-weight:750}
.stApp:has(.st-key-w-escenario) [data-testid="stCaptionContainer"]{color:#526874;line-height:1.6}
.stApp:has(.st-key-w-escenario) [data-testid="stMain"] .stMarkdown p{
  color:#263f4c !important;opacity:1 !important
}
.stApp:has(.st-key-w-escenario) [data-testid="stMain"] [data-testid="stMetricValue"],
.stApp:has(.st-key-w-escenario) [data-testid="stMain"] [data-testid="stMetricLabel"]{
  color:#173847 !important;opacity:1 !important
}
.stApp:has(.st-key-w-escenario) [data-testid="stMain"] .stPlotlyChart svg text{
  fill:#334e68 !important;fill-opacity:1 !important
}
.stApp:has(.st-key-w-escenario) [data-testid="stMain"] .stHtml:has(.dot) small{
  color:#526874 !important;opacity:1 !important
}
.stApp:has(.st-key-w-escenario) .t-num small,
.stApp:has(.st-key-w-escenario) .g-num small,
.stApp:has(.st-key-w-escenario) [class*="st-key-cant-"] p,
.stApp:has(.st-key-w-escenario) .t-badge,
.stApp:has(.st-key-w-escenario) .tira-l,
.stApp:has(.st-key-w-escenario) .split{
  color:#526874;opacity:1
}
.stApp:has(.st-key-w-escenario) .stVerticalBlock:has(.st-key-w-escenario){
  padding:clamp(16px,2.2vw,24px) !important;border-color:#a3b1c6 !important;
  border-radius:22px !important;
  background:linear-gradient(145deg,rgba(248,250,255,.98),rgba(240,246,255,.92));
  box-shadow:0 16px 38px -30px rgba(30,58,110,.48);
  transition:box-shadow .2s ease,border-color .2s ease
}
.stApp:has(.st-key-w-escenario) .stVerticalBlock:has(.st-key-w-escenario):hover{
  border-color:#b9c9e6 !important;box-shadow:0 20px 42px -30px rgba(30,64,130,.4)
}
.stApp:has(.st-key-w-escenario) .stVerticalBlock:has(.perfil-ico){
  border-color:#a3b1c6 !important;border-radius:20px !important;
  background:linear-gradient(155deg,#fff 0%,#f1f6ff 100%);
  box-shadow:0 10px 28px -24px rgba(25,55,110,.48);
  transition:transform .2s ease,border-color .2s ease,box-shadow .2s ease
}
.stApp:has(.st-key-w-escenario) .stVerticalBlock:has(.perfil-ico):hover{
  transform:translateY(-4px);border-color:#a9bee5 !important;
  box-shadow:0 20px 34px -24px rgba(35,76,151,.42)
}
.stApp:has(.st-key-w-escenario) .perfil-ico{
  display:grid;width:54px;height:54px;place-items:center;margin-bottom:12px;
  border:1px solid #a3b1c6;border-radius:17px;
  background:linear-gradient(145deg,#e9f1ff,#e8f7fb);font-size:1.9rem
}
.stApp:has(.st-key-w-escenario) .stVerticalBlock:has(.st-key-gcard-){
  border-color:#a3b1c6 !important;border-radius:20px !important;
  background:
    radial-gradient(ellipse at 100% 0%,rgba(59,130,246,.09),transparent 48%),
    linear-gradient(155deg,#fff 0%,#f3f7ff 100%);
  box-shadow:0 12px 30px -24px rgba(25,55,110,.55);
  transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease
}
.stApp:has(.st-key-w-escenario) .stVerticalBlock:has(.st-key-gcard-):hover{
  transform:translateY(-3px);border-color:#a9bee5 !important;
  box-shadow:0 20px 36px -24px rgba(35,76,151,.4)
}
.stApp:has(.st-key-w-escenario) .g-num span{color:#087f9b}
.stApp:has(.st-key-w-escenario) .stVerticalBlock:has([data-testid="stMetric"]),
.stApp:has(.st-key-w-escenario) .stVerticalBlock:has([data-testid="stPlotlyChart"]),
.stApp:has(.st-key-w-escenario) .stVerticalBlock:has([data-testid="stDataFrame"]),
.stApp:has(.st-key-w-escenario) .stVerticalBlock:has(.tip-item){
  border-color:#a3b1c6 !important;border-radius:19px !important;
  background:linear-gradient(155deg,rgba(255,255,255,.96),rgba(243,247,255,.94));
  box-shadow:0 10px 28px -24px rgba(25,55,110,.48)
}
.stApp:has(.st-key-w-escenario) .stButton > button{
  min-height:42px;border-radius:13px;font-weight:700;
  transition:transform .16s ease,box-shadow .16s ease,background .16s ease,border-color .16s ease
}
.stApp:has(.st-key-w-escenario) .stButton > button:hover:not(:disabled){
  transform:translateY(-2px);box-shadow:0 10px 22px -16px rgba(17,70,79,.62)
}
.stApp:has(.st-key-w-escenario) .stButton > button:focus-visible,
.stApp:has(.st-key-w-escenario) [data-baseweb="select"] > div:focus-within{
  outline:3px solid rgba(16,185,129,.28);outline-offset:2px
}
.stApp:has(.st-key-w-escenario) .stButton > button[kind="primary"]{
  border-color:#31599f;background:linear-gradient(135deg,#31599f,#243b73);
  box-shadow:0 9px 20px -14px rgba(36,59,115,.78)
}
.stApp:has(.st-key-w-escenario) .stButton > button[kind="primary"]:hover:not(:disabled){
  border-color:#1d3265;background:linear-gradient(135deg,#294b8a,#1d3265);
  box-shadow:0 13px 24px -14px rgba(36,59,115,.78)
}
.stApp:has(.st-key-w-escenario) [data-baseweb="select"] > div,
.stApp:has(.st-key-w-escenario) [data-baseweb="input"] > div,
.stApp:has(.st-key-w-escenario) [data-baseweb="textarea"] > div{border-radius:12px}
.stApp:has(.st-key-w-escenario) [data-testid="stExpander"]{
  border-color:#dfe9ec;border-radius:16px;background:rgba(255,255,255,.78);
  transition:border-color .18s ease,background .18s ease
}
.stApp:has(.st-key-w-escenario) [data-testid="stExpander"]:hover{
  border-color:#b9d8d1;background:#fff
}
.stApp:has(.st-key-w-escenario) [data-testid="stDataFrame"]{
  overflow:hidden;border:1px solid #e4edf1;border-radius:15px
}
.stApp:has(.st-key-w-escenario) .stMarkdown h3,
.stApp:has(.st-key-w-escenario) .stMarkdown h4{scroll-margin-top:7.5rem}
@media (max-width:900px){
  .stApp:has(.st-key-w-escenario) .stMainBlockContainer{
    padding-left:1rem;padding-right:1rem
  }
  .stApp:has(.st-key-w-escenario) .hero{padding:20px;border-radius:22px}
}
@media (max-width:640px){
  html:has(.st-key-w-escenario){scroll-padding-top:8.5rem}
  .stApp:has(.st-key-w-escenario) .stMainBlockContainer{
    padding-top:1rem !important;padding-left:.75rem;padding-right:.75rem;padding-bottom:2.5rem
  }
  .stApp:has(.st-key-w-escenario) .st-key-navbar{
    grid-template-columns:1fr;justify-items:center;row-gap:5px;padding:8px 8px 7px
  }
  .stApp:has(.st-key-w-escenario) .nav-marca{font-size:1rem}
  .stApp:has(.st-key-w-escenario) .st-key-nav-links{gap:2px}
  .stApp:has(.st-key-w-escenario) .st-key-nav-links a{
    min-height:36px;padding:4px 8px !important
  }
  .stApp:has(.st-key-w-escenario) .st-key-nav-links a p{font-size:.84rem !important}
  .stApp:has(.st-key-w-escenario) .hero{padding:16px;border-radius:19px}
  .stApp:has(.st-key-w-escenario) .hero-top{align-items:flex-start}
  .stApp:has(.st-key-w-escenario) .hero-marca{align-items:flex-start;gap:10px}
  .stApp:has(.st-key-w-escenario) .hero-logo{width:38px;height:38px;flex:none}
  .stApp:has(.st-key-w-escenario) .hero-marca p{font-size:.8rem;line-height:1.55}
  .stApp:has(.st-key-w-escenario) .kpis{gap:8px;margin-top:14px}
  .stApp:has(.st-key-w-escenario) .kpi{padding:10px;border-radius:14px}
  .stApp:has(.st-key-w-escenario) .kpi span{font-size:.64rem;line-height:1.35}
  .stApp:has(.st-key-w-escenario) .kpi b{font-size:1.15rem}
  .stApp:has(.st-key-w-escenario) .kpi.g b{font-size:1.42rem}
  .stApp:has(.st-key-w-escenario) .stVerticalBlock:has(.st-key-w-escenario){
    padding:14px !important;border-radius:17px !important
  }
  .stApp:has(.st-key-w-escenario) .stVerticalBlock:has(.perfil-ico){
    border-radius:16px !important
  }
  .stApp:has(.st-key-w-escenario) .stMarkdown h3{font-size:1.18rem}
}
@media (prefers-reduced-motion:reduce){
  .stApp:has(.st-key-w-escenario) *,
  .stApp:has(.st-key-w-escenario) *::before,
  .stApp:has(.st-key-w-escenario) *::after{
    scroll-behavior:auto !important;animation-duration:.01ms !important;
    animation-iteration-count:1 !important;transition-duration:.01ms !important
  }
}

.stApp:has(.st-key-lobby){
  background:
    radial-gradient(ellipse at 4% 4%,rgba(16,185,129,.1),transparent 34rem),
    radial-gradient(ellipse at 95% 24%,rgba(34,211,238,.09),transparent 32rem),
    linear-gradient(180deg,#f7fafc 0%,#eef5f6 100%);
  overflow-x:hidden
}
.stApp:has(.st-key-lobby) [data-testid="stAppViewContainer"],
.stApp:has(.st-key-lobby) [data-testid="stMain"]{background:transparent}
.stApp:has(.st-key-lobby) .stMainBlockContainer{
  max-width:1420px;padding:1rem clamp(1rem,3vw,2.5rem) 3.5rem !important
}
.stApp:has(.st-key-lobby) .st-key-navbar{
  position:relative;top:auto;left:auto;right:auto;width:100%;margin:0 auto 1.4rem;
  grid-template-columns:1fr auto 1fr;padding:11px clamp(1rem,3vw,2.5rem);
  background:linear-gradient(90deg,#0b1230,#1e1b4b);
  border-bottom:1px solid rgba(255,255,255,.12);
  box-shadow:0 8px 24px -12px rgba(15,23,42,.7);
  backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px)
}
.stApp:has(.st-key-lobby) .nav-marca{
  display:flex;align-items:center;gap:.55rem;font-size:1.02rem;letter-spacing:-.025em
}
.stApp:has(.st-key-lobby) .st-key-nav-links{gap:6px}
.stApp:has(.st-key-lobby) .st-key-nav-links a{
  min-height:40px;padding:7px 13px !important;
  transition:background .18s ease,transform .18s ease,box-shadow .18s ease
}
.stApp:has(.st-key-lobby) .st-key-nav-links a:hover,
.stApp:has(.st-key-lobby) .st-key-nav-links a:focus-visible{
  background:rgba(255,255,255,.13) !important;transform:translateY(-1px);
  outline:2px solid rgba(167,243,208,.72);outline-offset:2px
}
.stApp:has(.st-key-lobby) .st-key-nav-on a{
  background:linear-gradient(135deg,rgba(16,185,129,.42),rgba(34,211,238,.25)) !important;
  box-shadow:inset 0 0 0 1px rgba(209,250,229,.24),0 5px 16px -12px rgba(52,211,153,.85)
}
.stApp:has(.st-key-lobby) .st-key-lobby-hero{
  position:relative;isolation:isolate;overflow:hidden;
  padding:clamp(24px,4.2vw,58px);
  border:1px solid rgba(255,255,255,.16);border-radius:30px;
  background:
    radial-gradient(900px 300px at 90% -20%,rgba(16,185,129,.45),transparent 60%),
    radial-gradient(700px 300px at 0% 0%,rgba(59,130,246,.45),transparent 60%),
    linear-gradient(160deg,#0b1230,#1e1b4b);
  box-shadow:0 18px 40px -20px rgba(15,23,42,.6)
}
.stApp:has(.st-key-lobby) .st-key-lobby-hero::before{
  position:absolute;inset:0;z-index:-1;content:"";pointer-events:none;opacity:.34;
  background-image:
    linear-gradient(rgba(220,255,250,.075) 1px,transparent 1px),
    linear-gradient(90deg,rgba(220,255,250,.075) 1px,transparent 1px);
  background-size:42px 42px;
  mask-image:radial-gradient(ellipse at 75% 48%,#000,transparent 75%)
}
.stApp:has(.st-key-lobby) .st-key-lobby-hero [data-testid="stHorizontalBlock"]{
  position:relative;z-index:1
}
.stApp:has(.st-key-lobby) .lobby-hero-copy{max-width:660px}
.stApp:has(.st-key-lobby) .lobby-eyebrow{
  display:inline-flex;align-items:center;gap:9px;margin-bottom:20px;
  color:#b8e4de;font-size:.73rem;font-weight:800;letter-spacing:.13em
}
.stApp:has(.st-key-lobby) .lobby-live-dot{
  width:9px;height:9px;border-radius:50%;background:#34d399;
  box-shadow:0 0 0 5px rgba(52,211,153,.14),0 0 18px rgba(52,211,153,.85)
}
.stApp:has(.st-key-lobby) .lobby-hero-copy h1{
  margin:0;color:#fff;font-size:clamp(2.7rem,5.2vw,4.7rem);
  font-weight:850;line-height:.99;letter-spacing:-.065em
}
.stApp:has(.st-key-lobby) .lobby-hero-copy h1 span{
  color:#75e3c1;text-shadow:0 8px 36px rgba(52,211,153,.2)
}
.stApp:has(.st-key-lobby) .lobby-hero-copy p{
  max-width:570px;margin:20px 0 24px;color:#d0e4e6;
  font-size:clamp(1rem,1.35vw,1.15rem);line-height:1.75
}
.stApp:has(.st-key-lobby) .st-key-lobby-hero-links{
  display:flex !important;align-items:stretch;gap:10px;max-width:520px
}
.stApp:has(.st-key-lobby) .st-key-lobby-hero-links > div{width:100% !important}
.stApp:has(.st-key-lobby) .st-key-lobby-hero-links a{
  min-height:48px;justify-content:center;padding:11px 16px !important;
  border:1px solid rgba(255,255,255,.18);border-radius:14px;
  background:rgba(255,255,255,.09);color:#f3fffd !important;font-weight:750;
  text-decoration:none;transition:transform .18s ease,background .18s ease,box-shadow .18s ease
}
.stApp:has(.st-key-lobby) .st-key-lobby-hero-links a:first-child{
  border-color:#38d9a8;background:linear-gradient(135deg,#087f68,#066d62);
  box-shadow:0 12px 28px -16px rgba(52,211,153,.85)
}
.stApp:has(.st-key-lobby) .st-key-lobby-hero-links a:hover{
  transform:translateY(-2px);background:rgba(255,255,255,.16);
  box-shadow:0 14px 28px -18px rgba(7,31,43,.75)
}
.stApp:has(.st-key-lobby) .st-key-lobby-hero-links a:first-child:hover{
  background:linear-gradient(135deg,#066d62,#05594f)
}
.stApp:has(.st-key-lobby) .st-key-lobby-hero-links a:focus-visible,
.stApp:has(.st-key-lobby) .st-key-lobby-card-casa a:focus-visible,
.stApp:has(.st-key-lobby) .st-key-lobby-card-ambiente a:focus-visible,
.stApp:has(.st-key-lobby) .st-key-lobby-card-factura a:focus-visible,
.stApp:has(.st-key-lobby) .st-key-lobby-card-analisis a:focus-visible{
  outline:3px solid #6ee7c0;outline-offset:3px
}
.stApp:has(.st-key-lobby) .lobby-trust{
  display:flex;align-items:center;gap:8px;margin-top:22px;
  color:#a9c9cc;font-size:.83rem;font-weight:600
}
.stApp:has(.st-key-lobby) .lobby-trust span{color:#7ce6c2}
.stApp:has(.st-key-lobby) .lobby-visual{
  position:relative;display:grid;min-height:320px;place-items:center;
  margin:4px auto;max-width:430px
}
.stApp:has(.st-key-lobby) .lobby-orbit{
  position:absolute;aspect-ratio:1;border:1px solid rgba(174,250,231,.2);
  border-radius:50%;box-shadow:0 0 38px rgba(45,212,191,.08),inset 0 0 34px rgba(45,212,191,.06)
}
.stApp:has(.st-key-lobby) .lobby-orbit-one{width:min(310px,75vw);animation:lobbyOrbit 24s linear infinite}
.stApp:has(.st-key-lobby) .lobby-orbit-two{
  width:min(240px,58vw);border-style:dashed;border-color:rgba(125,232,205,.27);
  animation:lobbyOrbit 32s linear infinite reverse
}
.stApp:has(.st-key-lobby) .lobby-orbit-one::before,
.stApp:has(.st-key-lobby) .lobby-orbit-two::after{
  position:absolute;width:10px;height:10px;content:"";border-radius:50%;
  background:#69e8c0;box-shadow:0 0 18px 5px rgba(52,211,153,.42)
}
.stApp:has(.st-key-lobby) .lobby-orbit-one::before{top:14%;right:19%}
.stApp:has(.st-key-lobby) .lobby-orbit-two::after{bottom:17%;left:10%;background:#65d8ed}
.stApp:has(.st-key-lobby) .lobby-energy-core{
  display:grid;width:154px;aspect-ratio:1;place-items:center;border:1px solid rgba(220,255,250,.3);
  border-radius:42px;background:linear-gradient(145deg,rgba(115,242,209,.2),rgba(34,211,238,.08));
  box-shadow:0 0 0 12px rgba(91,232,197,.045),0 0 90px rgba(45,212,191,.28),inset 0 0 36px rgba(220,255,250,.1);
  transform:rotate(-8deg);backdrop-filter:blur(12px)
}
.stApp:has(.st-key-lobby) .lobby-energy-core span{
  color:#b9ffeb;font-size:5.4rem;line-height:1;filter:drop-shadow(0 0 22px rgba(105,232,192,.8));
  animation:lobbyPulse 3.2s ease-in-out infinite
}
.stApp:has(.st-key-lobby) .lobby-float{
  position:absolute;display:flex;align-items:center;gap:9px;padding:10px 14px;
  border:1px solid rgba(220,255,250,.18);border-radius:13px;
  background:rgba(10,36,49,.68);color:#f1fffc;font-size:.8rem;font-weight:700;
  box-shadow:0 16px 38px -22px rgba(0,0,0,.8);backdrop-filter:blur(12px);
  animation:lobbyFloat 5.5s ease-in-out infinite
}
.stApp:has(.st-key-lobby) .lobby-float span{color:#71e4c1;font-size:1.1rem}
.stApp:has(.st-key-lobby) .lobby-float-top{top:12%;right:1%}
.stApp:has(.st-key-lobby) .lobby-float-bottom{bottom:16%;left:0;animation-delay:-2.5s}
.stApp:has(.st-key-lobby) .lobby-visual-caption{
  position:absolute;bottom:2%;color:rgba(220,248,243,.84);
  font-size:.65rem;font-weight:800;letter-spacing:.2em
}
@keyframes lobbyOrbit{to{transform:rotate(360deg)}}
@keyframes lobbyPulse{50%{transform:scale(1.08);filter:drop-shadow(0 0 32px rgba(105,232,192,1))}}
@keyframes lobbyFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
.stApp:has(.st-key-lobby) .lobby-section-heading{
  display:flex;align-items:flex-end;justify-content:space-between;gap:20px;
  margin:clamp(36px,5vw,62px) 2px 20px
}
.stApp:has(.st-key-lobby) .lobby-section-kicker{
  color:#07866f;font-size:.7rem;font-weight:850;letter-spacing:.15em
}
.stApp:has(.st-key-lobby) .lobby-section-heading h2{
  margin:7px 0 0;color:#153746;font-size:clamp(1.6rem,2.8vw,2.25rem);
  font-weight:820;letter-spacing:-.045em
}
.stApp:has(.st-key-lobby) .lobby-section-heading p{
  max-width:380px;margin:0;color:#475f6e;line-height:1.65
}
.stApp:has(.st-key-lobby) .st-key-lobby-card-casa,
.stApp:has(.st-key-lobby) .st-key-lobby-card-ambiente,
.stApp:has(.st-key-lobby) .st-key-lobby-card-factura,
.stApp:has(.st-key-lobby) .st-key-lobby-card-analisis{
  position:relative;isolation:isolate;overflow:hidden;
  min-height:270px;padding:clamp(23px,3vw,32px) !important;
  border:1px solid var(--card-border) !important;border-top:4px solid var(--card-accent) !important;
  border-radius:24px !important;
  background:
    radial-gradient(ellipse at 100% 0%,var(--card-glow),transparent 48%),
    linear-gradient(150deg,#fff 0%,var(--card-surface) 100%);
  box-shadow:0 16px 38px -26px rgba(14,42,73,.28);
  transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease,background .22s ease
}
.stApp:has(.st-key-lobby) .st-key-lobby-card-casa{
  --card-accent:#07866f;--card-border:#cce9df;--card-surface:#f1faf6;--card-glow:rgba(16,185,129,.13)
}
.stApp:has(.st-key-lobby) .st-key-lobby-card-ambiente{
  --card-accent:#087f9b;--card-border:#cce8ef;--card-surface:#f0f9fc;--card-glow:rgba(14,165,233,.14)
}
.stApp:has(.st-key-lobby) .st-key-lobby-card-factura{
  --card-accent:#a45113;--card-border:#f0ddca;--card-surface:#fff8f1;--card-glow:rgba(249,115,22,.12)
}
.stApp:has(.st-key-lobby) .st-key-lobby-card-analisis{
  --card-accent:#6351a8;--card-border:#e1daf2;--card-surface:#f7f5fc;--card-glow:rgba(139,92,246,.12)
}
.stApp:has(.st-key-lobby) .st-key-lobby-card-casa:hover,
.stApp:has(.st-key-lobby) .st-key-lobby-card-ambiente:hover,
.stApp:has(.st-key-lobby) .st-key-lobby-card-factura:hover,
.stApp:has(.st-key-lobby) .st-key-lobby-card-analisis:hover{
  transform:translateY(-5px);border-color:var(--card-border) !important;
  border-top-color:var(--card-accent) !important;
  box-shadow:0 24px 48px -28px rgba(14,42,73,.42)
}
.stApp:has(.st-key-lobby) .lobby-card-top{
  display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:25px
}
.stApp:has(.st-key-lobby) .lobby-card-icon{
  display:grid;width:60px;height:60px;place-items:center;
  border:1px solid var(--card-border);
  border-radius:20px;
  background:linear-gradient(145deg,var(--card-surface),#fff);
  color:var(--card-accent);font-size:2.1rem;font-weight:750;
  box-shadow:0 9px 22px -14px var(--card-accent),inset 0 1px rgba(255,255,255,.9);
  transition:transform .22s ease,box-shadow .22s ease,background .22s ease
}
.stApp:has(.st-key-lobby) .st-key-lobby-card-casa:hover .lobby-card-icon,
.stApp:has(.st-key-lobby) .st-key-lobby-card-ambiente:hover .lobby-card-icon,
.stApp:has(.st-key-lobby) .st-key-lobby-card-factura:hover .lobby-card-icon,
.stApp:has(.st-key-lobby) .st-key-lobby-card-analisis:hover .lobby-card-icon{
  transform:translateY(-2px) scale(1.04);box-shadow:0 12px 24px -13px var(--card-accent)
}
.stApp:has(.st-key-lobby) .lobby-card-index{
  color:#526874;font-size:.68rem;font-weight:850;letter-spacing:.13em
}
.stApp:has(.st-key-lobby) .st-key-lobby-card-casa h3,
.stApp:has(.st-key-lobby) .st-key-lobby-card-ambiente h3,
.stApp:has(.st-key-lobby) .st-key-lobby-card-factura h3,
.stApp:has(.st-key-lobby) .st-key-lobby-card-analisis h3{
  margin:0 0 10px;color:#102b46;font-size:1.45rem;font-weight:800;letter-spacing:-.035em
}
.stApp:has(.st-key-lobby) .st-key-lobby-card-casa p,
.stApp:has(.st-key-lobby) .st-key-lobby-card-ambiente p,
.stApp:has(.st-key-lobby) .st-key-lobby-card-factura p,
.stApp:has(.st-key-lobby) .st-key-lobby-card-analisis p{
  min-height:3.3em;margin:0 0 23px;color:#475f6e;font-size:.95rem;line-height:1.7
}
.stApp:has(.st-key-lobby) .st-key-lobby-card-casa a,
.stApp:has(.st-key-lobby) .st-key-lobby-card-ambiente a,
.stApp:has(.st-key-lobby) .st-key-lobby-card-factura a,
.stApp:has(.st-key-lobby) .st-key-lobby-card-analisis a{
  display:flex;align-items:center;justify-content:space-between;min-height:44px;
  padding:10px 14px !important;border:1px solid rgba(255,255,255,.2);
  border-radius:13px;background:linear-gradient(115deg,#102b46,#1e3d68);
  color:#fff !important;font-weight:750;text-decoration:none;
  box-shadow:0 8px 18px -14px rgba(15,35,67,.8);
  transition:background .18s ease,border-color .18s ease,color .18s ease,transform .18s ease
}
.stApp:has(.st-key-lobby) .st-key-lobby-card-casa a *,
.stApp:has(.st-key-lobby) .st-key-lobby-card-ambiente a *,
.stApp:has(.st-key-lobby) .st-key-lobby-card-factura a *,
.stApp:has(.st-key-lobby) .st-key-lobby-card-analisis a *{color:#fff !important}
.stApp:has(.st-key-lobby) .st-key-lobby-card-casa a:hover,
.stApp:has(.st-key-lobby) .st-key-lobby-card-ambiente a:hover,
.stApp:has(.st-key-lobby) .st-key-lobby-card-factura a:hover,
.stApp:has(.st-key-lobby) .st-key-lobby-card-analisis a:hover{
  transform:translateX(3px);border-color:var(--card-accent);
  background:linear-gradient(115deg,#173b64,#245384);color:#fff !important;
  box-shadow:0 10px 22px -14px var(--card-accent)
}
.stApp:has(.st-key-lobby) .lobby-footer{
  display:flex;align-items:center;gap:12px;margin-top:clamp(36px,5vw,60px);
  padding:18px 4px;border-top:1px solid #dce8e9;color:#526c76;font-size:.86rem;font-weight:650
}
.stApp:has(.st-key-lobby) .lobby-footer-mark{color:#07866f;font-size:1.25rem}
.stApp:has(.st-key-lobby) .lobby-footer-line{height:1px;flex:1;background:linear-gradient(90deg,#c7dcda,transparent)}
.stApp:has(.st-key-lobby) .lobby-footer-note{
  color:#526874;font-size:.63rem;font-weight:800;letter-spacing:.13em
}
@media (max-width:900px){
  .stApp:has(.st-key-lobby) .stMainBlockContainer{padding-left:1rem !important;padding-right:1rem !important}
  .stApp:has(.st-key-lobby) .st-key-lobby-hero{padding:30px}
  .stApp:has(.st-key-lobby) .lobby-visual{min-height:280px}
}
@media (max-width:640px){
  .stApp:has(.st-key-lobby) .stMainBlockContainer{padding:.75rem .75rem 2rem !important}
  .stApp:has(.st-key-lobby) .st-key-navbar{
    grid-template-columns:1fr;justify-items:center;row-gap:5px;padding:8px 7px;margin-bottom:1rem
  }
  .stApp:has(.st-key-lobby) .nav-marca{font-size:.98rem}
  .stApp:has(.st-key-lobby) .st-key-nav-links{gap:1px}
  .stApp:has(.st-key-lobby) .st-key-nav-links a{min-height:34px;padding:3px 6px !important}
  .stApp:has(.st-key-lobby) .st-key-nav-links a p{font-size:.78rem !important}
  .stApp:has(.st-key-lobby) .st-key-lobby-hero{padding:24px 19px;border-radius:22px}
  .stApp:has(.st-key-lobby) .lobby-eyebrow{margin-bottom:15px;font-size:.61rem;letter-spacing:.1em}
  .stApp:has(.st-key-lobby) .lobby-hero-copy h1{font-size:clamp(2.5rem,12vw,3.35rem)}
  .stApp:has(.st-key-lobby) .lobby-hero-copy p{margin:15px 0 19px;font-size:.95rem}
  .stApp:has(.st-key-lobby) .st-key-lobby-hero-links{flex-direction:column !important;gap:7px}
  .stApp:has(.st-key-lobby) .lobby-trust{margin-top:16px;font-size:.75rem}
  .stApp:has(.st-key-lobby) .lobby-visual{min-height:240px;margin:8px auto 0}
  .stApp:has(.st-key-lobby) .lobby-orbit-one{width:220px}
  .stApp:has(.st-key-lobby) .lobby-orbit-two{width:172px}
  .stApp:has(.st-key-lobby) .lobby-energy-core{width:116px;border-radius:32px}
  .stApp:has(.st-key-lobby) .lobby-energy-core span{font-size:4rem}
  .stApp:has(.st-key-lobby) .lobby-float{padding:8px 10px;font-size:.7rem}
  .stApp:has(.st-key-lobby) .lobby-float-top{top:5%;right:0}
  .stApp:has(.st-key-lobby) .lobby-float-bottom{bottom:12%;left:0}
  .stApp:has(.st-key-lobby) .lobby-visual-caption{bottom:0}
  .stApp:has(.st-key-lobby) .lobby-section-heading{display:block;margin:34px 3px 16px}
  .stApp:has(.st-key-lobby) .lobby-section-heading p{margin-top:8px;font-size:.89rem}
  .stApp:has(.st-key-lobby) .st-key-lobby-card-casa,
  .stApp:has(.st-key-lobby) .st-key-lobby-card-ambiente,
  .stApp:has(.st-key-lobby) .st-key-lobby-card-factura,
  .stApp:has(.st-key-lobby) .st-key-lobby-card-analisis{
    min-height:0;padding:20px !important;border-radius:18px !important
  }
  .stApp:has(.st-key-lobby) .lobby-card-top{margin-bottom:15px}
  .stApp:has(.st-key-lobby) .lobby-card-icon{width:46px;height:46px;border-radius:14px;font-size:1.7rem}
  .stApp:has(.st-key-lobby) .st-key-lobby-card-casa p,
  .stApp:has(.st-key-lobby) .st-key-lobby-card-ambiente p,
  .stApp:has(.st-key-lobby) .st-key-lobby-card-factura p,
  .stApp:has(.st-key-lobby) .st-key-lobby-card-analisis p{min-height:0;margin-bottom:16px}
  .stApp:has(.st-key-lobby) .lobby-footer{flex-wrap:wrap;font-size:.78rem}
  .stApp:has(.st-key-lobby) .lobby-footer-line{display:none}
  .stApp:has(.st-key-lobby) .lobby-footer-note{width:100%;margin-left:31px}
}
@media (prefers-reduced-motion:reduce){
  .stApp:has(.st-key-lobby) *,
  .stApp:has(.st-key-lobby) *::before,
  .stApp:has(.st-key-lobby) *::after{
    scroll-behavior:auto !important;animation-duration:.01ms !important;
    animation-iteration-count:1 !important;transition-duration:.01ms !important
  }
}

/* ---------- Igual en todas las pestañas: fondo, ancho y navbar con el estilo del Inicio ---------- */
.stApp{
  background:
    radial-gradient(ellipse at 4% 4%,rgba(16,185,129,.1),transparent 34rem),
    radial-gradient(ellipse at 95% 24%,rgba(34,211,238,.09),transparent 32rem),
    linear-gradient(180deg,#f7fafc 0%,#eef5f6 100%) !important;
  overflow-x:hidden
}
.stApp [data-testid="stAppViewContainer"],.stApp [data-testid="stMain"]{background:transparent !important}
.stApp .stMainBlockContainer{
  max-width:1420px !important;padding:1rem clamp(1rem,3vw,2.5rem) 3.5rem !important
}
.stApp .st-key-navbar{
  position:relative !important;top:auto !important;left:auto !important;right:auto !important;
  width:100% !important;margin:0 auto 1.4rem !important;
  grid-template-columns:1fr auto 1fr !important;padding:11px clamp(1rem,3vw,2.5rem) !important;
  background:linear-gradient(90deg,#0b1230,#1e1b4b) !important;
  border-bottom:1px solid rgba(255,255,255,.12) !important;
  box-shadow:0 8px 24px -12px rgba(15,23,42,.7) !important
}
.stApp .nav-marca{display:flex;align-items:center;gap:.55rem;font-size:1.02rem !important;letter-spacing:-.025em}
.stApp .st-key-nav-links{gap:6px !important}
.stApp .st-key-nav-links a{
  min-height:40px;padding:7px 13px !important;
  transition:background .18s ease,transform .18s ease,box-shadow .18s ease
}
.stApp .st-key-nav-links a:hover,.stApp .st-key-nav-links a:focus-visible{
  background:rgba(255,255,255,.13) !important;transform:translateY(-1px);
  outline:2px solid rgba(167,243,208,.72);outline-offset:2px
}
.stApp .st-key-nav-on a{
  background:linear-gradient(135deg,rgba(16,185,129,.42),rgba(34,211,238,.25)) !important;
  box-shadow:inset 0 0 0 1px rgba(209,250,229,.24),0 5px 16px -12px rgba(52,211,153,.85)
}
/* Recuadros: borde visible y menos separación entre bloques */
.stApp [data-testid="stMain"] .stVerticalBlock{gap:.75rem}
.stApp [data-testid="stMain"] [data-testid="stHorizontalBlock"]{gap:.85rem}
.stApp [data-testid="stExpander"] details{border-color:#a3b1c6 !important}

/* Ambiente 3D en tres partes que encajan al hacer scroll:
   1) navbar y resumen · 2) el simulador a pantalla completa · 3) artefactos y muebles */
.stApp .st-key-amb-pantalla{
  height:100vh;box-sizing:border-box;padding:12px 0 8px;gap:.6rem !important
}
.stApp .st-key-amb-abajo{padding-top:16px;min-height:100vh;box-sizing:border-box}
@media (max-width:640px){
  .stApp .st-key-amb-pantalla{height:auto}
}

/* El bloque principal de la página (el que contiene el navbar) nunca se dibuja como tarjeta. */
.stApp:has(.st-key-navbar) [data-testid="stMain"] .stVerticalBlock:has(.st-key-navbar){
  background:transparent !important;border:none !important;box-shadow:none !important;
  padding:0 !important;border-radius:0 !important;transform:none !important
}
@media (max-width:900px){
  .stApp .stMainBlockContainer{padding-left:1rem !important;padding-right:1rem !important}
}
@media (max-width:640px){
  .stApp .stMainBlockContainer{padding:.75rem .75rem 2rem !important}
  .stApp .st-key-navbar{
    grid-template-columns:1fr !important;justify-items:center;row-gap:5px;padding:8px 7px !important;
    margin-bottom:1rem !important
  }
  .stApp .nav-marca{font-size:.98rem !important}
  .stApp .st-key-nav-links{gap:1px !important}
  .stApp .st-key-nav-links a{min-height:34px;padding:3px 6px !important}
  .stApp .st-key-nav-links a p{font-size:.78rem !important}
}
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
    # Lo mismo que el paso 3 de Mi casa: la factura de EDEA del mes, con todos sus cargos e impuestos.
    costo = {k: r["costos"][k]["porMes"][m]["total"] for k in tar["escenarios"]}
    f = {"total": costo[esc]}
    sin = {"total": costo["sin_subsidio"]}
    fantasma = mm["pas"] + mm["base"]
    # Plata del consumo en espera: sus kWh × el mismo precio por kWh que usan las tarjetas.
    fantasma_pesos = fantasma * C.precio_kwh(tar, esc)["precio"]
    if esc == "sin_subsidio":
        otros = [(k, sin["total"] - costo[k]) for k in tar["escenarios"] if k != "sin_subsidio"]
        k_mejor, v = max(otros, key=lambda x: x[1]) if otros else ("", 0)
        ahorro_v = f"$ {fmt(v)}"
    else:
        ahorro_v = f"$ {fmt(sin['total'] - f['total'], 2)}"
    n = len(s["items"])
    vig = '/'.join(reversed(tar['vigencia_desde'].split('-'))) if tar.get('vigencia_desde') else ''
    mes_txt = MESES_LARGO[m]
    if esc == "sin_subsidio":
        # Se compara con el subsidio nacional (SEF), el más común.
        ref = "sef" if "sef" in tar["escenarios"] else k_mejor
        ahorro_v = f"$ {fmt(sin['total'] - costo[ref], 2)}"
        ahorro_lbl = "Si tuvieras subsidio nacional (SEF)"
        ahorro_sub = "pagarías esto menos en cada cuota"
    else:
        ahorro_lbl = "Lo que te ahorra tu subsidio"
        ahorro_sub = f"en cada cuota, con {tar['escenarios'][esc]['nombre'].lower()}"
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
        <div class="kpi g"><span>Electricidad en 2 meses</span><b>{fmt(2 * mm['total'])} <em>kWh</em></b>
          <small>{fmt(mm['total'])} kWh por cuota · suma de tus {n} electrodomésticos</small></div>
        <div class="kpi g acc"><span>Cada cuota de tu factura</span><b>$ {fmt(f['total'], 2)}</b>
          <small>2 cuotas iguales: $ {fmt(2 * round(f['total'], 2), 2)} cada 2 meses · con cargo fijo, tramo e
          impuestos</small></div>
        <div class="kpi"><span>{ahorro_lbl}</span><b>{ahorro_v}</b><small>{ahorro_sub}</small></div>
        <div class="kpi"><span>Gasto sin usar nada</span><b>$ {fmt(fantasma_pesos)}</b>
          <small>{fmt(fantasma)} kWh por cuota · equipos en espera y siempre enchufados</small></div>
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
   - EDEA lee el medidor **cada 2 meses** y lo cobra en **2 cuotas iguales**; cada cuota es la
     **factura de EDEA** de un mes de tu consumo: **cargo fijo** y precio por
     kWh según el **tramo** (R1 hasta 100 kWh, R2 hasta 200, R3 hasta 400…), **Cargo Transición
     Tarifaria**, subsidio si corresponde e **impuestos** (IVA 21 %, Ley 10740 18 % y tasas: unos
     54,5 % sin subsidio). El detalle renglón por renglón está en el paso 3 de *Mi casa*;
   - cada electrodoméstico vale sus kWh × el precio promedio del kWh (el de una casa típica de
     300 kWh, con impuestos), así **cambiar uno no cambia a los demás**.
4. **Subsidios.** Elegí tu situación arriba de todo en *Mi casa*: con el **subsidio nacional (SEF)**
   los primeros 150 kWh salen más baratos; con la **tarifa social provincial** bajan los cargos y
   hay un descuento fijo por mes. Las fuentes con sus links están en `datos/FUENTES.md`.
5. **Gasto sin usar nada.** Lo que consumen los equipos enchufados aunque estén apagados
   (la lucecita de la TV, el decodificador, el router) más el consumo de base de la casa, y lo que
   cuesta: esos kWh × el precio por kWh con impuestos.

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


# ---------- Detalle de la factura (paso 3 de Mi casa) ----------

FACTURA_CSS = """
<style>
.fac{border:1.5px solid #cbd5e1;border-radius:14px;overflow:hidden;font-size:.92rem;background:#fff;color:#0f172a}
.fac-head{display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap;
  background:#006b7d;color:#fff;padding:9px 14px;font-weight:700;letter-spacing:.02em}
.fac-head small{font-weight:500;opacity:.85}
.fac-sec{padding:8px 14px 2px;font-size:.72rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;
  color:#0e8fa3}
.fac-row{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:5px 14px;
  border-bottom:1px dotted #cbd5e1}
.fac-row small{display:block;color:#64748b;font-size:.78rem}
.fac-m{font-variant-numeric:tabular-nums;white-space:nowrap;text-align:right}
.fac-neg .fac-m{color:#059669}
.fac-sub{font-weight:800;border-bottom:none;border-top:1.5px solid #94a3b8;margin-top:2px}
.fac-total{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:10px 14px 12px;
  padding:10px 14px;border-radius:10px;background:#006b7d;color:#fff}
.fac-total b{font-size:1.35rem;font-variant-numeric:tabular-nums;white-space:nowrap}
</style>
"""


def _plata(v: float) -> str:
    return f"{'− ' if v < 0 else ''}$ {fmt(abs(v), 2)}"


def factura_detalle(det: dict, esc: dict) -> None:
    """La factura del mes con el estilo de la boleta de EDEA: cargos, impuestos y total."""
    f = det["factura"]
    filas = []
    for c in det["cargos"]:
        if "kwh" in c:
            sub = f"{fmt(c['kwh'], 1)} kWh × $ {fmt(c['precio'], 3)}"
        else:
            sub = c.get("detalle", "")
        clase = "fac-row fac-neg" if c["monto"] < 0 else "fac-row"
        filas.append(f"<div class='{clase}'><div>{html.escape(c['concepto'])}<small>{html.escape(sub)}</small></div>"
                     f"<div class='fac-m'>{_plata(c['monto'])}</div></div>")
    filas.append(f"<div class='fac-row fac-sub'><div>Subtotal energía</div><div class='fac-m'>{_plata(f['subtotal'])}</div></div>")
    filas.append("<div class='fac-sec'>Impuestos y tasas</div>")
    for i in det["impuestos"]:
        filas.append(f"<div class='fac-row'><div>{html.escape(i['concepto'])}<small>{fmt(i['pct'], 3).rstrip('0').rstrip(',')} %"
                     f" del subtotal</small></div><div class='fac-m'>{_plata(i['monto'])}</div></div>")
    filas.append(f"<div class='fac-row fac-sub'><div>Subtotal impuestos</div><div class='fac-m'>{_plata(f['impuestos'])}</div></div>")
    st.html(FACTURA_CSS + f"""
    <div class="fac">
      <div class="fac-head"><span>Conceptos</span>
        <small>{html.escape(esc['corto'])} · tramo {f['tramo']} · {fmt(f['kwh'], 1)} kWh</small></div>
      <div class="fac-sec">Energía</div>
      {''.join(filas)}
      <div class="fac-total"><span>TOTAL DE CADA CUOTA</span><b>{_plata(f['total'])}</b></div>
    </div>""")


# ---------- Boleta completa con el diseño de la factura modelo ----------
# Se usa para la factura de la casa (siempre) y para la escaneada (al lado, para comparar).

BOLETA_CSS = """
<style>
.bol-par{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:18px;align-items:start}
.bol-solo{max-width:900px;margin:0 auto}
.bol{container-type:inline-size;background:#fff;color:#333;border:1px solid #d6dbe1;border-top:5px solid var(--bol-c);
  border-radius:6px;box-shadow:0 0 12px rgba(0,0,0,.08);padding:20px 22px;font-family:Arial,Helvetica,sans-serif}
.bol-head{display:flex;gap:16px;justify-content:space-between;border-bottom:2px solid #ccc;padding-bottom:14px;
  margin-bottom:6px;flex-wrap:wrap}
.bol-logo{font-size:28px;font-weight:bold;color:var(--bol-c);letter-spacing:-1px;line-height:1.05}
.bol-logo small{display:block;font-size:11px;font-weight:normal;letter-spacing:0;color:#666;margin-top:6px}
.bol-info{flex:1;min-width:150px;font-size:11px;line-height:1.5;color:#333}
.bol-info b{font-size:12px}
.bol-pago{background:#006b7d;color:#fff;padding:12px 14px;min-width:200px;border-radius:4px;font-size:10.5px;
  text-transform:uppercase}
.bol-pago .v{display:block;font-size:15px;font-weight:bold;margin-bottom:6px;text-transform:none}
.bol-pago .tot{background:#fff;color:#000;font-size:19px;font-weight:bold;text-align:center;padding:5px 8px;
  margin-top:4px;text-transform:none;white-space:nowrap}
.bol-body{display:grid;grid-template-columns:1fr 1fr;gap:22px}
@container (max-width:640px){.bol-body{grid-template-columns:1fr;gap:0}}
.bol h4{font-size:13.5px;color:#006b7d;border-bottom:1px solid #ccc;padding-bottom:4px;margin:14px 0 8px;font-weight:bold}
.bol-dato{display:flex;justify-content:space-between;gap:8px;font-size:11.5px;margin-bottom:5px}
.bol-dato span:first-child{color:#666}
.bol-dato b{font-variant-numeric:tabular-nums}
.bol-graf{display:flex;align-items:flex-end;height:90px;gap:4px;margin:20px 0 22px;border-bottom:1px solid #000}
.bol-bar{flex:1;background:#d9d9d9;position:relative;min-height:2px}
.bol-bar.on{background:var(--bol-c)}
.bol-bar i{position:absolute;top:-14px;width:100%;text-align:center;font-size:8.5px;font-style:normal;color:#000}
.bol-bar em{position:absolute;bottom:-16px;width:100%;text-align:center;font-size:8.5px;font-style:normal;color:#666}
.bol-leg{font-size:10px;color:#666;line-height:1.5}
.bol table{width:100%;border-collapse:collapse;font-size:10.5px;margin-bottom:6px}
.bol th,.bol td{padding:4px 3px;border-bottom:1px solid #eee;text-align:right;font-variant-numeric:tabular-nums}
.bol th{background:#f9f9f9;color:#666;font-weight:normal}
.bol th:first-child,.bol td:first-child{text-align:left}
.bol ul{list-style:none;margin:0;padding:0;font-size:11px}
.bol li{display:flex;justify-content:space-between;gap:10px;padding:3px 0;border-bottom:1px dotted #e5e5e5}
.bol li small{display:block;color:#888;font-size:9.5px}
.bol li .m{white-space:nowrap;font-variant-numeric:tabular-nums;text-align:right}
.bol li.neg .m{color:#059669}
.bol li.sec{font-weight:bold;border-bottom:none;margin-top:8px}
.bol li.sub{font-weight:bold;border-top:1px solid #ccc;border-bottom:none;margin-top:4px;padding-top:5px}
.bol li.fin{font-size:14px;color:#000;border-top:2px solid #000;margin-top:10px;padding-top:6px;font-weight:bold}
.bol-total{background:#f0f0f0;border:1px solid #ccc;padding:10px;text-align:center;font-size:17px;font-weight:bold;
  margin-top:16px}
.bol-nota{font-size:10px;color:#666;text-align:center;margin-top:6px}
.bol-d{display:inline-block;margin-left:5px;padding:0 5px;border-radius:999px;font-size:9.5px;font-weight:bold;
  vertical-align:middle;font-family:Arial,sans-serif}
.bol-d.mas{background:#ffe4e6;color:#be123c}.bol-d.menos{background:#dcfce7;color:#047857}
.bol-d.igual{background:#e2e8f0;color:#334155}
</style>
"""


def _pct(p: float) -> str:
    return fmt(p, 3).rstrip("0").rstrip(",") + " %"


def _num(v: float, dec: int = 2) -> str:
    return f"{'-' if v < 0 else ''}{fmt(abs(v), dec)}"


def boleta_desde_detalle(det: dict, titulo: str, subtitulo: str, *, periodo: str = "", dias: float | None = None,
                         categoria: str = "", cuadro: str = "", vigencia: str = "",
                         historial: list | None = None, bimestre: tuple | None = None) -> dict:
    """Pasa calculo.detalle_factura() al formato de la boleta modelo.
    bimestre = (kWh, días) de la lectura completa: la boleta muestra una de sus 2 cuotas."""
    f = det["factura"]
    cargos = [{"concepto": c["concepto"],
               "sub": f"{fmt(c['kwh'], 1)} kWh × $ {fmt(c['precio'], 3)}" if "kwh" in c else c.get("detalle", ""),
               "monto": c["monto"]} for c in det["cargos"]]
    imps = [{"concepto": i["concepto"], "sub": _pct(i["pct"]), "monto": i["monto"]} for i in det["impuestos"]]
    precio = next((c for c in det["cargos"] if c["concepto"] == "Cargo variable"), {}).get("precio", 0)
    ctt = next((c for c in det["cargos"] if "Transición" in c["concepto"]), {}).get("precio", 0)
    tarifas = [{"desde": vigencia, "tramo": f["tramo"], "cf": f["cargo_fijo"], "cv": precio, "ctt": ctt,
                "kwh": f["kwh"], "dias": dias}]
    return {"titulo": titulo, "subtitulo": subtitulo, "periodo": periodo, "kwh": f["kwh"], "dias": dias,
            "tramo": f["tramo"], "categoria": categoria, "cuadro": cuadro, "tarifas": tarifas,
            "historial": historial or [], "cargos": cargos, "subtotal": f["subtotal"], "impuestos": imps,
            "subtotal_impuestos": f["impuestos"], "total": f["total"], "otros": [], "a_pagar": None,
            "bimestre": bimestre}


def boleta_desde_escaneo(leido: dict, kwh: float, titulo: str, subtitulo: str, *, periodo: str = "",
                         dias: float | None = None, categoria: str = "", cuadro: str = "",
                         a_pagar: float | None = None, bimestre: tuple | None = None) -> dict:
    """Pasa lo leído de la factura (factura.extraer()) al formato de la boleta modelo."""
    con = leido["conceptos"]

    def fila(r):
        sub = f"{fmt(r['kwh'], 0)} kWh" if "kwh" in r else (_pct(r["pct"]) if "pct" in r else "")
        return {"concepto": r["concepto"], "sub": sub, "monto": r["monto"]}  # tal como figura en la factura

    hist = leido.get("historial") or []
    return {"titulo": titulo, "subtitulo": subtitulo, "periodo": periodo, "kwh": kwh, "dias": dias, "tramo": None,
            "categoria": categoria, "cuadro": cuadro, "tarifas": leido.get("tarifas") or [],
            "historial": [(h["periodo"], h["kwh"], i == len(hist) - 1) for i, h in enumerate(hist)],
            "cargos": [fila(r) for r in con["cargos"]], "subtotal": con["subtotal"],
            "impuestos": [fila(r) for r in con["impuestos"] if abs(r["monto"]) > 0.004],
            "subtotal_impuestos": con["subtotal_impuestos"], "total": con["subtotal"] + con["subtotal_impuestos"],
            "otros": [fila(r) for r in con.get("otros", [])], "a_pagar": a_pagar, "bimestre": bimestre}


def _delta(v: float, ref: float | None) -> str:
    if ref is None or ref <= 0:
        return ""
    p = (v / ref - 1) * 100
    if abs(p) < 0.5:
        return "<span class='bol-d igual'>= igual</span>"
    return f"<span class='bol-d {'mas' if p > 0 else 'menos'}'>{'▲' if p > 0 else '▼'} {fmt(abs(p), 0)} %</span>"


def _boleta_html(b: dict, color: str, ref: dict | None = None) -> str:
    r = ref or {}
    esc = html.escape

    def lista(filas):
        return "".join(
            f"<li class='{'neg' if x['monto'] < 0 else ''}'><span>{esc(x['concepto'])}<small>{esc(x['sub'])}</small>"
            f"</span><span class='m'>{_num(x['monto'])}</span></li>" for x in filas)

    graf = ""
    if b["historial"]:
        tope = max(k for _, k, _ in b["historial"]) or 1
        graf = "<div class='bol-graf'>" + "".join(
            f"<div class='bol-bar{' on' if on else ''}' style='height:{k / tope * 100:.0f}%'>"
            f"<i>{fmt(k)}</i><em>{esc(et)}</em></div>" for et, k, on in b["historial"]) + "</div>"
    tarifas = "".join(
        f"<tr><td>{esc(str(t.get('desde') or ''))}</td><td>{esc(str(t.get('tramo') or ''))}</td>"
        f"<td>{fmt(t['cf'], 2)}</td><td>{fmt(t['cv'], 3)}</td>"
        f"<td>{fmt(t['ctt'], 3) if t.get('ctt') else '—'}</td>"
        f"<td>{fmt(t['kwh'], 0)}</td><td>{fmt(t['dias'], 0) if t.get('dias') else ''}</td></tr>" for t in b["tarifas"])
    otros = ""
    if b["otros"]:
        otros = ("<li class='sec'>• OTROS CONCEPTOS DE LA CUENTA</li>" + lista(b["otros"]) +
                 "<li><small>Mora, depósitos y gastos no dependen del consumo: quedan fuera de la comparación."
                 "</small></li>")
    diario = f"$ {fmt(b['total'] / b['dias'], 2)}" if b.get("dias") else "—"
    bim = b.get("bimestre")
    if bim:
        # Como la boleta de EDEA: lectura de dos meses, cobrada en dos cuotas iguales.
        cuota_pago = "Cuota<span class='v'>1 de 2</span>"
        consumos = (f"<div class='bol-dato'><span>Período de consumo</span><b>{fmt(bim[1], 0)} días</b></div>"
                    f"<div class='bol-dato'><span>Consumo del período</span><b>{fmt(bim[0], 1)} kWh</b></div>"
                    f"<div class='bol-dato'><span>Cuota 1 de 2 (la mitad)</span><b>{fmt(b['kwh'], 1)} kWh</b></div>"
                    f"<div class='bol-dato'><span>Total a facturar</span><b>{fmt(b['kwh'], 0)} kWh</b></div>")
    else:
        cuota_pago = ""
        consumos = (f"<div class='bol-dato'><span>Período de consumo</span>"
                    f"<b>{fmt(b['dias'], 0) if b.get('dias') else '—'} días</b></div>"
                    f"<div class='bol-dato'><span>Consumo</span><b>{fmt(b['kwh'], 1)} kWh</b></div>"
                    f"<div class='bol-dato'><span>Total a facturar</span><b>{fmt(b['kwh'], 0)} kWh</b></div>")
    pagar = (f"<div class='bol-nota'>Total a pagar impreso en la factura: <b>{_plata(b['a_pagar'])}</b></div>"
             if b.get("a_pagar") and abs(b["a_pagar"] - b["total"]) > 1 else "")
    return f"""
    <div class="bol" style="--bol-c:{color}">
      <div class="bol-head">
        <div class="bol-logo">{esc(b['titulo'])}<small>{esc(b['subtitulo'])}</small></div>
        <div class="bol-info"><div><b>TARIFA:</b> T1R residencial · <b>IVA:</b> CFI</div>
          <div><b>CATEGORÍA:</b> {esc(b['categoria'])}</div>
          <div><b>CUADRO TARIFARIO:</b> {esc(b['cuadro'])}</div></div>
        <div class="bol-pago">Período<span class="v">{esc(b['periodo']) or '—'}</span>{cuota_pago}
          Consumo<span class="v">{fmt(b['kwh'], 0)} kWh {_delta(b['kwh'], r.get('kwh'))}</span>
          Total a pagar<div class="tot">{_plata(b['total'])}</div></div>
      </div>
      <div class="bol-body">
        <div>
          <h4>Consumos registrados</h4>
          {consumos}
          <div class="bol-dato"><span>Gasto diario de electricidad</span><b>{diario}</b></div>
          {graf}
          <h4>Información para el usuario</h4>
          <div class="bol-leg">Categoría: {esc(b['categoria'])}<br>Cuadro tarifario: {esc(b['cuadro'])}<br>
            El cargo variable y el CTT se cobran por kWh; el cargo fijo, aunque no haya consumo.</div>
        </div>
        <div>
          <h4>Tarifas aplicadas</h4>
          <table><thead><tr><th>Desde</th><th>Tramo</th><th>C. fijo $/mes</th><th>C. var. $/kWh</th>
            <th>CTT $/kWh</th><th>kWh</th><th>Días</th></tr></thead><tbody>{tarifas}</tbody></table>
          <h4>Conceptos</h4>
          <ul>
            {lista(b['cargos'])}
            <li class="sub"><span>SUBTOTAL ENERGÍA</span><span class="m">{_num(b['subtotal'])}{_delta(b['subtotal'], r.get('subtotal'))}</span></li>
            <li class="sec">• IMPUESTOS Y TASAS (sobre $ {fmt(b['subtotal'], 2)})</li>
            {lista(b['impuestos'])}
            <li class="sub"><span>SUBTOTAL IMPUESTOS</span><span class="m">{_num(b['subtotal_impuestos'])}{_delta(b['subtotal_impuestos'], r.get('subtotal_impuestos'))}</span></li>
            <li class="fin"><span>TOTAL FACTURA</span><span class="m">{_num(b['total'])}</span></li>
            {otros}
          </ul>
        </div>
      </div>
      <div class="bol-total">TOTAL A PAGAR: {_plata(b['total'])} {_delta(b['total'], r.get('total'))}</div>
      {pagar}
    </div>"""


def boleta_sola(b: dict) -> None:
    """La factura de la casa, grande, con el diseño de la factura modelo."""
    st.html(BOLETA_CSS + "<div class='bol-solo'>" + _boleta_html(b, "#7c3aed") + "</div>")


def boletas_lado_a_lado(factura: dict, casa: dict) -> None:
    """La factura escaneada a la izquierda y la de la casa a la derecha (una debajo de la otra en el
    celular). En la de la casa, cada diferencia se marca contra la factura."""
    st.html(BOLETA_CSS + "<div class='bol-par'>" + _boleta_html(factura, "#008f5a") +
            _boleta_html(casa, "#7c3aed", factura) + "</div>")
