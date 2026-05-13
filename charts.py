"""charts.py – Plotly chart builders with the dark-purple theme."""

from __future__ import annotations

import plotly.graph_objects as go

from models import Holding, HistoricalPoint, PortfolioMetrics
from config import (
    CHART_HEIGHT, CHART_TEMPLATE, CHART_PAPER_BG, CHART_PLOT_BG,
    COLOR_PROFIT, COLOR_LOSS, COLOR_NEUTRAL, COLOR_ACCENT,
    COLOR_ACCENT2, COLOR_ACCENT3, COLOR_BORDER, SECTOR_COLORS,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_CARD,
)

_FONT = dict(family="'DM Sans', 'Segoe UI', sans-serif", size=12, color=COLOR_TEXT_SECONDARY)


def _base_layout(**kwargs) -> dict:
    layout: dict = {
        "template":       CHART_TEMPLATE,
        "paper_bgcolor":  CHART_PAPER_BG,
        "plot_bgcolor":   CHART_PLOT_BG,
        "margin":         dict(l=24, r=24, t=44, b=24),
        "font":           _FONT,
        "title_font":     dict(family="'DM Sans', sans-serif", size=14, color=COLOR_TEXT_PRIMARY),
        "legend":         dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=COLOR_BORDER,
            font=dict(color=COLOR_TEXT_SECONDARY),
        ),
    }
    layout.update(kwargs)
    layout.setdefault("height", CHART_HEIGHT)
    return layout


def _pnl_color(v: float) -> str:
    return COLOR_PROFIT if v >= 0 else COLOR_LOSS


def _axis(title: str = "", **kw) -> dict:
    return dict(
        title=dict(text=title, font=dict(color=COLOR_TEXT_SECONDARY)),
        gridcolor="rgba(110,90,190,0.12)",
        zerolinecolor="rgba(110,90,190,0.25)",
        tickfont=dict(color=COLOR_TEXT_SECONDARY),
        **kw,
    )


# ── Invested vs Current Value ─────────────────────────────────────────────────
def portfolio_value_bar(metrics: PortfolioMetrics) -> go.Figure:
    color = _pnl_color(metrics.total_pnl)
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Invested",
        x=[metrics.total_invested], y=["Portfolio"],
        orientation="h",
        marker=dict(color=COLOR_NEUTRAL, opacity=0.75, line=dict(width=0)),
        text=[f"₹{metrics.total_invested:,.0f}"],
        textposition="auto",
        textfont=dict(color=COLOR_TEXT_PRIMARY, size=13),
    ))
    fig.add_trace(go.Bar(
        name="Current Value",
        x=[metrics.current_value], y=["Portfolio"],
        orientation="h",
        marker=dict(
            color=color, opacity=0.9,
            line=dict(width=0),
        ),
        text=[f"₹{metrics.current_value:,.0f}"],
        textposition="auto",
        textfont=dict(color=COLOR_TEXT_PRIMARY, size=13),
    ))

    layout = _base_layout(title="Invested vs Current Value", barmode="group")
    layout["legend"].update(orientation="h", yanchor="bottom", y=1.02)
    fig.update_layout(**layout, xaxis=_axis("Amount (₹)"), yaxis=_axis())
    return fig


# ── P&L by Holding ────────────────────────────────────────────────────────────
def holdings_pnl_bar(holdings: list[Holding]) -> go.Figure:
    sh = sorted(holdings, key=lambda h: h.pnl)
    tickers = [h.ticker for h in sh]
    pnls    = [h.pnl for h in sh]
    colors  = [_pnl_color(p) for p in pnls]

    fig = go.Figure(go.Bar(
        x=pnls, y=tickers, orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[f"₹{p:,.0f}" for p in pnls],
        textposition="auto",
        textfont=dict(color=COLOR_TEXT_PRIMARY),
    ))
    fig.update_layout(**_base_layout(title="P&L by Holding"),
                      xaxis=_axis("Profit / Loss (₹)"), yaxis=_axis())
    return fig


# ── Return % by Holding ───────────────────────────────────────────────────────
def holdings_pnl_pct_bar(holdings: list[Holding]) -> go.Figure:
    sh     = sorted(holdings, key=lambda h: h.pnl_pct)
    tickers = [h.ticker for h in sh]
    pcts    = [h.pnl_pct for h in sh]
    colors  = [_pnl_color(p) for p in pcts]

    fig = go.Figure(go.Bar(
        x=pcts, y=tickers, orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[f"{p:.1f}%" for p in pcts],
        textposition="auto",
        textfont=dict(color=COLOR_TEXT_PRIMARY),
    ))
    fig.update_layout(**_base_layout(title="Return % by Holding"),
                      xaxis=_axis("Return (%)"), yaxis=_axis())
    return fig


# ── Sector Pie ────────────────────────────────────────────────────────────────
def sector_pie_chart(metrics: PortfolioMetrics) -> go.Figure:
    labels = list(metrics.sector_allocation.keys())
    values = list(metrics.sector_allocation.values())

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.52,
        marker=dict(
            colors=SECTOR_COLORS[:len(labels)],
            line=dict(color=CHART_PAPER_BG, width=2),
        ),
        textinfo="label+percent",
        textfont=dict(color=COLOR_TEXT_PRIMARY, size=11),
        hovertemplate="%{label}<br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(**_base_layout(title="Sector Allocation"))
    return fig


