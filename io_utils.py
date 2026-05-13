"""Input and output helpers for JSON/CSV portfolio data."""

from __future__ import annotations

import csv
import io
import json
from typing import Iterable

from data_layer import build_holding_from_input, normalize_ticker
from models import Holding, PortfolioMetrics

REQUIRED_PORTFOLIO_FIELDS = {"ticker", "shares", "buy_price"}


# Decode raw string or bytes to string
def _decode_raw(raw: str | bytes) -> str:
    if isinstance(raw, bytes):
        return raw.decode("utf-8-sig")
    return raw


# Validate and parse numeric field from input
def _validate_numeric_field(name: str, value: object, row_label: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{row_label}: invalid {name}.") from exc
    if parsed <= 0:
        raise ValueError(f"{row_label}: {name} must be greater than 0.")
    return parsed


# Check for duplicate tickers in portfolio items
def _check_duplicate_tickers(items: Iterable[dict[str, object]]) -> str:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        ticker = normalize_ticker(str(item.get("ticker", "")))
        if ticker in seen:
            duplicates.add(ticker)
        seen.add(ticker)
    if duplicates:
        return ", ".join(sorted(duplicates))
    return ""


# Parse portfolio from JSON data
def parse_json_portfolio(raw: str | bytes, use_live: bool = False) -> tuple[list[Holding], str]:
    try:
        data = json.loads(_decode_raw(raw))
    except json.JSONDecodeError as exc:
        return [], f"Invalid JSON: {exc}"

    if not isinstance(data, list):
        return [], "JSON must be a list of objects."

    duplicates = _check_duplicate_tickers(data)
    if duplicates:
        return [], f"Duplicate tickers found: {duplicates}"

    holdings: list[Holding] = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            return [], f"Item {index} must be a JSON object."

        missing = REQUIRED_PORTFOLIO_FIELDS - set(item.keys())
        if missing:
            return [], f"Item {index} is missing fields: {sorted(missing)}"

        try:
            ticker = normalize_ticker(str(item["ticker"]))
            shares = _validate_numeric_field("shares", item["shares"], f"Item {index}")
            buy_price = _validate_numeric_field("buy_price", item["buy_price"], f"Item {index}")
            holdings.append(build_holding_from_input(ticker, shares, buy_price, use_live=use_live))
        except ValueError as exc:
            return [], str(exc)

    return holdings, ""


# Parse portfolio from CSV data
def parse_csv_portfolio(raw: str | bytes, use_live: bool = False) -> tuple[list[Holding], str]:
    content = _decode_raw(raw)
    reader = csv.DictReader(io.StringIO(content))
    if reader.fieldnames is None:
        return [], "CSV must include a header row."

    normalized_fieldnames = {name.strip().lower() for name in reader.fieldnames}
    missing = REQUIRED_PORTFOLIO_FIELDS - normalized_fieldnames
    if missing:
        return [], f"CSV missing columns: {sorted(missing)}"

    rows: list[dict[str, str]] = []
    for row in reader:
        normalized_row = {(key or "").strip().lower(): (value or "").strip() for key, value in row.items()}
        if any(normalized_row.values()):
            rows.append(normalized_row)

    if not rows:
        return [], "CSV has no data rows."

    duplicates = _check_duplicate_tickers(rows)
    if duplicates:
        return [], f"Duplicate tickers found: {duplicates}"

    holdings: list[Holding] = []
    for index, row in enumerate(rows, start=1):
        try:
            ticker = normalize_ticker(row["ticker"])
            shares = _validate_numeric_field("shares", row["shares"], f"Row {index}")
            buy_price = _validate_numeric_field("buy_price", row["buy_price"], f"Row {index}")
            holdings.append(build_holding_from_input(ticker, shares, buy_price, use_live=use_live))
        except ValueError as exc:
            return [], str(exc)

    return holdings, ""


# Export portfolio holdings to JSON string
def export_portfolio_json(holdings: list[Holding]) -> str:
    payload = [
        {
            "ticker": holding.ticker,
            "shares": holding.shares,
            "buy_price": holding.buy_price,
        }
        for holding in holdings
    ]
    return json.dumps(payload, indent=2)


# Export portfolio metrics and holdings to CSV string
def export_metrics_csv(metrics: PortfolioMetrics, holdings: list[Holding]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["=== PORTFOLIO SUMMARY ==="])
    writer.writerow(["Metric", "Value"])
    writer.writerows([
        ("Total Invested (₹)", f"{metrics.total_invested:,.2f}"),
        ("Current Value (₹)", f"{metrics.current_value:,.2f}"),
        ("Total P&L (₹)", f"{metrics.total_pnl:,.2f}"),
        ("Total Return (%)", f"{metrics.total_return_pct:.2f}%"),
        ("Weighted Beta", f"{metrics.weighted_beta:.3f}"),
        ("HHI", f"{metrics.hhi:.4f}"),
        ("Diversification Score", f"{metrics.diversification_score:.1f}"),
        ("Diversification Label", metrics.diversification_label),
        ("Risk Score", f"{metrics.risk_score:.1f}"),
        ("Risk Level", metrics.risk_level),
        ("Profitable Holdings", metrics.profitable_holdings_count),
        ("Losing Holdings", metrics.losing_holdings_count),
        ("Top Holding", f"{metrics.top_holding_ticker} ({metrics.top_holding_pct:.1f}%)"),
        ("Best Holding", f"{metrics.best_holding_ticker} ({metrics.best_holding_return_pct:.2f}%)"),
        ("Worst Holding", f"{metrics.worst_holding_ticker} ({metrics.worst_holding_return_pct:.2f}%)"),
        ("Annual Dividends (₹)", f"{metrics.annual_dividends:,.2f}"),
    ])

    writer.writerow([])
    writer.writerow(["=== HOLDINGS DETAIL ==="])
    writer.writerow([
        "Ticker", "Name", "Sector", "Shares", "Buy Price (₹)", "Current Price (₹)",
        "Invested (₹)", "Current Value (₹)", "P&L (₹)", "Return (%)", "Beta", "Div Yield (%)",
    ])

    for holding in holdings:
        writer.writerow([
            holding.ticker,
            holding.name,
            holding.sector,
            holding.shares,
            f"{holding.buy_price:.2f}",
            f"{holding.current_price:.2f}",
            f"{holding.invested:.2f}",
            f"{holding.current_value:.2f}",
            f"{holding.pnl:.2f}",
            f"{holding.pnl_pct:.2f}%",
            f"{holding.beta:.2f}",
            f"{holding.dividend_yield * 100:.2f}%",
        ])

    return output.getvalue()


# Get sample JSON template for portfolio input
def json_template() -> str:
    return json.dumps([
        {"ticker": "TCS", "shares": 30, "buy_price": 3500},
        {"ticker": "RELIANCE", "shares": 50, "buy_price": 2400},
    ], indent=2)


# Get sample CSV template for portfolio input
def csv_template() -> str:
    return "ticker,shares,buy_price\nTCS,30,3500\nRELIANCE,50,2400\n"
