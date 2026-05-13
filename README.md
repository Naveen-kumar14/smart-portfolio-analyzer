# 📊 Smart Portfolio Analysis System

> A modern **Python + Streamlit** portfolio analytics dashboard for Indian stock investors 🇮🇳  
> Built with a sleek **dark purple glassmorphism UI**, real-time market integration, and advanced portfolio insights.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-Interactive_Charts-6f42c1?style=for-the-badge&logo=plotly)
![Yahoo Finance](https://img.shields.io/badge/Data-yFinance-success?style=for-the-badge)

---

# ✨ Features

## 🎨 Premium UI Experience
- Dark purple glassmorphism theme
- Gradient headers & glowing cards
- Animated hover effects
- Custom scrollbar styling
- Responsive layout for desktop & laptop

---

## 📈 Portfolio Analytics
- Total portfolio valuation
- Profit / Loss tracking
- Daily performance monitoring
- Allocation breakdown
- Portfolio diversification insights
- Period High & Period Low metrics

---

## 📊 Advanced Charts
- Portfolio allocation pie chart
- Cumulative returns graph
- Portfolio drawdown visualization
- Dividend income analytics
- Interactive Plotly dashboards

---

## 📂 Import / Export Support

Supports portfolio uploads using:

### JSON
```json
[
  {"ticker": "TCS", "shares": 30, "buy_price": 3500},
  {"ticker": "RELIANCE", "shares": 50, "buy_price": 2400}
]
```

### CSV
```csv
ticker,shares,buy_price
TCS,30,3500
RELIANCE,50,2400
```

---

# ⚡ Live Market Data

Live NSE stock prices are fetched using:

```python
yfinance
```

Ticker format:

```python
<TICKER>.NS
```

Example:

```python
TCS.NS
RELIANCE.NS
```

If Yahoo Finance fails to return data, the application automatically switches to a deterministic simulated fallback price system.

---

# 🏗️ Project Structure

```bash
portfolio/
│
├── app.py              # Streamlit application entry
├── config.py           # Theme settings & constants
├── data_layer.py       # Live price/history fetching
├── io_utils.py         # CSV & JSON import/export
├── metrics.py          # Portfolio calculations
├── models.py           # Dataclasses & models
├── charts.py           # Plotly visualizations
├── ui_components.py    # Reusable Streamlit UI components
├── sample_data.py      # Demo portfolio dataset
└── requirements.txt    # Dependencies
```

---

# 🚀 Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/Naveen-kumar14/smart-portfolio-analyzer.git
```

## 2️⃣ Navigate into Project

```bash
cd smart-portfolio-analyzer
```

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 4️⃣ Run Application

```bash
streamlit run app.py
```

---

# ☁️ Live Demo

## 🌐 Streamlit Deployment

APP URL:  
👉 https://portix.streamlit.app

---

# 📦 Supported NSE Stocks

```text
RELIANCE
TCS
HDFCBANK
INFY
HINDUNILVR
SUNPHARMA
BHARTIARTL
LT
AXISBANK
TITAN
WIPRO
MARUTI
NTPC
ONGC
SBIN
ICICIBANK
BAJFINANCE
NESTLEIND
DRREDDY
ADANIENT
ITC
HCLTECH
```

---

# 🧠 Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core backend |
| Streamlit | Web dashboard |
| Plotly | Interactive charts |
| Pandas | Data analysis |
| yFinance | Live stock data |
| Dataclasses | Portfolio models |

---

# 📸 Highlights

- 📉 Real-time portfolio drawdown analysis
- 💰 Dividend tracking system
- 📊 Interactive financial visualizations
- 🧮 Accurate portfolio metrics engine
- 🎨 Fully customized Streamlit UI
- ⚡ Fast modular architecture

---

# 🔮 Future Enhancements

- AI-based stock recommendations
- Risk score prediction
- Portfolio rebalancing suggestions
- Multi-user authentication
- Firebase / PostgreSQL integration
- Export reports as PDF
- Mobile responsive optimization

---

# 👨‍💻 Contributors

| Name | GitHub |
|---|---|
| Naveen Kumar C | [@Naveen-kumar14](https://github.com/Naveen-kumar14) |
| Nathaneal Cecil | Contributor |

---

# ⭐ Support

If you like this project:

- ⭐ Star the repository
- 🍴 Fork the project
- 🚀 Share with others

---



---

> Built with ❤️ using Python, Streamlit, and real-time market data.
