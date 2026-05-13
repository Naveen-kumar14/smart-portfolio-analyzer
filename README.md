# 📊 Smart Portfolio Analysis System

A modular Python + Streamlit portfolio dashboard for Indian stocks, featuring a **dark purple glass UI**, live prices via `yfinance`, and rich analytics.

---

## ✨ What's enhanced

| Area | Enhancement |
|---|---|
| **Theme** | Dark purple glass UI — `#0D0B14` background, violet accents, gradient title |
| **Charts** | Drawdown chart, cumulative return line, dividend bar — all new |
| **Performance tab** | Period High *and* Period Low metrics added |
| **Holdings tab** | Dividend income section with per-stock bar |
| **Data formatting** | Styled DataFrames with ₹ and % formatting |
| **CSS** | Custom scrollbar, hover glow cards, gradient tab indicator |
| **Code quality** | `use_container_width=True` (replaces deprecated `width="stretch"`) |

---

## 📁 File structure

```
portfolio/
├── app.py            # Streamlit entry point
├── config.py         # Settings, colours, thresholds
├── data_layer.py     # Price + history fetching (live / simulated)
├── io_utils.py       # JSON / CSV import-export helpers
├── metrics.py        # Pure portfolio calculations
├── models.py         # Dataclasses (Holding, PortfolioMetrics, …)
├── charts.py         # Plotly chart builders
├── ui_components.py  # Streamlit rendering helpers (CSS + tabs)
├── sample_data.py    # Demo portfolio
└── requirements.txt
```

---

## 🚀 Local setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Deploy on Streamlit Community Cloud (free, public URL)

1. Push all files to a **public GitHub repo** (e.g. `github.com/yourname/portfolio-app`).

2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.

3. Click **"New app"** → choose your repo, branch (`main`), and main file (`app.py`).

4. Click **Deploy**. Streamlit builds and hosts the app — you get a URL like  
   `https://yourname-portfolio-app-app-xxxx.streamlit.app`

5. The app auto-redeploys on every `git push`.

> **No credit card needed.** Community Cloud is free for public repos.

---

## 📥 Input formats

### JSON
```json
[
  {"ticker": "TCS",      "shares": 30, "buy_price": 3500},
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

## 📝 Supported tickers (22 NSE stocks)

`RELIANCE · TCS · HDFCBANK · INFY · HINDUNILVR · SUNPHARMA · BHARTIARTL · LT · AXISBANK · TITAN · WIPRO · MARUTI · NTPC · ONGC · SBIN · ICICIBANK · BAJFINANCE · NESTLEIND · DRREDDY · ADANIENT · ITC · HCLTECH`

Live prices are fetched as `<TICKER>.NS` from Yahoo Finance via `yfinance`.  
If a live fetch fails the app logs it to the terminal and falls back to a deterministic simulated price.

---

## Contributors

1. Naveen Kumar.c ([Naveen-kumar14](https://github.com/Naveen-kumar14))
2. Akash.r ([Akash-r-git](https://github.com/Akash-r-git))
