from __future__ import annotations

from datetime import datetime

import streamlit as st

import config
import data_layer
import io_utils
import metrics as m
import ui_components
from models import Holding
from sample_data import DEMO_HOLDINGS

PORTFOLIO_SOURCES = ["Demo Portfolio", "Manual Entry", "Upload JSON", "Upload CSV"]


def _init_state() -> None:
    st.session_state.setdefault("manual_holdings", [])
    st.session_state.setdefault("refresh_nonce", 0)
    st.session_state.setdefault("last_refresh", None)


def _sidebar_runtime_settings() -> tuple[bool, bool, int]:
    st.sidebar.markdown("### ⚙️ Runtime Settings")
    use_live_prices = st.sidebar.toggle(
        "Use live prices",
        value=config.DEFAULT_USE_LIVE_PRICES,
        help="Uses yfinance when available; falls back to simulated prices on failure.",
    )
    use_live_history = st.sidebar.toggle(
        "Use live history",
        value=config.DEFAULT_USE_LIVE_HISTORY,
        help="Uses yfinance history when available; falls back to simulated history on failure.",
    )
    history_days = st.sidebar.slider(
        "History window (days)",
        min_value=30,
        max_value=config.MAX_HISTORY_DAYS,
        value=config.DEFAULT_HISTORY_DAYS,
        step=30,
    )
    st.sidebar.markdown("---")
    return use_live_prices, use_live_history, history_days


def _load_demo_portfolio(use_live_prices: bool) -> list[Holding]:
    if use_live_prices:
        return data_layer.refresh_holdings_prices(DEMO_HOLDINGS, use_live=True)
    return DEMO_HOLDINGS


def _render_manual_entry(use_live_prices: bool) -> list[Holding]:
    st.sidebar.markdown("#### Add Holdings Manually")
    known_tickers = data_layer.supported_tickers()

    with st.sidebar.form("add_holding_form", clear_on_submit=True):
        ticker    = st.selectbox("Ticker", known_tickers)
        shares    = st.number_input("Shares", min_value=0.01, value=10.0, step=1.0)
        buy_price = st.number_input("Buy Price (₹)", min_value=0.01, value=1000.0, step=50.0)
        submitted = st.form_submit_button("➕ Add Holding")

        if submitted:
            existing = {h.ticker for h in st.session_state.manual_holdings}
            if ticker in existing:
                st.sidebar.warning(f"{ticker} already exists. Remove it first.")
            else:
                st.session_state.manual_holdings.append(
                    data_layer.build_holding_from_input(ticker, shares, buy_price, use_live=use_live_prices)
                )
                st.sidebar.success(f"Added {ticker}")

    if st.session_state.manual_holdings:
        labels = [h.ticker for h in st.session_state.manual_holdings]
        remove = st.sidebar.selectbox("Remove holding", ["None", *labels])
        if st.sidebar.button("➖ Remove Selected") and remove != "None":
            st.session_state.manual_holdings = [
                h for h in st.session_state.manual_holdings if h.ticker != remove
            ]
            st.sidebar.success(f"Removed {remove}")

    if st.sidebar.button("🗑️ Clear All"):
        st.session_state.manual_holdings = []

    if use_live_prices and st.session_state.manual_holdings:
        st.session_state.manual_holdings = data_layer.refresh_holdings_prices(
            st.session_state.manual_holdings, use_live=True,
        )

    if not st.session_state.manual_holdings:
        st.sidebar.info("No holdings yet. Add some above.")

    return st.session_state.manual_holdings


def _render_json_upload(use_live_prices: bool) -> tuple[list[Holding], str]:
    st.sidebar.markdown("#### Upload JSON File")
    st.sidebar.code(io_utils.json_template(), language="json")
    uploaded = st.sidebar.file_uploader("Choose JSON file", type=["json"])
    if not uploaded:
        return [], ""
    holdings, err = io_utils.parse_json_portfolio(uploaded.read(), use_live=use_live_prices)
    if err:
        st.sidebar.error(f"Parse error: {err}")
    else:
        st.sidebar.success(f"✅ Loaded {len(holdings)} holdings")
    return holdings, err


