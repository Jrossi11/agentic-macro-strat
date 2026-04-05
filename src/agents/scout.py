from typing import List
from ..tools.tavily_search import HistoricalScout

COMMODITIES = ["Crude Oil", "Natural Gas", "Gold", "Silver", "Copper"]

class ScoutAgent:
    def __init__(self):
        self.scout_tool = HistoricalScout()

    def run_scout(self, start_date: str, end_date: str) -> List[str]:
        """
        Coordinates searches for all target commodities in a given range.
        """
        all_results = []
        for commodity in COMMODITIES:
            print(f"Scouting {commodity} shocks from {start_date} to {end_date}...")
            results = self.scout_tool.search_quarterly_shocks(commodity, start_date, end_date)
            # Add context for each search result to inform the Analyst which commodity it was for
            prefixed_results = [f"[COMMODITY: {commodity}] {res}" for res in results]
            all_results.extend(prefixed_results)
            
        return all_results
