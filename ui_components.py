"""
ui_components.py – Streamlit UI rendering with a dark-purple glass theme.
All st.* calls live here. No calculations – pure presentation.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from models import Holding, PortfolioMetrics, HistoricalPoint
import charts
from config import APP_CURRENCY_SYMBOL


# ─────────────────────────────────────────────────────────────────────────────
#  CSS Injection
# ─────────────────────────────────────────────────────────────────────────────

def inject_custom_css() -> None:
    st.markdown("""
<style>
/* ── Google Font ─────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

/* ── Root variables ──────────────────────────────────────────── */
:root {
  --bg:           #0D0B14;
  --surface:      #13101F;
  --card:         #1C1830;
  --card-hover:   #231E3D;
  --border:       #2E2855;
  --border-glow:  rgba(167,139,250,0.35);
  --accent:       #A78BFA;
  --accent2:      #C084FC;
  --profit:       #00E5A0;
  --loss:         #FF4F7B;
  --neutral:      #7B7FA6;
  --text:         #EDE9FF;
  --text-muted:   #9D94C4;
  --text-dim:     #5C5480;
}

/* ── App shell ───────────────────────────────────────────────── */
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar ─────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-muted) !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong { color: var(--text) !important; }
[data-testid="stSidebar"] .stButton button {
    background: rgba(167,139,250,0.12) !important;
    border: 1px solid var(--border) !important;
    color: var(--accent) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all .2s !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(167,139,250,0.22) !important;
    border-color: var(--accent) !important;
}

/* ── Main buttons ────────────────────────────────────────────── */
.stButton button {
    background: linear-gradient(135deg, rgba(167,139,250,0.18), rgba(192,132,252,0.12)) !important;
    border: 1px solid var(--border) !important;
    color: var(--accent) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all .2s !important;
}
.stButton button:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 0 16px rgba(167,139,250,0.25) !important;
}

/* ── Metric cards ─────────────────────────────────────────────── */
.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px 16px;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
    transition: border-color .2s, box-shadow .2s;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    opacity: 0;
    transition: opacity .2s;
}
.metric-card:hover { border-color: var(--border-glow); box-shadow: 0 0 18px rgba(167,139,250,.15); }
.metric-card:hover::before { opacity: 1; }

.metric-label {
    color: var(--text-dim);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: .09em;
    font-weight: 600;
    margin-bottom: 6px;
}
.metric-value {
    color: var(--text);
    font-size: 1.40rem;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    line-height: 1.15;
}
.metric-sub {
    color: var(--text-muted);
    font-size: 0.78rem;
    margin-top: 4px;
}
.profit { color: var(--profit) !important; font-weight: 600; }
.loss   { color: var(--loss)   !important; font-weight: 600; }
.accent { color: var(--accent) !important; }

/* ── Section headers ─────────────────────────────────────────── */
.section-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
    border-left: 3px solid var(--accent);
    padding-left: 11px;
    margin: 22px 0 14px;
    letter-spacing: .01em;
}

/* ── Risk badges ─────────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: .04em;
    text-transform: uppercase;
}
.badge-low      { background: rgba(0,229,160,0.13);   color: #00E5A0; border: 1px solid rgba(0,229,160,0.3); }
.badge-medium   { background: rgba(167,139,250,0.13); color: #A78BFA; border: 1px solid rgba(167,139,250,0.3); }
.badge-high     { background: rgba(245,158,11,0.13);  color: #FBBF24; border: 1px solid rgba(245,158,11,0.3); }
.badge-veryhigh { background: rgba(255,79,123,0.13);  color: #FF4F7B; border: 1px solid rgba(255,79,123,0.3); }

/* ── DataFrames ──────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] * { font-family: 'DM Sans', sans-serif !important; }

/* ── Tabs ────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border) !important;
    gap: 2px;
}
[data-testid="stTabs"] button[role="tab"] {
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    border-radius: 8px 8px 0 0 !important;
    transition: color .2s !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: rgba(167,139,250,0.07) !important;
}

/* ── Toggle / Slider ─────────────────────────────────────────── */
[data-testid="stToggle"] span { color: var(--text-muted) !important; }
[data-testid="stSlider"] * { color: var(--text-muted) !important; }

/* ── Radio buttons ───────────────────────────────────────────── */
[data-testid="stRadio"] label { color: var(--text-muted) !important; }

/* ── Expander ────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: var(--text) !important; }

/* ── Alerts / Info ───────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: rgba(167,139,250,0.07) !important;
    border-color: var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-muted) !important;
}

/* ── Download buttons ─────────────────────────────────────────── */
[data-testid="stDownloadButton"] button {
    background: rgba(167,139,250,0.10) !important;
    border: 1px solid var(--border) !important;
    color: var(--accent) !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: var(--accent) !important;
}