def _render_csv_upload(use_live_prices: bool) -> tuple[list[Holding], str]:
    st.sidebar.markdown("#### Upload CSV File")
    st.sidebar.code(io_utils.csv_template(), language="text")
    uploaded = st.sidebar.file_uploader("Choose CSV file", type=["csv"])
    if not uploaded:
        return [], ""
    holdings, err = io_utils.parse_csv_portfolio(uploaded.read(), use_live=use_live_prices)
    if err:
        st.sidebar.error(f"Parse error: {err}")
    else:
        st.sidebar.success(f"✅ Loaded {len(holdings)} holdings")
    return holdings, err


def main() -> None:
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon=config.APP_ICON,
        layout=config.APP_LAYOUT,
        initial_sidebar_state="expanded",
    )
    ui_components.inject_custom_css()
    _init_state()

    st.sidebar.title(f"{config.APP_ICON} {config.APP_TITLE}")
    st.sidebar.markdown("---")

    use_live_prices, use_live_history, history_days = _sidebar_runtime_settings()
    data_layer.reset_runtime_status()

    if st.sidebar.button("🔄 Refresh Prices"):
        st.session_state.refresh_nonce += 1
        st.session_state.last_refresh = datetime.now().strftime("%H:%M:%S")

    input_mode = st.sidebar.radio("Portfolio Source", PORTFOLIO_SOURCES, index=0)
    holdings: list[Holding] = []
    error_msg = ""

    if input_mode == "Demo Portfolio":
        holdings = _load_demo_portfolio(use_live_prices)
        st.sidebar.success(f"✅ {len(holdings)} demo holdings loaded")
    elif input_mode == "Manual Entry":
        holdings = _render_manual_entry(use_live_prices)
    elif input_mode == "Upload JSON":
        holdings, error_msg = _render_json_upload(use_live_prices)
    elif input_mode == "Upload CSV":
        holdings, error_msg = _render_csv_upload(use_live_prices)

    if st.session_state.last_refresh:
        st.sidebar.caption(f"Last refresh: {st.session_state.last_refresh}")

    if not holdings:
        st.title(f"{config.APP_ICON} {config.APP_TITLE}")
        st.info(
            "👈 Select a portfolio source from the sidebar to get started.\n\n"
            "Use **Demo Portfolio** for an instant preview, or add your own holdings."
        )
        st.stop()

    portfolio_metrics = m.compute_portfolio_metrics(holdings)
    history = data_layer.get_historical_portfolio_values(
        holdings, days=history_days, use_live=use_live_history,
    )

    ui_components.render_sidebar_info(portfolio_metrics)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Export")
    st.sidebar.download_button(
        label="⬇️ Export Portfolio JSON",
        data=io_utils.export_portfolio_json(holdings),
        file_name=config.EXPORT_JSON_FILENAME,
        mime="application/json",
    )
    st.sidebar.download_button(
        label="⬇️ Export Metrics CSV",
        data=io_utils.export_metrics_csv(portfolio_metrics, holdings),
        file_name=config.EXPORT_CSV_FILENAME,
        mime="text/csv",
    )

    st.title(f"{config.APP_ICON} {config.APP_TITLE}")
    live_status    = data_layer.get_last_price_mode()   if use_live_prices   else "Simulated"
    history_status = data_layer.get_last_history_mode() if use_live_history  else "Simulated"
    st.caption(
        f"{portfolio_metrics.holdings_count} holdings · "
        f"Value: {config.APP_CURRENCY_SYMBOL}{portfolio_metrics.current_value:,.0f} · "
        f"Prices: {live_status} · History: {history_status} ({history_days}d) · "
        f"Mode: {input_mode}"
    )

    if error_msg:
        st.warning(error_msg)

    st.markdown("---")

    tabs = st.tabs(config.TAB_NAMES)
    with tabs[0]:
        ui_components.render_overview_tab(portfolio_metrics)
    with tabs[1]:
        ui_components.render_holdings_tab(holdings)
    with tabs[2]:
        ui_components.render_allocation_tab(portfolio_metrics, holdings)
    with tabs[3]:
        ui_components.render_performance_tab(history, portfolio_metrics)
    with tabs[4]:
        ui_components.render_risk_tab(portfolio_metrics, holdings)


if __name__ == "__main__":
    main()
