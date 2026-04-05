import json
from .graph import app
from typing import List

def generate_backtest_windows():
    """Generates quarterly windows from 2023-Q1 to 2026-Q1."""
    windows = []
    for year in [2023, 2024, 2025, 2026]:
        for q in range(1, 5):
            if year == 2026 and q > 1:
                break
                
            quarter = f"{year}-Q{q}"
            if q == 1: start, end = f"{year}-01-01", f"{year}-03-31"
            elif q == 2: start, end = f"{year}-04-01", f"{year}-06-30"
            elif q == 3: start, end = f"{year}-07-01", f"{year}-09-30"
            else: start, end = f"{year}-10-01", f"{year}-12-31"
            
            windows.append({"quarter": quarter, "start": start, "end": end})
    return windows

def run_backtest():
    """
    Runs the multi-agent backtest for each quarter.
    """
    windows = generate_backtest_windows()
    results = []

    for window in windows:
        print(f"\n🚀 Running Backtest for {window['quarter']}...")
        initial_state = {
            "quarter": window["quarter"],
            "start_date": window["start"],
            "end_date": window["end"],
            "raw_search_results": [],
            "market_balance": {},
            "extracted_catalysts": [],
            "signals": [],
            "portfolio": [],
            "pnl_summary": None
        }

        # Run Graph
        final_state = app.invoke(initial_state)
        
        if final_state.get("pnl_summary"):
            summary = final_state["pnl_summary"]
            print(f"✅ {summary.summary}")
            results.append(summary.dict())
        else:
            print(f"❌ Failed to generate results for {window['quarter']}")

    # Save all results
    output_file = "backtest_results_2023_2026.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\n📊 Full backtest results saved to {output_file}")

if __name__ == "__main__":
    run_backtest()
