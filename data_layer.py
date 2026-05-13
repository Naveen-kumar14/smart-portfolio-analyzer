"""Data access layer for portfolio metadata, prices, and historical values."""

from __future__ import annotations

import hashlib
import math
import random
from datetime import date, timedelta
from typing import Optional

from config import DEFAULT_HISTORY_DAYS, SIMULATED_PRICE_VARIATION
from models import HistoricalPoint, Holding

STOCK_DB: dict[str, dict[str, float | str]] = {
    "RELIANCE":    {"name": "Reliance Industries",       "sector": "Energy",         "base_price": 2761.0, "beta": 0.95, "div_yield": 0.003},
    "TCS":         {"name": "Tata Consultancy Services", "sector": "Technology",     "base_price": 3842.0, "beta": 0.85, "div_yield": 0.012},
    "HDFCBANK":    {"name": "HDFC Bank",                 "sector": "Finance",        "base_price": 1612.0, "beta": 1.05, "div_yield": 0.010},
    "INFY":        {"name": "Infosys",                   "sector": "Technology",     "base_price": 1523.0, "beta": 0.88, "div_yield": 0.025},
    "HINDUNILVR":  {"name": "Hindustan Unilever",        "sector": "Consumer Goods", "base_price": 2387.0, "beta": 0.72, "div_yield": 0.015},
    "SUNPHARMA":   {"name": "Sun Pharmaceutical",        "sector": "Healthcare",     "base_price": 1105.0, "beta": 0.65, "div_yield": 0.005},
    "BHARTIARTL":  {"name": "Bharti Airtel",             "sector": "Telecom",        "base_price": 920.0,  "beta": 1.10, "div_yield": 0.008},
    "LT":          {"name": "Larsen & Toubro",           "sector": "Industrials",    "base_price": 2476.0, "beta": 1.15, "div_yield": 0.018},
    "AXISBANK":    {"name": "Axis Bank",                 "sector": "Finance",        "base_price": 1028.0, "beta": 1.20, "div_yield": 0.002},
    "TITAN":       {"name": "Titan Company",             "sector": "Consumer Goods", "base_price": 3198.0, "beta": 0.93, "div_yield": 0.004},
    "WIPRO":       {"name": "Wipro",                     "sector": "Technology",     "base_price": 478.0,  "beta": 0.82, "div_yield": 0.007},
    "MARUTI":      {"name": "Maruti Suzuki",             "sector": "Automobile",     "base_price": 9870.0, "beta": 1.08, "div_yield": 0.009},
    "NTPC":        {"name": "NTPC",                      "sector": "Utilities",      "base_price": 271.0,  "beta": 0.60, "div_yield": 0.045},
    "ONGC":        {"name": "ONGC",                      "sector": "Energy",         "base_price": 268.0,  "beta": 1.00, "div_yield": 0.060},
    "SBIN":        {"name": "State Bank of India",       "sector": "Finance",        "base_price": 627.0,  "beta": 1.30, "div_yield": 0.018},
    "ICICIBANK":   {"name": "ICICI Bank",                "sector": "Finance",        "base_price": 1102.0, "beta": 1.15, "div_yield": 0.008},
    "BAJFINANCE":  {"name": "Bajaj Finance",             "sector": "Finance",        "base_price": 6854.0, "beta": 1.35, "div_yield": 0.003},
    "NESTLEIND":   {"name": "Nestle India",              "sector": "Consumer Goods", "base_price": 22500.0, "beta": 0.55, "div_yield": 0.020},
    "DRREDDY":     {"name": "Dr. Reddy's Laboratories",  "sector": "Healthcare",     "base_price": 6200.0, "beta": 0.70, "div_yield": 0.006},
    "ADANIENT":    {"name": "Adani Enterprises",         "sector": "Industrials",    "base_price": 2450.0, "beta": 1.50, "div_yield": 0.001},
    "ITC":         {"name": "ITC Limited",               "sector": "Consumer Goods", "base_price": 420.0,  "beta": 0.78, "div_yield": 0.032},
    "HCLTECH":     {"name": "HCL Technologies",          "sector": "Technology",     "base_price": 1300.0, "beta": 0.90, "div_yield": 0.018},
}

_LAST_PRICE_MODE = "Simulated"
_LAST_HISTORY_MODE = "Simulated"


# Reset runtime status flags to simulated mode
def reset_runtime_status() -> None:
    global _LAST_PRICE_MODE, _LAST_HISTORY_MODE
    _LAST_PRICE_MODE = "Simulated"
    _LAST_HISTORY_MODE = "Simulated"


# Get the last used price mode (Live or Simulated)
def get_last_price_mode() -> str:
    return _LAST_PRICE_MODE


# Get the last used history mode (Live or Simulated)
def get_last_history_mode() -> str:
    return _LAST_HISTORY_MODE


# Normalize ticker symbol to uppercase and stripped
def normalize_ticker(ticker: str) -> str:
    return ticker.upper().strip()


# Retrieve stock information from database
def get_stock_info(ticker: str) -> Optional[dict[str, float | str]]:
    return STOCK_DB.get(normalize_ticker(ticker))


