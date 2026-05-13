"""
Application-wide configuration for the Smart Portfolio Analysis System.
Dark Purple Theme Edition.
"""

APP_TITLE = "Smart Portfolio Analysis"
APP_ICON = "📊"
APP_LAYOUT = "wide"
APP_CURRENCY_SYMBOL = "₹"

# Runtime defaults
DEFAULT_USE_LIVE_PRICES = True
DEFAULT_USE_LIVE_HISTORY = True
DEFAULT_HISTORY_DAYS = 90
MAX_HISTORY_DAYS = 365
SIMULATED_PRICE_VARIATION = 0.02

# Risk thresholds
RISK_LOW_MAX = 30
RISK_MEDIUM_MAX = 60
RISK_HIGH_MAX = 80

RISK_LEVELS = {
    "Low": (0, RISK_LOW_MAX),
    "Medium": (RISK_LOW_MAX, RISK_MEDIUM_MAX),
    "High": (RISK_MEDIUM_MAX, RISK_HIGH_MAX),
    "Very High": (RISK_HIGH_MAX, 100),
}

# Diversification thresholds (HHI)
HHI_WELL_DIVERSIFIED = 0.15
HHI_MODERATELY_DIVERSIFIED = 0.25

# Beta bands
BETA_LOW = 0.8
BETA_HIGH = 1.2

# ── Dark Purple Palette ────────────────────────────────────────────────────────
COLOR_PROFIT      = "#00E5A0"   # vivid mint green
COLOR_LOSS        = "#FF4F7B"   # vibrant rose-red
COLOR_NEUTRAL     = "#7B7FA6"   # muted lavender-grey
COLOR_ACCENT      = "#A78BFA"   # soft violet accent
COLOR_ACCENT2     = "#C084FC"   # lighter purple
COLOR_ACCENT3     = "#818CF8"   # indigo

COLOR_BG          = "#0D0B14"   # near-black purple tint
COLOR_SURFACE     = "#13101F"   # dark purple surface
COLOR_CARD        = "#1C1830"   # card background
COLOR_CARD_HOVER  = "#231E3D"   # card hover
COLOR_BORDER      = "#2E2855"   # subtle purple border
COLOR_BORDER_GLOW = "#6D28D9"   # glow border

COLOR_TEXT_PRIMARY   = "#EDE9FF"   # near-white with purple tint
COLOR_TEXT_SECONDARY = "#9D94C4"   # muted lavender text
COLOR_TEXT_MUTED     = "#5C5480"   # very muted

# Chart colours
SECTOR_COLORS = [
    "#A78BFA",  # violet
    "#00E5A0",  # mint
    "#FF4F7B",  # rose
    "#F59E0B",  # amber
    "#38BDF8",  # sky
    "#FB7185",  # pink
    "#34D399",  # emerald
    "#F472B6",  # fuchsia
    "#60A5FA",  # blue
    "#C084FC",  # purple
    "#FBBF24",  # yellow
    "#818CF8",  # indigo
]

CHART_HEIGHT      = 420
CHART_TEMPLATE    = "plotly_dark"
CHART_PAPER_BG    = "rgba(0,0,0,0)"
CHART_PLOT_BG     = "rgba(0,0,0,0)"

EXPORT_JSON_FILENAME = "portfolio.json"
EXPORT_CSV_FILENAME  = "portfolio_metrics.csv"

TAB_NAMES = [
    "📋 Overview",
    "📈 Holdings",
    "🥧 Allocation",
    "📉 Performance",
    "⚠️ Risk Analysis",
]
