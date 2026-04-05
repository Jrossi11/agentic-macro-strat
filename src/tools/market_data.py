import yfinance as yf
import pandas as pd
from typing import Dict, Tuple, Any

# Mapping of common commodity names to futures tickers
TICKER_MAP = {
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
}

class MarketData:
    def get_price_performance(self, commodity: str, start_date: str, end_date: str) -> float:
        """
        Returns percentage change for a commodity between two dates.
        Handles yfinance 0.2.x MultiIndex formats.
        """
        symbol = TICKER_MAP.get(commodity)
        if not symbol:
            return 0.0
            
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if data.empty:
            return 0.0
            
        # Robust column selection for yfinance 0.2.x+ MultiIndex
        # 'Close' is generally the standard ahora, but 'Adj Close' is also common.
        # We'll try 'Adj Close' then 'Close'
        col_to_use = None
        for col in ['Adj Close', 'Close']:
            if col in data.columns.get_level_values(0):
                col_to_use = col
                break
        
        if not col_to_use:
            return 0.0

        # If MultiIndex, first level is Price, second level is Ticker
        # We handle both single and multi-index here
        if isinstance(data.columns, pd.MultiIndex):
            prices = data[col_to_use][symbol]
        else:
            prices = data[col_to_use]
            
        first_price = float(prices.iloc[0])
        last_price = float(prices.iloc[-1])
        
        return float((last_price - first_price) / first_price)

    def get_technical_context(self, commodity: str, date: str) -> Dict[str, Any]:
        """
        Returns a technical snapshot for a commodity on a given date.
        Includes 50/200 MAs, 20-day High/Low, and ATR.
        """
        symbol = TICKER_MAP.get(commodity)
        if not symbol:
            return {}
            
        # Download roughly 1 year of data to ensure MAs are calculated
        start_history = (pd.to_datetime(date) - pd.DateOffset(days=300)).strftime('%Y-%m-%d')
        data = yf.download(symbol, start=start_history, end=date, progress=False)
        
        if data.empty:
            return {}
            
        # Extract Close prices safely
        if isinstance(data.columns, pd.MultiIndex):
            prices = data['Close'][symbol]
            highs = data['High'][symbol]
            lows = data['Low'][symbol]
        else:
            prices = data['Close']
            highs = data['High']
            lows = data['Low']
            
        # Calculations
        ma50 = prices.rolling(window=50).mean().iloc[-1]
        ma200 = prices.rolling(window=200).mean().iloc[-1]
        recent_20_high = highs.rolling(window=20).max().iloc[-1]
        recent_20_low = lows.rolling(window=20).min().iloc[-1]
        
        # Simple ATR (14-day)
        tr = pd.concat([
            highs - lows,
            (highs - prices.shift()).abs(),
            (lows - prices.shift()).abs()
        ], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        
        current_price = float(prices.iloc[-1])
        
        return {
            "current_price": current_price,
            "ma50": float(ma50),
            "ma200": float(ma200),
            "high20": float(recent_20_high),
            "low20": float(recent_20_low),
            "atr": float(atr),
            "symbol": symbol
        }

    def get_daily_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Returns daily OHLC for a given window.
        """
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            # Flatten or just return the relevant subset
            return data
        return data