# Get list of all supported ticker symbols
def supported_tickers() -> list[str]:
    return sorted(STOCK_DB.keys())


# Generate stable random percentage for simulation
def _stable_random_percent(key: str, low: float, high: float) -> float:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    seed = int(digest[:16], 16)
    rng = random.Random(seed)
    return rng.uniform(low, high)


# Get current price for a ticker, live or simulated
def get_live_price(ticker: str, use_live: bool = False) -> Optional[float]:
    global _LAST_PRICE_MODE

    ticker = normalize_ticker(ticker)
    info = get_stock_info(ticker)
    if info is None:
        return None

    if use_live:
        try:
            import yfinance as yf

            fast_info = yf.Ticker(f"{ticker}.NS").fast_info
            last_price = fast_info.get("lastPrice") or fast_info.get("last_price")
            if last_price:
                _LAST_PRICE_MODE = "Live"
                return round(float(last_price), 2)
        except Exception as e:
            print(f"Live price failed for {ticker}: {e}")

    _LAST_PRICE_MODE = "Simulated"
    base_price = float(info["base_price"])
    variation = _stable_random_percent(
        key=f"{ticker}-{date.today().isoformat()}",
        low=-SIMULATED_PRICE_VARIATION,
        high=SIMULATED_PRICE_VARIATION,
    )
    return round(base_price * (1 + variation), 2)


# Create Holding object from user input
def build_holding_from_input(ticker: str, shares: float, buy_price: float, use_live: bool = False) -> Holding:
    ticker = normalize_ticker(ticker)
    info = get_stock_info(ticker) or {}
    current_price = get_live_price(ticker, use_live=use_live) or float(info.get("base_price", buy_price))

    return Holding(
        ticker=ticker,
        name=str(info.get("name", ticker)),
        sector=str(info.get("sector", "Other")),
        shares=float(shares),
        buy_price=float(buy_price),
        current_price=current_price,
        beta=float(info.get("beta", 1.0)),
        dividend_yield=float(info.get("div_yield", 0.0)),
    )


# Refresh prices for all holdings
def refresh_holdings_prices(holdings: list[Holding], use_live: bool = False) -> list[Holding]:
    refreshed: list[Holding] = []
    modes_seen: set[str] = set()

    for holding in holdings:
        refreshed_holding = build_holding_from_input(
            ticker=holding.ticker,
            shares=holding.shares,
            buy_price=holding.buy_price,
            use_live=use_live,
        )
        refreshed.append(refreshed_holding)
        modes_seen.add(_LAST_PRICE_MODE)

    if "Live" in modes_seen and "Simulated" in modes_seen:
        globals()["_LAST_PRICE_MODE"] = "Mixed"
    elif "Live" in modes_seen:
        globals()["_LAST_PRICE_MODE"] = "Live"
    else:
        globals()["_LAST_PRICE_MODE"] = "Simulated"

    return refreshed


# Get historical portfolio values over time
def get_historical_portfolio_values(
    holdings: list[Holding],
    days: int = DEFAULT_HISTORY_DAYS,
    use_live: bool = False,
) -> list[HistoricalPoint]:
    global _LAST_HISTORY_MODE

    days = max(7, min(days, 365))

    if use_live:
        try:
            history = _fetch_yfinance_history(holdings, days)
            _LAST_HISTORY_MODE = "Live"
            return history
        except Exception as e:
            print(f"Live history failed: {e}")

    _LAST_HISTORY_MODE = "Simulated"
    return _simulate_history(holdings, days)


# Simulate historical portfolio values
def _simulate_history(holdings: list[Holding], days: int) -> list[HistoricalPoint]:
    today = date.today()
    total_now = sum(h.current_value for h in holdings)

    daily_drift = 0.0003
    daily_vol = 0.008
    rng = random.Random(42)

    values: list[float] = [max(total_now, 1.0)]
    for _ in range(days - 1):
        shock = rng.gauss(daily_drift, daily_vol)
        prev = values[-1] / math.exp(shock)
        values.append(round(prev, 2))

    values.reverse()
    history: list[HistoricalPoint] = []
    for index, value in enumerate(values):
        day = today - timedelta(days=(days - 1 - index))
        history.append(HistoricalPoint(date=day.isoformat(), value=value))
    return history


# Fetch historical data from yfinance
def _fetch_yfinance_history(holdings: list[Holding], days: int) -> list[HistoricalPoint]:
    import pandas as pd
    import yfinance as yf

    end = date.today()
    start = end - timedelta(days=days + 15)

    total_series: Optional[pd.Series] = None
    for holding in holdings:
        hist = yf.Ticker(f"{holding.ticker}.NS").history(
            start=start.isoformat(),
            end=end.isoformat(),
        )["Close"]
        weighted = hist * holding.shares
        total_series = weighted if total_series is None else total_series.add(weighted, fill_value=0)

    if total_series is None or total_series.empty:
        raise ValueError("No history returned from yfinance.")

    return [
        HistoricalPoint(date=str(idx.date()), value=round(float(val), 2))
        for idx, val in total_series.tail(days).items()
    ]