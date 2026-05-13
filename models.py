from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Holding:
    """Represents a single stock holding in the portfolio."""

    ticker: str
    name: str
    sector: str
    shares: float
    buy_price: float
    current_price: float
    beta: float = 1.0
    dividend_yield: float = 0.0

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        self.name = self.name.strip()
        self.sector = self.sector.strip() or "Other"

        if self.shares <= 0:
            raise ValueError("Shares must be greater than 0.")
        if self.buy_price <= 0:
            raise ValueError("Buy price must be greater than 0.")
        if self.current_price <= 0:
            raise ValueError("Current price must be greater than 0.")
        if self.beta < 0:
            raise ValueError("Beta cannot be negative.")
        if self.dividend_yield < 0:
            raise ValueError("Dividend yield cannot be negative.")

    @property
    def invested(self) -> float:
        return self.shares * self.buy_price

    @property
    def current_value(self) -> float:
        return self.shares * self.current_price

    @property
    def pnl(self) -> float:
        return self.current_value - self.invested

    @property
    def pnl_pct(self) -> float:
        return 0.0 if self.invested == 0 else (self.pnl / self.invested) * 100

    @property
    def annual_dividend(self) -> float:
        return self.current_value * self.dividend_yield


@dataclass(slots=True)
class RiskBreakdown:
    beta_component: float
    concentration_component: float
    loss_component: float


@dataclass(slots=True)
class PortfolioMetrics:
    total_invested: float
    current_value: float
    total_pnl: float
    total_return_pct: float
    weighted_beta: float
    hhi: float
    diversification_score: float
    diversification_label: str
    risk_score: float
    risk_level: str
    top_holding_ticker: str
    top_holding_pct: float
    annual_dividends: float
    sector_allocation: dict[str, float]
    holdings_count: int
    profitable_holdings_count: int
    losing_holdings_count: int
    best_holding_ticker: str
    best_holding_return_pct: float
    worst_holding_ticker: str
    worst_holding_return_pct: float
    risk_breakdown: RiskBreakdown


@dataclass(slots=True)
class HistoricalPoint:
    date: str
    value: float
