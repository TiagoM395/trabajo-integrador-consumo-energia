"""Gráficos Plotly del simulador. Toman los resultados de calculo.simular()."""
from __future__ import annotations

import plotly.graph_objects as go

from simulador.estado import COLOR, COLOR_CAT, MESES, MESES_LARGO, fmt, hhmm

ESC_COLOR = {"sin_subsidio": "#e11d48", "sef": "#2563eb", "tarifa_social": "#7c3aed", "tarifa_social_sef": "#059669",
             "social_nacional": "#2563eb", "social_provincial": "#7c3aed"}
FUENTE = "Plus Jakarta Sans, system-ui, sans-serif"


def _base(fig: go.Figure, alto: int = 320, leyenda: bool = True) -> go.Figure:
    fig.update_layout(
        height=alto, margin=dict(l=8, r=8, t=10, b=8), font=dict(family=FUENTE, size=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", hoverlabel=dict(font_family=FUENTE),
        showlegend=leyenda, legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        bargap=0.28, dragmode=False,
    )
    fig.update_xaxes(showgrid=False, fixedrange=True)
    fig.update_yaxes(gridcolor="rgba(127,127,127,.18)", zeroline=False, fixedrange=True)
    return fig


def meses(r: dict, sel: int, tope: float | None, costo: list[float]) -> go.Figure:
    """Barras apiladas activo / standby / base, con rango ±25 % y línea de tope."""
    ms = r["meses"]
    fig = go.Figure()
    capas = [("base", "Base de la casa"), ("pas", "Standby"), ("act", "Activo")]
    for k, nombre in capas:
        fig.add_bar(
            x=MESES, y=[m[k] for m in ms], name=nombre, marker_color=COLOR[k],
            marker_line_width=0,
            customdata=[[MESES_LARGO[i], m["total"], m["min"], m["max"], costo[i]] for i, m in enumerate(ms)],
            hovertemplate="<b>%{customdata[0]}</b><br>" + nombre + ": %{y:.1f} kWh<br>"
                          "Total %{customdata[1]:.1f} kWh (rango %{customdata[2]:.0f}–%{customdata[3]:.0f})"
                          "<br>$ %{customdata[4]:,.0f}<extra></extra>",
            selectedpoints=[sel], unselected=dict(marker=dict(opacity=0.38)),
        )
    fig.add_scatter(
        x=MESES, y=[m["total"] for m in ms], mode="markers", name="Rango ±25 %",
        marker=dict(size=1, color="rgba(0,0,0,0)"), hoverinfo="skip",
        error_y=dict(type="data", symmetric=False, array=[m["max"] - m["total"] for m in ms],
                     arrayminus=[m["total"] - m["min"] for m in ms], color="rgba(100,116,139,.8)", thickness=1.4, width=5),
    )
    if tope:
        fig.add_hline(y=tope, line=dict(color=ESC_COLOR["social_nacional"], dash="dash", width=2),
                      annotation_text=f"Tope bonificado {fmt(tope)} kWh", annotation_position="top left",
                      annotation_font_color=ESC_COLOR["social_nacional"])
    fig.update_layout(barmode="stack", yaxis_title="kWh", clickmode="event+select")
    return _base(fig, 330)


def dona(act: float, pas: float, base: float, mes_txt: str) -> go.Figure:
    total = act + pas + base
    fig = go.Figure(go.Pie(
        labels=["Activo", "Standby", "Base"], values=[act, pas, base], hole=0.68, sort=False,
        marker=dict(colors=[COLOR["act"], COLOR["pas"], COLOR["base"]], line=dict(width=0)),
        textinfo="none", hovertemplate="<b>%{label}</b><br>%{value:.1f} kWh · %{percent}<extra></extra>",
    ))
    fig.add_annotation(text=f"<b style='font-size:24px'>{fmt(total)}</b><br>kWh en {mes_txt}", showarrow=False, font=dict(size=12))
    return _base(fig, 220, leyenda=False)


def curva(curva_dia: dict, items: list[dict], hora: float) -> go.Figure:
    """Curva de carga de 24 h apilada por artefacto."""
    x = list(range(24))
    etiquetas = [f"{hhmm(h)}–{hhmm(h + 1)}" for h in x]
    fig = go.Figure()
    fig.add_scatter(x=x, y=[v * 1000 for v in curva_dia["base"]], name="🏠 Base", stackgroup="a",
                    line=dict(width=0, shape="hv", color=COLOR["base"]), customdata=etiquetas,
                    hovertemplate="%{customdata}<br>Base: %{y:.0f} W<extra></extra>")
    orden = sorted(zip(curva_dia["series"], items), key=lambda p: -sum(p[0]["valores"]))
    for serie, inst in orden:
        if not any(serie["valores"]):
            continue
        fig.add_scatter(
            x=x, y=[v * 1000 for v in serie["valores"]], name=f"{inst['icono']} {inst['nombre']}", stackgroup="a",
            line=dict(width=0, shape="hv", color=COLOR_CAT[inst["cat"]]), customdata=etiquetas,
            hovertemplate="%{customdata}<br>" + inst["nombre"] + ": %{y:.0f} W<extra></extra>",
        )
    fig.add_scatter(x=x, y=[v * 1000 for v in curva_dia["total"]], name="Total", mode="lines",
                    line=dict(color="rgba(15,23,42,.75)", width=2, shape="hv"), customdata=etiquetas,
                    hovertemplate="%{customdata}<br><b>Total %{y:.0f} W</b><extra></extra>")
    fig.add_vrect(x0=0, x1=7, fillcolor="rgba(30,27,75,.07)", line_width=0)
    fig.add_vrect(x0=20, x1=24, fillcolor="rgba(30,27,75,.07)", line_width=0)
    fig.add_vline(x=hora, line=dict(color="#3b82f6", width=2))
    fig.update_xaxes(tickvals=list(range(0, 25, 3)), ticktext=[f"{h:02d}h" for h in range(0, 25, 3)], range=[0, 24])
    fig.update_layout(yaxis_title="W (potencia media)", hovermode="x unified")
    return _base(fig, 380, leyenda=False)


def agenda(items: list[dict], ventanas, hora: float) -> go.Figure:
    """Agenda del día: bloques de uso (verde) y standby (naranja) por artefacto."""
    fig = go.Figure()
    nombres = [f"{i['icono']} {i['nombre']}" for i in items]

    def segmentos(ini, largo):
        if largo <= 0:
            return []
        if largo >= 24:
            return [(0, 24)]
        s = ini % 24
        return [(s, largo)] if s + largo <= 24 else [(s, 24 - s), (0, s + largo - 24)]

    for tipo, color, nombre in (("conn", "rgba(249,115,22,.45)", "Standby / enchufado"), ("uso", COLOR["act"], "En uso")):
        ys, xs, bases, txt = [], [], [], []
        for inst, n in zip(items, nombres):
            if inst["modo"] in ("anual", "siempre"):
                if tipo == "uso":
                    ys.append(n); xs.append(24); bases.append(0); txt.append("todo el día")
                continue
            v = ventanas(inst)[tipo]
            for s, l in segmentos(*v):
                ys.append(n); xs.append(l); bases.append(s); txt.append(f"{hhmm(s)} → {hhmm(s + l)}")
        fig.add_bar(y=ys, x=xs, base=bases, orientation="h", name=nombre, marker_color=color,
                    marker_line_width=0, customdata=txt, hovertemplate="%{y}<br>%{customdata}<extra>" + nombre + "</extra>")
    fig.add_vline(x=hora, line=dict(color="#3b82f6", width=2))
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(range=[0, 24], tickvals=list(range(0, 25, 3)), ticktext=[f"{h:02d}h" for h in range(0, 25, 3)])
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
    return _base(fig, max(220, 34 * len(items) + 70))


def costo_consumo(tarifas: dict, kwh: float, sel: str, factura) -> go.Figure:
    """Costo mensual según el consumo para cada escenario. Se calcula kWh por kWh, así se ven los
    saltos de tramo de la tarifa real."""
    xmax = int(max(kwh * 1.6, 450))
    xs = list(range(0, xmax + 1, 2))
    fig = go.Figure()
    for esc_id, e in tarifas["escenarios"].items():
        fig.add_scatter(
            x=xs, y=[factura(x, tarifas, esc_id)["total"] for x in xs], mode="lines", name=e["corto"],
            line=dict(color=ESC_COLOR.get(esc_id, "#888"), width=5 if esc_id == sel else 2.5),
            opacity=1 if esc_id == sel else 0.55, hovertemplate="%{x:.0f} kWh → $ %{y:,.0f}<extra>" + e["corto"] + "</extra>",
        )
        f = factura(kwh, tarifas, esc_id)
        fig.add_scatter(x=[kwh], y=[f["total"]], mode="markers", showlegend=False,
                        marker=dict(size=13, color=ESC_COLOR.get(esc_id, "#888"), line=dict(width=3, color="white")),
                        hovertemplate=f"<b>{e['nombre']}</b><br>{fmt(kwh)} kWh → $ {fmt(f['total'])}"
                                      f"<br>{fmt(f['efectivo'], 1)} $/kWh efectivo<extra></extra>")
    fig.add_vline(x=kwh, line=dict(color="#3b82f6", width=2, dash="dot"),
                  annotation_text=f"Tu consumo: {fmt(kwh)} kWh", annotation_position="top right")
    fig.update_layout(xaxis_title="kWh por mes", yaxis_title="$ por mes", yaxis_tickformat=",.0f")
    return _base(fig, 340)


def meta_diaria(r: dict, meta: float) -> go.Figure:
    prom = [m["total"] / m["dias"] for m in r["meses"]]
    fig = go.Figure(go.Bar(
        x=MESES, y=prom, marker_color=["#e11d48" if v > meta else COLOR["act"] for v in prom], marker_line_width=0,
        hovertemplate="%{x}: %{y:.1f} kWh/día<extra></extra>",
    ))
    fig.add_hline(y=meta, line=dict(color="#0f172a", dash="dash", width=2),
                  annotation_text=f"meta {fmt(meta, 1)} kWh/día", annotation_position="top left")
    fig.update_layout(yaxis_title="kWh/día promedio")
    return _base(fig, 260, leyenda=False)
