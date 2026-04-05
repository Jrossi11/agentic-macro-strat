from langgraph.graph import StateGraph, END
from .state import AgentState
from .agents.scout import HistoricalScout
from .agents.analyst import AnalystAgent
from .agents.quant import QuantAgent
from .agents.macro_scout import MacroScoutAgent

# Initialize Agents
scout = HistoricalScout()
analyst = AnalystAgent()
quant = QuantAgent()
macro_scout = MacroScoutAgent()

def scout_node(state: AgentState):
    """Fetches raw search results for the given quarter."""
    print(f"--- Scouting Quarter: {state['quarter']} ---")
    
    commodities = ["Crude Oil", "Natural Gas", "Gold", "Silver", "Copper"]
    all_results = []
    for c in commodities:
        print(f"Scouting {c} shocks from {state['start_date']} to {state['end_date']}...")
        results = scout.search_quarterly_shocks(c, state['start_date'], state['end_date'])
        all_results.extend(results)
        
    return {"raw_search_results": all_results}

def macro_scout_node(state: AgentState):
    """Fetches global supply/demand balance from authoritative agencies."""
    print(f"--- Macro Research: {state['quarter']} ---")
    commodities = ["Crude Oil", "Natural Gas", "Gold", "Silver", "Copper"]
    balances = macro_scout.get_all_balances(commodities, state['quarter'])
    return {"market_balance": balances}

def analyst_node(state: AgentState):
    """Extracts catalysts from raw search results with temporal validation."""
    print(f"--- Analyzing Shocks for {state['quarter']} ---")
    catalysts = analyst.extract_shocks(
        state['raw_search_results'],
        quarter=state['quarter'],
        quarter_start=state['start_date'],
        quarter_end=state['end_date']
    )
    return {"extracted_catalysts": catalysts}

def quant_node(state: AgentState):
    """Generates signals and evaluates performance with technical and macro context."""
    print(f"--- Quant Portfolio Generation: {state['quarter']} ---")
    signals = quant.generate_signals(
        state['extracted_catalysts'], 
        state['start_date'],
        state['market_balance']
    )
    pnl_summary = quant.evaluate_performance(
        state['quarter'], 
        signals, 
        state['start_date'], 
        state['end_date']
    )
    return {"signals": signals, "pnl_summary": pnl_summary}

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("scout", scout_node)
workflow.add_node("macro_scout", macro_scout_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("quant", quant_node)

workflow.set_entry_point("scout")
workflow.add_edge("scout", "macro_scout")
workflow.add_edge("macro_scout", "analyst")
workflow.add_edge("analyst", "quant")
workflow.add_edge("quant", END)

# Compile
app = workflow.compile()
