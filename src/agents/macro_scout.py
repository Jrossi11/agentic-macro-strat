import os
from typing import Dict, List
from tavily import TavilyClient
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from ..tools.cache import DiskCache

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY") or os.getenv("TAVILIY_API_KEY")

class MacroScoutAgent:
    def __init__(self):
        if not tavily_api_key:
            raise ValueError("TAVILY_API_KEY for MacroScout not found")
        self.client = TavilyClient(api_key=tavily_api_key)
        self.cache = DiskCache()
        model_name = os.getenv("MODEL", "gemini-1.5-flash")
        self.llm = ChatGoogleGenerativeAI(
            model=model_name, 
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    def get_market_balance(self, commodity: str, quarter: str) -> float:
        """
        Searches authoritative agencies (USGS, EIA, IEA) to determine 
        if a commodity was in Deficit (1.0) or Surplus (-1.0).
        """
        # Targeting specific domains for Copper vs Energy
        domains = ["eia.gov", "iea.org", "opec.org"]
        if commodity.lower() in ["copper", "gold", "silver"]:
            domains.append("usgs.gov")
            domains.append("mining.com")

        query = f"site:{' OR site:'.join(domains)} {commodity} global supply demand balance {quarter} report"
        
        # Check Cache
        cached = self.cache.get(query, quarter, quarter) # Use quarter as date proxy
        if cached:
            raw_text = "\n".join(cached)
        else:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_raw_content=True
            )
            results = [f"Source: {r.get('url')}\nContent: {r.get('content')}" for r in response.get("results", [])]
            self.cache.set(query, quarter, quarter, results)
            raw_text = "\n".join(results)

        # Reasoning via LLM to extract the balance score
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a macro-economic analyst. Based on the reports provided, "
                       "determine if the market for the specified commodity was in a 'Deficit' or 'Surplus'. "
                       "Return a single numerical score between -1.0 (Extreme Surplus) and 1.0 (Extreme Deficit). "
                       "0.0 means Balanced. "
                       "Focus on EIA/USGS data if available. Return JUST the number."),
            ("user", "Commodity: {commodity}\nQuarter: {quarter}\nReports: {text}")
        ])
        
        try:
            result = self.llm.invoke(prompt.format(commodity=commodity, quarter=quarter, text=raw_text))
            return float(result.content.strip())
        except Exception:
            return 0.0

    def get_all_balances(self, commodities: List[str], quarter: str) -> Dict[str, float]:
        balances = {}
        for c in commodities:
            balances[c] = self.get_market_balance(c, quarter)
        return balances
