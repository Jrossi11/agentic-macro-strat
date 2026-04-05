import os
from src.agents.scout import HistoricalScout
from src.agents.macro_scout import MacroScoutAgent

def generate_quarters():
    quarters = []
    for year in [2023, 2024, 2025, 2026]:
        for q in range(1, 5):
            if year == 2026 and q > 1:
                break
            q_str = f"{year}-Q{q}"
            
            # Simple date mapping
            if q == 1: start, end = f"{year}-01-01", f"{year}-03-31"
            elif q == 2: start, end = f"{year}-04-01", f"{year}-06-30"
            elif q == 3: start, end = f"{year}-07-01", f"{year}-09-30"
            else: start, end = f"{year}-10-01", f"{year}-12-31"
            
            quarters.append({"quarter": q_str, "start": start, "end": end})
    return quarters

def run_archive():
    print("🚀 Starting Bulk Search Archive (2023-2026)...")
    scout = HistoricalScout()
    macro_scout = MacroScoutAgent()
    
    commodities = ["Crude Oil", "Natural Gas", "Gold", "Silver", "Copper"]
    quarters = generate_quarters()
    
    total_tasks = len(commodities) * len(quarters) * 2 # Shock + Macro
    completed = 0
    
    for q_data in quarters:
        q = q_data["quarter"]
        start = q_data["start"]
        end = q_data["end"]
        
        print(f"\n--- Checking Quarter: {q} ---")
        for commodity in commodities:
            # 1. Shock Search
            print(f"Scouting {commodity} Shocks...")
            scout.search_quarterly_shocks(commodity, start, end)
            completed += 1
            
            # 2. Macro Balance Search
            print(f"Scouting {commodity} Macro Balance (USGS/EIA)...")
            macro_scout.get_market_balance(commodity, q)
            completed += 1
            
            print(f"Progress: {completed}/{total_tasks}")

    print("\n✅ Archive Complete! data/tavily_cache.json is now fully populated.")

if __name__ == "__main__":
    run_archive()
