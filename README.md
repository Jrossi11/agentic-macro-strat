# 🏹 Agentic Macro Strategy (Asymmetry Hunter)

An autonomous multi-agent research and backtesting engine designed to identify commodity supply/demand shocks and translate them into high-conviction trading signals.

Built for **Jacaranda Capital Partners** to detect and model asymmetric macro opportunities before they are fully priced in.

---

## 🏗️ System Architecture

The core logic is an orchestrated **LangGraph** pipeline where specialized agents handle the transition from raw unstructured news to structured risk-managed trades.

### The Agent Swarm
1.  **🔎 Historical Scout**: Queries the **Tavily Search API** for specific commodity shocks (strikes, weather, site closures) within targeted date windows.
2.  **🌍 Macro Scout**: Scans authoritative domains (`eia.gov`, `usgs.gov`, `iea.org`) to determine the global market regime (Deficit vs. Surplus).
3.  **📊 Analyst Agent**: Transforms raw text into structured **Catalyst** objects. 
    *   **Temporal Hardening**: Enforces a strict filter to reject any article published after the quarter window, eliminating look-ahead bias.
4.  **🧠 Quant Agent**: The decision engine. Cross-references fundamental shocks with technical price action (50/200 MAs, 20-day High/Low, ATR).
    *   **Asymmetry Logic**: Prioritizes "A++" setups where a supply shock occurs in a fundamental deficit regime.
    *   **Trailing Risk Management**: Replaces static exits with a 3.0x ATR trailing stop that ratchets with winners.

---

## 🚀 Key Features

### 🛡️ Anti-Bias Engineering
*   **Temporal Validation**: Analyzes article metadata and content to estimate `source_publish_date`. Programmatically drops articles published outside the trade window.
*   **Date-Aware Entry**: Simulates trade entry at `max(quarter_start, catalyst_detection_date)`. You cannot trade a signal before the information exists.

### 📊 Interactive Dashboard
A premium **Streamlit** dashboard for auditing the "Clean Backtest" (2023-2026):
*   **Performance Overview**: Real-time equity curves comparing the Agentic Strategy vs. **S&P 500 (SPY)** and **Commodity Index (GSG)**.
*   **Agent Drill-Down**: Inspect the exact LLM reasoning, technical context, and source articles for every trade.
*   **Pipeline Visualization**: An interactive representation of the agentic workflow.

### 📈 Backtest Results (2023-2026)
*   **Base (Hold) Strategy**: +105.5% (High conviction, unmanaged)
*   **Trailing Stop Strategy**: +41.2% (Risk-managed, widened 3x ATR trail)
*   **S&P 500 Benchmark**: +61.4%
*   **Commodity Benchmark**: +48.7%

---

## 🛠️ Tech Stack
*   **Framework**: LangGraph, LangChain
*   **Intelligence**: Google Gemini 1.5 Pro / Flash
*   **Data APIs**: Tavily (Search), yfinance (Market Data)
*   **Visualization**: Streamlit, Plotly
*   **Validation**: Pydantic V2

---

## 🚦 Getting Started

### 1. Prerequisites
```bash
python -m venv venv
source venv/bin/activate  # .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file:
```env
GOOGLE_API_KEY=your_key
TAVILY_API_KEY=your_key
MODEL=gemini-1.5-pro
```

### 3. Usage
**Run the Backtest:**
```bash
python -m src.main
```

**Launch the Dashboard:**
```bash
streamlit run dashboard.py
```

---

## 📋 Methodology Note
This system favors **Asymmetry**. It seeks "Supply Shocks" (Left-tail events) in markets already showing "Fundamental Deficits" (Bullish regimes). By widening trailing stops, the system aims to capture the multi-month trending nature of commodity shocks while using LLM-based filtering to ignore retrospective "hindsight" news.
