import os
from typing import List
from tavily import TavilyClient
from dotenv import load_dotenv
from .cache import DiskCache

load_dotenv()

# Handle potential typo in .env from user
tavily_api_key = os.getenv("TAVILY_API_KEY") or os.getenv("TAVILIY_API_KEY")

class HistoricalScout:
    def __init__(self):
        if not tavily_api_key:
            raise ValueError("TAVILY_API_KEY not found in environment")
        self.client = TavilyClient(api_key=tavily_api_key)
        self.cache = DiskCache()

    def search_quarterly_shocks(self, commodity: str, start_date: str, end_date: str) -> List[str]:
        """
        Searches for supply/demand shocks for a specific commodity within a date range.
        Uses a local DiskCache to save tokens.
        """
        query = f"{commodity} supply and demand shocks, mining strikes, production disruptions, geopolitical news {start_date} to {end_date}"
        
        # Check cache first
        cached_results = self.cache.get(query, start_date, end_date)
        if cached_results:
            return cached_results

        # Tavily's search method with date range
        response = self.client.search(
            query=query,
            search_depth="advanced",
            max_results=10,
            include_raw_content=True
        )
        
        results = []
        for result in response.get("results", []):
            content = f"Title: {result.get('title')}\nSource: {result.get('url')}\nContent: {result.get('content')}"
            results.append(content)
        
        # Store in cache
        self.cache.set(query, start_date, end_date, results)
            
        return results
