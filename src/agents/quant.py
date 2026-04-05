import os
import pandas as pd
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from ..schemas import Catalyst, Signal, QuarterResult
from ..tools.market_data import MarketData
from dotenv import load_dotenv

load_dotenv()

class QuantAgent:
    def __init__(self):
        self.market_tool = MarketData()
        model_name = os.getenv("MODEL", "gemini-1.5-flash")
        self.llm = ChatGoogleGenerativeAI(
            model=model_name, 
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        # We'll use a wrapper later for structured output if needed, 
        # but for now we'll process each commodity group.

    def generate_signals(self, catalysts: List[Catalyst], quarter_start: str, market_balances: Dict[str, float]) -> List[Signal]:
        """
        Translates catalysts into trading signals using Technical Analysis AND Macro Balance context.
        Hunts for Asymmetry and 'Priced In' events.
        """
        if not catalysts:
            return []

        # Group catalysts by commodity
        by_commodity = {}
        for c in catalysts:
            if c.commodity not in by_commodity:
                by_commodity[c.commodity] = []
            by_commodity[c.commodity].append(c)

        signals = []
        for commodity, cats in by_commodity.items():
            # 1. Fetch Technical Context
            tech = self.market_tool.get_technical_context(commodity, quarter_start)
            if not tech:
                continue

            balance_score = market_balances.get(commodity, 0.0)
            balance_desc = "Deficit (Bullish Bias)" if balance_score > 0.3 else "Surplus (Bearish Bias)" if balance_score < -0.3 else "Balanced"

            # 2. Reasoning via LLM
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a senior macro quantitative trader. Your goal is to detect ASYMMETRY. "
                           "You are given a fundamental supply/demand catalysts, technical price action, AND the broad market balance. "
                           "CRITICAL: A supply shock in a 'Deficit' regime is an A++ high conviction trade. "
                           "If the market is in a 'Surplus', be more skeptical of upside potential. "
                           "Determine if the move is already 'priced in' by looking at the technicals. "
                           "Weight your signal based on the synergy between the Shock and the Balance. "
                           "Return a structured JSON match for the Signal schema."),
                ("user", "Commodity: {commodity}\n"
                         "Catalysts: {catalysts}\n"
                         "Market Balance: {balance_desc} (Score: {balance})\n"
                         "Technical Snapshot: {tech}\n"
                         "Analyze for asymmetry and 'priced in' risk.")
            ])
            
            # Format cats for the prompt
            cat_text = "\n".join([f"- {c.description} (Severity: {c.severity}, Likelihood: {c.likelihood_ratio})" for c in cats])
            
            try:
                # Use structured output for each signal
                structured_llm = self.llm.with_structured_output(Signal)
                signal = structured_llm.invoke(prompt.format(
                    commodity=commodity,
                    catalysts=cat_text,
                    balance_desc=balance_desc,
                    balance=balance_score,
                    tech=str(tech)
                ))
                if signal:
                    # Inject catalysts back in
                    signal.catalysts = cats
                    signals.append(signal)
            except Exception as e:
                print(f"Error reasoning for {commodity}: {e}")

        # Normalize weights
        if signals:
            total_severity = sum(s.weight_severity for s in signals)
            for s in signals:
                s.weight_equal = 1.0 / len(signals)
                if total_severity > 0:
                    s.weight_severity = s.weight_severity / total_severity
                else:
                    s.weight_severity = s.weight_equal

        return signals

    def evaluate_performance(self, quarter: str, signals: List[Signal], start_date: str, end_date: str) -> QuarterResult:
        """
        Simulates intra-quarter exits (TP/SL) using daily High/Low data.
        Uses the ACTUAL entry date = max(quarter_start, latest catalyst detection date).
        """
        pnl_equal = 0.0
        pnl_severity = 0.0
        pnl_likelihood = 0.0
        pnl_active = 0.0
        
        for s in signals:
            # Compute the actual entry date: you can't trade before the catalyst is known
            catalyst_dates = [c.date_detected for c in s.catalysts if c.date_detected]
            latest_detected = max(catalyst_dates) if catalyst_dates else start_date
            actual_entry = max(start_date, latest_detected)
            
            # Clamp: if the latest catalyst was detected after quarter end, skip
            if actual_entry >= end_date:
                print(f"  [SKIP] {s.commodity}: latest catalyst detected {latest_detected} >= quarter end {end_date}")
                continue
            
            # 1. Get performance from actual entry date to quarter end
            actual_perf = self.market_tool.get_price_performance(s.commodity, actual_entry, end_date)
            
            # 2. Get likelihood-weighted perf
            avg_likelihood = sum(c.likelihood_ratio for c in s.catalysts) / len(s.catalysts)
            likelihood_weighted_perf = actual_perf * avg_likelihood

            # 3. Simulate Active Exit (TP/SL) from actual entry date
            active_perf = self._simulate_exit(s, actual_entry, end_date)
            
            # Aggregate
            pnl_equal += s.weight_equal * actual_perf
            pnl_severity += s.weight_severity * actual_perf
            pnl_likelihood += s.weight_severity * likelihood_weighted_perf
            pnl_active += s.weight_severity * active_perf
            
        summary = f"Backtest {quarter}: Base PnL: {pnl_severity:.2%}, Active (TP/SL) PnL: {pnl_active:.2%}, Likelihood PnL: {pnl_likelihood:.2%}"
        
        return QuarterResult(
            quarter=quarter,
            signals=signals,
            pnl_equal=pnl_equal,
            pnl_severity=pnl_severity,
            pnl_likelihood_weighted=pnl_likelihood,
            pnl_active_risk=pnl_active,
            summary=summary
        )

    def _simulate_exit(self, signal: Signal, start_date: str, end_date: str) -> float:
        """
        Trailing Stop simulation.
        - No fixed Take Profit — lets winners run.
        - Stop Loss trails behind the best price by 2x ATR (initial distance).
        - For LONG: trail ratchets UP as price rises. Exit if low touches trail.
        - For SHORT: trail ratchets DOWN as price falls. Exit if high touches trail.
        """
        from ..tools.market_data import TICKER_MAP
        symbol = TICKER_MAP.get(signal.commodity)
        if not symbol: return 0.0
        
        data = self.market_tool.get_daily_data(symbol, start_date, end_date)
        if data.empty: return 0.0
        
        # Safe extraction for MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            highs = data['High'][symbol]
            lows = data['Low'][symbol]
            closes = data['Close'][symbol]
        else:
            highs = data['High']
            lows = data['Low']
            closes = data['Close']
            
        entry_price = float(closes.iloc[0])
        
        # Calculate the initial trail distance from the Quant's SL
        # Widen by 1.5x for quarterly timeframe — gives room for intra-quarter noise
        TRAIL_MULTIPLIER = 1.5
        if signal.direction == "LONG":
            trail_distance = (entry_price - signal.stop_loss) * TRAIL_MULTIPLIER
            best_price = entry_price
            trailing_stop = entry_price - trail_distance
        else:  # SHORT
            trail_distance = (signal.stop_loss - entry_price) * TRAIL_MULTIPLIER
            best_price = entry_price
            trailing_stop = entry_price + trail_distance
        
        # Ensure trail_distance is positive and reasonable
        if trail_distance <= 0:
            trail_distance = entry_price * 0.05  # fallback 5%
            if signal.direction == "LONG":
                trailing_stop = entry_price - trail_distance
            else:
                trailing_stop = entry_price + trail_distance
        
        for i in range(len(data)):
            day_high = float(highs.iloc[i])
            day_low = float(lows.iloc[i])
            day_close = float(closes.iloc[i])
            
            if signal.direction == "LONG":
                # Update best price and ratchet trail up
                if day_close > best_price:
                    best_price = day_close
                    trailing_stop = best_price - trail_distance
                
                # Check if trailing stop was hit
                if day_low <= trailing_stop:
                    return (trailing_stop - entry_price) / entry_price
            
            else:  # SHORT
                # Update best price (lowest) and ratchet trail down
                if day_close < best_price:
                    best_price = day_close
                    trailing_stop = best_price + trail_distance
                
                # Check if trailing stop was hit
                if day_high >= trailing_stop:
                    return (entry_price - trailing_stop) / entry_price
        
        # If never hit, return end-of-quarter performance
        final_price = float(closes.iloc[-1])
        if signal.direction == "LONG":
            return (final_price - entry_price) / entry_price
        else:
            return (entry_price - final_price) / entry_price
