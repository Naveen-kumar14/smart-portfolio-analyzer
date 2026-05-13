"""Pure portfolio calculations."""

from __future__ import annotations

from config import (
    HHI_MODERATELY_DIVERSIFIED,
    HHI_WELL_DIVERSIFIED,
    RISK_HIGH_MAX,
    RISK_LOW_MAX,
    RISK_MEDIUM_MAX,
)
from models import Holding, PortfolioMetrics, RiskBreakdown


# Calculate total amount invested in portfolio
def total_invested(holdings: list[Holding]) -> float:
    return sum(holding.invested for holding in holdings)


# Calculate current total value of portfolio
def current_portfolio_value(holdings: list[Holding]) -> float:
    return sum(holding.current_value for holding in holdings)


# Calculate total profit/loss of portfolio
def total_pnl(holdings: list[Holding]) -> float:
    return current_portfolio_value(holdings) - total_invested(holdings)


# Calculate total return percentage of portfolio
def total_return_pct(holdings: list[Holding]) -> float:
    invested = total_invested(holdings)
    return 0.0 if invested == 0 else (total_pnl(holdings) / invested) * 100


# Calculate weighted beta of portfolio
def weighted_beta(holdings: list[Holding]) -> float:
    portfolio_value = current_portfolio_value(holdings)
    if portfolio_value == 0:
        return 1.0
    return sum((holding.current_value / portfolio_value) * holding.beta for holding in holdings)


# Calculate sector allocation by value
def sector_allocation(holdings: list[Holding]) -> dict[str, float]:
    allocation: dict[str, float] = {}
    for holding in holdings:
        allocation[holding.sector] = allocation.get(holding.sector, 0.0) + holding.current_value
    return allocation


# Calculate Herfindahl-Hirschman Index for diversification
def herfindahl_index(holdings: list[Holding]) -> float:
    allocation = sector_allocation(holdings)
    total = sum(allocation.values())
    if total == 0:
        return 1.0
    return sum((value / total) ** 2 for value in allocation.values())


# Calculate diversification score from HHI
def diversification_score(holdings: list[Holding]) -> float:
    return round((1 - herfindahl_index(holdings)) * 100, 1)


# Get diversification label based on HHI
def diversification_label(hhi: float) -> str:
    if hhi <= HHI_WELL_DIVERSIFIED:
        return "Well Diversified"
    if hhi <= HHI_MODERATELY_DIVERSIFIED:
        return "Moderately Diversified"
    return "Concentrated"


# Calculate ratio of losing holdings value to total
def _loss_ratio(holdings: list[Holding]) -> float:
    total_value = current_portfolio_value(holdings)
    if total_value == 0:
        return 0.0
    losing_value = sum(holding.current_value for holding in holdings if holding.pnl < 0)
    return losing_value / total_value


# Calculate risk breakdown components
def risk_breakdown(holdings: list[Holding]) -> RiskBreakdown:
    beta_score = min(max((weighted_beta(holdings) / 2.0) * 100, 0), 100)
    concentration_score = herfindahl_index(holdings) * 100
    loss_score = _loss_ratio(holdings) * 100

    return RiskBreakdown(
        beta_component=round(0.40 * beta_score, 1),
        concentration_component=round(0.35 * concentration_score, 1),
        loss_component=round(0.25 * loss_score, 1),
    )


# Calculate overall risk score
def risk_score(holdings: list[Holding]) -> float:
    breakdown = risk_breakdown(holdings)
    return round(min(breakdown.beta_component + breakdown.concentration_component + breakdown.loss_component, 100), 1)


# Get risk level label from score
def risk_level(score: float) -> str:
    if score <= RISK_LOW_MAX:
        return "Low"
    if score <= RISK_MEDIUM_MAX:
        return "Medium"
    if score <= RISK_HIGH_MAX:
        return "High"
    return "Very High"


# Find the top holding by value
def top_holding(holdings: list[Holding]) -> tuple[str, float]:
    if not holdings:
        return "N/A", 0.0
    total_value = current_portfolio_value(holdings)
    holding = max(holdings, key=lambda holding: holding.current_value)
    pct = 0.0 if total_value == 0 else (holding.current_value / total_value) * 100
    return holding.ticker, round(pct, 1)


# Calculate total annual dividends
def annual_dividends(holdings: list[Holding]) -> float:
    return sum(holding.annual_dividend for holding in holdings)


# Find best and worst performing holdings
def _best_and_worst_holding(holdings: list[Holding]) -> tuple[str, float, str, float]:
    if not holdings:
        return "N/A", 0.0, "N/A", 0.0
    best = max(holdings, key=lambda holding: holding.pnl_pct)
    worst = min(holdings, key=lambda holding: holding.pnl_pct)
    return best.ticker, round(best.pnl_pct, 2), worst.ticker, round(worst.pnl_pct, 2)


# Compute all portfolio metrics
def compute_portfolio_metrics(holdings: list[Holding]) -> PortfolioMetrics:
    invested = total_invested(holdings)
    current_value = current_portfolio_value(holdings)
    pnl = total_pnl(holdings)
    return_pct = total_return_pct(holdings)
    beta = weighted_beta(holdings)
    hhi = herfindahl_index(holdings)
    div_score = diversification_score(holdings)
    div_label = diversification_label(hhi)
    score = risk_score(holdings)
    level = risk_level(score)
    top_ticker, top_pct = top_holding(holdings)
    best_ticker, best_return, worst_ticker, worst_return = _best_and_worst_holding(holdings)
    breakdown = risk_breakdown(holdings)

    return PortfolioMetrics(
        total_invested=round(invested, 2),
        current_value=round(current_value, 2),
        total_pnl=round(pnl, 2),
        total_return_pct=round(return_pct, 2),
        weighted_beta=round(beta, 3),
        hhi=round(hhi, 4),
        diversification_score=div_score,
        diversification_label=div_label,
        risk_score=score,
        risk_level=level,
        top_holding_ticker=top_ticker,
        top_holding_pct=top_pct,
        annual_dividends=round(annual_dividends(holdings), 2),
        sector_allocation=sector_allocation(holdings),
        holdings_count=len(holdings),
        profitable_holdings_count=sum(1 for holding in holdings if holding.pnl >= 0),
        losing_holdings_count=sum(1 for holding in holdings if holding.pnl < 0),
        best_holding_ticker=best_ticker,
        best_holding_return_pct=best_return,
        worst_holding_ticker=worst_ticker,
        worst_holding_return_pct=worst_return,
        risk_breakdown=breakdown,
    )
