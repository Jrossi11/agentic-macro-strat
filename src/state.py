from typing import List, TypedDict, Annotated, Dict, Optional
from .schemas import Catalyst, Signal, QuarterResult

class AgentState(TypedDict):
    """The state of the multi-agent system for a given quarter."""
    quarter: str
    start_date: str
    end_date: str
    raw_search_results: List[str]
    market_balance: Dict[str, float]
    extracted_catalysts: List[Catalyst]
    signals: List[Signal]
    portfolio: List[Signal]
    pnl_summary: QuarterResult