/* ── Caption / small text ────────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-dim) !important;
    font-size: 0.78rem !important;
}

/* ── Selectbox / Number input ────────────────────────────────── */
[data-testid="stSelectbox"] > div,
[data-testid="stNumberInput"] > div input {
    background: var(--card) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* ── Page title ──────────────────────────────────────────────── */
h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    background: linear-gradient(120deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2rem !important;
}

/* ── Divider ─────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Summary stat strip (sidebar quick stats table) ──────────── */
[data-testid="stSidebar"] table {
    width: 100%;
    border-collapse: collapse;
}
[data-testid="stSidebar"] table td {
    padding: 5px 4px;
    border-bottom: 1px solid rgba(46,40,85,0.5);
    font-size: 0.82rem;
}

/* ── Scrollbar ───────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Building blocks
# ─────────────────────────────────────────────────────────────────────────────

def _metric_card(label: str, value: str, sub: str = "",
                 pnl_color: bool = False, positive: bool = True) -> str:
    if pnl_color:
        sub_class = "profit" if positive else "loss"
    else:
        sub_class = "metric-sub"
    sub_html = f'<div class="{sub_class} metric-sub">{sub}</div>' if sub else ""
    return f"""
<div class="metric-card">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{value}</div>
  {sub_html}
</div>"""


def _risk_badge(level: str) -> str:
    cls = {"Low": "badge-low", "Medium": "badge-medium",
           "High": "badge-high", "Very High": "badge-veryhigh"}.get(level, "badge-medium")
    return f'<span class="badge {cls}">{level}</span>'


def section_header(title: str) -> None:
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Overview Tab
# ─────────────────────────────────────────────────────────────────────────────

def render_overview_tab(metrics: PortfolioMetrics) -> None:
    pnl_pos  = metrics.total_pnl >= 0
    pnl_sign = "+" if pnl_pos else ""
    ret_sign = "+" if metrics.total_return_pct >= 0 else ""

    section_header("Portfolio Summary")

    # Row 1
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_metric_card("Total Invested",
            f"{APP_CURRENCY_SYMBOL}{metrics.total_invested:,.0f}"), unsafe_allow_html=True)
    with c2:
        st.markdown(_metric_card("Current Value",
            f"{APP_CURRENCY_SYMBOL}{metrics.current_value:,.0f}",
            sub=f"{pnl_sign}{APP_CURRENCY_SYMBOL}{metrics.total_pnl:,.0f}",
            pnl_color=True, positive=pnl_pos), unsafe_allow_html=True)
    with c3:
        st.markdown(_metric_card("Total P&L",
            f'{pnl_sign}{APP_CURRENCY_SYMBOL}{metrics.total_pnl:,.0f}',
            sub=f"{ret_sign}{metrics.total_return_pct:.2f}%",
            pnl_color=True, positive=pnl_pos), unsafe_allow_html=True)
    with c4:
        st.markdown(_metric_card("Annual Dividends",
            f"{APP_CURRENCY_SYMBOL}{metrics.annual_dividends:,.0f}",
            sub="projected income"), unsafe_allow_html=True)

    # Row 2
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(_metric_card("Weighted Beta",
            f"{metrics.weighted_beta:.3f}", sub="portfolio volatility"), unsafe_allow_html=True)
    with c6:
        st.markdown(
            _metric_card("Risk Level", metrics.risk_level,
                         sub=f"Score: {metrics.risk_score:.1f} / 100")
            + _risk_badge(metrics.risk_level), unsafe_allow_html=True)
    with c7:
        st.markdown(_metric_card("Diversification",
            f"{metrics.diversification_score:.1f} / 100",
            sub=metrics.diversification_label), unsafe_allow_html=True)
    with c8:
        st.markdown(_metric_card("Top Holding",
            metrics.top_holding_ticker,
            sub=f"{metrics.top_holding_pct:.1f}% of portfolio"), unsafe_allow_html=True)

    # Row 3
    c9, c10, c11, c12 = st.columns(4)
    with c9:
        st.markdown(_metric_card("Profitable Holdings",
            str(metrics.profitable_holdings_count),
            sub=f"{metrics.losing_holdings_count} losing"), unsafe_allow_html=True)
    with c10:
        st.markdown(_metric_card("Best Performer",
            metrics.best_holding_ticker,
            sub=f"{metrics.best_holding_return_pct:+.2f}%",
            pnl_color=True, positive=True), unsafe_allow_html=True)
    with c11:
        st.markdown(_metric_card("Worst Performer",
            metrics.worst_holding_ticker,
            sub=f"{metrics.worst_holding_return_pct:+.2f}%",
            pnl_color=True, positive=False), unsafe_allow_html=True)
    with c12:
        st.markdown(_metric_card("Sectors",
            str(len(metrics.sector_allocation)),
            sub=metrics.diversification_label), unsafe_allow_html=True)

    st.markdown("")
    st.plotly_chart(charts.portfolio_value_bar(metrics), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Holdings Tab
# ─────────────────────────────────────────────────────────────────────────────

def render_holdings_tab(holdings: list[Holding]) -> None:
    section_header("Holdings Detail")

    rows = [{
        "Ticker":        h.ticker,
        "Name":          h.name,
        "Sector":        h.sector,
        "Shares":        h.shares,
        "Buy Price ₹":   h.buy_price,
        "Curr Price ₹":  h.current_price,
        "Invested ₹":    round(h.invested, 2),
        "Curr Value ₹":  round(h.current_value, 2),
        "P&L ₹":         round(h.pnl, 2),
        "Return %":      round(h.pnl_pct, 2),
        "Beta":          h.beta,
        "Div Yield %":   round(h.dividend_yield * 100, 2),
    } for h in holdings]

    df = pd.DataFrame(rows)

    def _color_pnl(val):
        c = "#00E5A0" if val >= 0 else "#FF4F7B"
        return f"color: {c}; font-weight:600"

    styled = (df.style
               .map(_color_pnl, subset=["P&L ₹", "Return %"])
               .format({"Buy Price ₹": "₹{:,.2f}", "Curr Price ₹": "₹{:,.2f}",
                        "Invested ₹": "₹{:,.2f}", "Curr Value ₹": "₹{:,.2f}",
                        "P&L ₹": "₹{:,.2f}", "Return %": "{:+.2f}%",
                        "Div Yield %": "{:.2f}%", "Beta": "{:.2f}"}))

    st.dataframe(styled, use_container_width=True, height=360)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.holdings_pnl_bar(holdings), use_container_width=True)
    with c2:
        st.plotly_chart(charts.holdings_pnl_pct_bar(holdings), use_container_width=True)

    # Dividends sub-section
    section_header("Dividend Income")
    div_fig = charts.dividend_bar(holdings)
    if div_fig.data:
        st.plotly_chart(div_fig, use_container_width=True)
    else:
        st.info("No dividend-yielding stocks in this portfolio.")


# ─────────────────────────────────────────────────────────────────────────────
#  Allocation Tab
# ─────────────────────────────────────────────────────────────────────────────

def render_allocation_tab(metrics: PortfolioMetrics, holdings: list[Holding]) -> None:
    section_header("Portfolio Allocation")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.sector_pie_chart(metrics), use_container_width=True)
    with c2:
        st.plotly_chart(charts.holding_weight_bar(holdings), use_container_width=True)

    section_header("Sector Breakdown")
    total = sum(metrics.sector_allocation.values()) or 1
    rows  = [
        {"Sector": s, "Value ₹": round(v, 2), "Weight %": round(v / total * 100, 1)}
        for s, v in sorted(metrics.sector_allocation.items(), key=lambda x: x[1], reverse=True)
    ]
    df = pd.DataFrame(rows)
    styled = df.style.format({"Value ₹": "₹{:,.2f}", "Weight %": "{:.1f}%"})
    st.dataframe(styled, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Performance Tab
# ─────────────────────────────────────────────────────────────────────────────

def render_performance_tab(history: list[HistoricalPoint], metrics: PortfolioMetrics) -> None:
    section_header("Portfolio Performance Over Time")

    if not history:
        st.info("No historical data available.")
        return

    st.caption(f"📅 Data through: {history[-1].date}")

    st.plotly_chart(charts.portfolio_history_line(history), use_container_width=True)

    start_val = history[0].value
    end_val   = history[-1].value
    window_ret = ((end_val - start_val) / start_val * 100) if start_val > 0 else 0
    buy_ret    = metrics.total_return_pct

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        col = "profit" if buy_ret >= 0 else "loss"
        st.markdown(_metric_card("Return Since Buy",
            f'<span class="{col}">{buy_ret:+.2f}%</span>'), unsafe_allow_html=True)
    with c2:
        col = "profit" if window_ret >= 0 else "loss"
        st.markdown(_metric_card(f"{len(history)}-Day Return",
            f'<span class="{col}">{window_ret:+.2f}%</span>'), unsafe_allow_html=True)
    with c3:
        st.markdown(_metric_card("Period High",
            f"{APP_CURRENCY_SYMBOL}{max(p.value for p in history):,.0f}"), unsafe_allow_html=True)
    with c4:
        st.markdown(_metric_card("Period Low",
            f"{APP_CURRENCY_SYMBOL}{min(p.value for p in history):,.0f}"), unsafe_allow_html=True)

    c1b, c2b = st.columns(2)
    with c1b:
        st.plotly_chart(charts.daily_returns_bar(history), use_container_width=True)
    with c2b:
        st.plotly_chart(charts.cumulative_return_line(history), use_container_width=True)

    st.plotly_chart(charts.drawdown_chart(history), use_container_width=True)
    st.caption("Note: Market data shows only trading days (no weekends/holidays).")


# ─────────────────────────────────────────────────────────────────────────────
#  Risk Tab
# ─────────────────────────────────────────────────────────────────────────────

def render_risk_tab(metrics: PortfolioMetrics, holdings: list[Holding]) -> None:
    section_header("Risk Analysis")

    c1, c2 = st.columns([1, 2])
    with c1:
        st.plotly_chart(charts.risk_gauge(metrics.risk_score), use_container_width=True)
        st.markdown(f"""
<div style='font-size:.88rem; color:#9D94C4; line-height:1.8;'>
  <b style='color:#EDE9FF'>Risk Level</b>  {_risk_badge(metrics.risk_level)}<br>
  <b style='color:#EDE9FF'>Risk Score</b>  {metrics.risk_score:.1f} / 100<br>
  <b style='color:#EDE9FF'>Weighted β</b>  {metrics.weighted_beta:.3f}<br>
  <b style='color:#EDE9FF'>HHI</b>  {metrics.hhi:.4f}<br>
  <b style='color:#EDE9FF'>Diversification</b>  {metrics.diversification_label}<br>
  <b style='color:#EDE9FF'>Components</b><br>
  &nbsp;&nbsp;β {metrics.risk_breakdown.beta_component:.1f} &nbsp;·&nbsp;
  Conc. {metrics.risk_breakdown.concentration_component:.1f} &nbsp;·&nbsp;
  Loss {metrics.risk_breakdown.loss_component:.1f}
</div>""", unsafe_allow_html=True)
    with c2:
        st.plotly_chart(charts.beta_comparison_bar(holdings), use_container_width=True)

    section_header("Risk vs Return  (bubble size = portfolio weight)")
    st.plotly_chart(charts.sector_risk_bubble(holdings), use_container_width=True)

    _render_risk_explainer(metrics)


def _render_risk_explainer(metrics: PortfolioMetrics) -> None:
    section_header("Understanding Your Risk Score")

    if metrics.weighted_beta < 1:
        beta_note = "Your portfolio is <b>defensive</b> — it moves less than the market."
    elif metrics.weighted_beta > 1:
        beta_note = "Your portfolio is <b>aggressive</b> — it amplifies market moves."
    else:
        beta_note = "Your portfolio tracks the market closely."

    if metrics.hhi <= 0.15:
        hhi_note = "Sectors are spread <b>very well</b> — good diversification."
    elif metrics.hhi <= 0.25:
        hhi_note = "<b>Moderate</b> sector concentration."
    else:
        hhi_note = "<b>High concentration</b> — consider spreading across more sectors."

    with st.expander("📖 What do these numbers mean?", expanded=True):
        st.markdown(f"""
**Beta ({metrics.weighted_beta:.3f}):** {beta_note}
A beta of 1 means the portfolio moves exactly with Nifty/Sensex.

**HHI ({metrics.hhi:.4f}):** {hhi_note}
HHI (Herfindahl-Hirschman Index) measures sector concentration.
Range: 0 (perfectly spread) → 1 (all in one sector).

**Risk Score ({metrics.risk_score:.1f} / 100):**
Composite score = beta weight 40% + sector concentration 35% + loss ratio 25%.
Current split — β: {metrics.risk_breakdown.beta_component:.1f} · concentration: {metrics.risk_breakdown.concentration_component:.1f} · loss: {metrics.risk_breakdown.loss_component:.1f}.
*Lower is better.*

**Diversification Score ({metrics.diversification_score:.1f} / 100):**
`(1 − HHI) × 100` — higher = better spread across sectors.
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Sidebar Quick Stats
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar_info(metrics: PortfolioMetrics) -> None:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    pnl_pos   = metrics.total_pnl >= 0
    pnl_color = "#00E5A0" if pnl_pos else "#FF4F7B"
    pnl_sign  = "+" if pnl_pos else ""

    st.sidebar.markdown(f"""
| | |
|--|--|
| Holdings | {metrics.holdings_count} |
| Invested | {APP_CURRENCY_SYMBOL}{metrics.total_invested:,.0f} |
| Value | {APP_CURRENCY_SYMBOL}{metrics.current_value:,.0f} |
| P&L | <span style='color:{pnl_color};font-weight:600'>{pnl_sign}{APP_CURRENCY_SYMBOL}{metrics.total_pnl:,.0f}</span> |
| Return | <span style='color:{pnl_color};font-weight:600'>{pnl_sign}{metrics.total_return_pct:.2f}%</span> |
| Beta | {metrics.weighted_beta:.2f} |
| Risk | {metrics.risk_level} |
| Dividends | {APP_CURRENCY_SYMBOL}{metrics.annual_dividends:,.0f} |
""", unsafe_allow_html=True)