# ── Portfolio Weight Bar ──────────────────────────────────────────────────────
def holding_weight_bar(holdings: list[Holding]) -> go.Figure:
    total = sum(h.current_value for h in holdings) or 1
    sh    = sorted(holdings, key=lambda h: h.current_value, reverse=True)
    tickers = [h.ticker for h in sh]
    weights = [(h.current_value / total * 100) for h in sh]

    fig = go.Figure(go.Bar(
        x=tickers, y=weights,
        marker=dict(
            color=SECTOR_COLORS[:len(tickers)],
            opacity=0.85,
            line=dict(width=0),
        ),
        text=[f"{w:.1f}%" for w in weights],
        textposition="outside",
        textfont=dict(color=COLOR_TEXT_PRIMARY),
    ))
    fig.update_layout(**_base_layout(title="Portfolio Weight by Stock"),
                      yaxis=_axis("Weight (%)"), xaxis=_axis("Ticker"))
    return fig


# ── Portfolio History Line ────────────────────────────────────────────────────
def portfolio_history_line(history: list[HistoricalPoint]) -> go.Figure:
    dates  = [p.date for p in history]
    values = [p.value for p in history]
    gain   = (values[-1] >= values[0]) if values else True
    lcolor = COLOR_PROFIT if gain else COLOR_LOSS

    fig = go.Figure(go.Scatter(
        x=dates, y=values,
        mode="lines",
        line=dict(color=lcolor, width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor=f"rgba({_hex_rgb(lcolor)}, 0.10)",
        hovertemplate="Date: %{x}<br>Value: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title="Portfolio Value Over Time"),
        xaxis=_axis("Date", showgrid=False),
        yaxis=_axis("Portfolio Value (₹)"),
    )
    return fig


# ── Daily Returns Bar ─────────────────────────────────────────────────────────
def daily_returns_bar(history: list[HistoricalPoint]) -> go.Figure:
    if len(history) < 2:
        return go.Figure()

    dates   = [p.date for p in history[1:]]
    returns = [
        ((history[i].value - history[i - 1].value) / history[i - 1].value) * 100
        for i in range(1, len(history))
    ]
    colors = [COLOR_PROFIT if r >= 0 else COLOR_LOSS for r in returns]

    fig = go.Figure(go.Bar(
        x=dates, y=returns,
        marker=dict(color=colors, opacity=0.8, line=dict(width=0)),
        hovertemplate="Date: %{x}<br>Return: %{y:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title="Daily Returns (%)"),
        yaxis=_axis("Daily Return (%)"),
        xaxis=_axis("Date", showgrid=False),
    )
    return fig


# ── Beta Comparison Bar ───────────────────────────────────────────────────────
def beta_comparison_bar(holdings: list[Holding]) -> go.Figure:
    sh      = sorted(holdings, key=lambda h: h.beta, reverse=True)
    tickers = [h.ticker for h in sh]
    betas   = [h.beta for h in sh]
    colors  = [
        COLOR_LOSS if b > 1.2 else COLOR_PROFIT if b < 0.8 else COLOR_ACCENT
        for b in betas
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=tickers, y=betas,
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[f"{b:.2f}" for b in betas],
        textposition="outside",
        textfont=dict(color=COLOR_TEXT_PRIMARY),
        name="Beta",
    ))
    fig.add_hline(
        y=1.0, line_dash="dash", line_color=COLOR_NEUTRAL,
        annotation_text="Market β = 1",
        annotation_position="top right",
        annotation_font_color=COLOR_TEXT_SECONDARY,
    )
    fig.update_layout(
        **_base_layout(title="Beta Comparison (Market Sensitivity)"),
        yaxis=_axis("Beta"), xaxis=_axis("Ticker"),
    )
    return fig


# ── Risk Gauge ────────────────────────────────────────────────────────────────
def risk_gauge(risk_score: float) -> go.Figure:
    color = (
        COLOR_PROFIT  if risk_score <= 30
        else COLOR_ACCENT if risk_score <= 60
        else COLOR_LOSS
    )
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={"text": "Risk Score", "font": {"size": 15, "color": COLOR_TEXT_PRIMARY}},
        number={"font": {"size": 36, "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": COLOR_TEXT_SECONDARY,
                     "tickfont": {"color": COLOR_TEXT_SECONDARY}},
            "bar":  {"color": color, "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30],  "color": "rgba(0,229,160,0.12)"},
                {"range": [30, 60], "color": "rgba(167,139,250,0.12)"},
                {"range": [60, 80], "color": "rgba(245,158,11,0.12)"},
                {"range": [80, 100],"color": "rgba(255,79,123,0.12)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.75, "value": risk_score,
            },
        },
    ))
    fig.update_layout(**_base_layout())
    fig.update_layout(height=280)
    return fig


# ── Sector Risk Bubble ────────────────────────────────────────────────────────
def sector_risk_bubble(holdings: list[Holding]) -> go.Figure:
    total = sum(h.current_value for h in holdings) or 1
    sectors = sorted({h.sector for h in holdings})
    sector_color_map = {s: SECTOR_COLORS[i % len(SECTOR_COLORS)] for i, s in enumerate(sectors)}

    fig = go.Figure()
    for sector in sectors:
        grp = [h for h in holdings if h.sector == sector]
        fig.add_trace(go.Scatter(
            x=[h.beta for h in grp],
            y=[h.pnl_pct for h in grp],
            mode="markers+text",
            name=sector,
            text=[h.ticker for h in grp],
            textposition="top center",
            textfont=dict(color=COLOR_TEXT_PRIMARY, size=11),
            marker=dict(
                size=[(h.current_value / total) * 500 + 12 for h in grp],
                color=sector_color_map[sector],
                opacity=0.80,
                line=dict(width=1.5, color="rgba(255,255,255,0.2)"),
            ),
            hovertemplate="<b>%{text}</b><br>Beta: %{x:.2f}<br>Return: %{y:.1f}%<extra></extra>",
        ))

    fig.add_vline(x=1.0, line_dash="dash", line_color=COLOR_NEUTRAL,
                  annotation_text="β=1", annotation_position="top right",
                  annotation_font_color=COLOR_TEXT_SECONDARY)
    fig.add_hline(y=0, line_dash="dash", line_color=COLOR_NEUTRAL,
                  annotation_text="Break-even", annotation_position="bottom right",
                  annotation_font_color=COLOR_TEXT_SECONDARY)
    fig.update_layout(
        **_base_layout(title="Risk vs Return Bubble Chart"),
        xaxis=_axis("Beta (Market Sensitivity)"),
        yaxis=_axis("Return (%)"),
    )
    return fig


# ── Drawdown Chart ────────────────────────────────────────────────────────────
def drawdown_chart(history: list[HistoricalPoint]) -> go.Figure:
    if len(history) < 2:
        return go.Figure()

    values = [p.value for p in history]
    dates  = [p.date  for p in history]
    peak   = values[0]
    drawdowns = []
    for v in values:
        peak = max(peak, v)
        dd = ((v - peak) / peak * 100) if peak else 0
        drawdowns.append(round(dd, 3))

    fig = go.Figure(go.Scatter(
        x=dates, y=drawdowns,
        mode="lines",
        line=dict(color=COLOR_LOSS, width=2, shape="spline"),
        fill="tozeroy",
        fillcolor=f"rgba({_hex_rgb(COLOR_LOSS)}, 0.12)",
        hovertemplate="Date: %{x}<br>Drawdown: %{y:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title="Drawdown (%)"),
        xaxis=_axis("Date", showgrid=False),
        yaxis=_axis("Drawdown (%)"),
    )
    return fig


# ── Dividend Bar ──────────────────────────────────────────────────────────────
def dividend_bar(holdings: list[Holding]) -> go.Figure:
    sh  = sorted(holdings, key=lambda h: h.annual_dividend, reverse=True)
    sh  = [h for h in sh if h.annual_dividend > 0]
    if not sh:
        return go.Figure()

    fig = go.Figure(go.Bar(
        x=[h.ticker for h in sh],
        y=[h.annual_dividend for h in sh],
        marker=dict(
            color=SECTOR_COLORS[:len(sh)], opacity=0.85, line=dict(width=0),
        ),
        text=[f"₹{h.annual_dividend:,.0f}" for h in sh],
        textposition="outside",
        textfont=dict(color=COLOR_TEXT_PRIMARY),
    ))
    fig.update_layout(
        **_base_layout(title="Projected Annual Dividends by Stock"),
        yaxis=_axis("Annual Dividend (₹)"),
        xaxis=_axis("Ticker"),
    )
    return fig


# ── Cumulative Return Line ────────────────────────────────────────────────────
def cumulative_return_line(history: list[HistoricalPoint]) -> go.Figure:
    if len(history) < 2:
        return go.Figure()

    base   = history[0].value or 1
    dates  = [p.date for p in history]
    cumret = [((p.value - base) / base) * 100 for p in history]
    gain   = cumret[-1] >= 0
    lcolor = COLOR_PROFIT if gain else COLOR_LOSS

    fig = go.Figure(go.Scatter(
        x=dates, y=cumret,
        mode="lines",
        line=dict(color=lcolor, width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor=f"rgba({_hex_rgb(lcolor)}, 0.10)",
        hovertemplate="Date: %{x}<br>Cum Return: %{y:.2f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color=COLOR_NEUTRAL)
    fig.update_layout(
        **_base_layout(title="Cumulative Return (%)"),
        xaxis=_axis("Date", showgrid=False),
        yaxis=_axis("Cumulative Return (%)"),
    )
    return fig


# ── Helpers ───────────────────────────────────────────────────────────────────
def _hex_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"{int(h[0:2],16)}, {int(h[2:4],16)}, {int(h[4:6],16)}"
