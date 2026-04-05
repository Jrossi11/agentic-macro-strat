import os
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from ..schemas import Catalyst, CatalystList
from dotenv import load_dotenv

load_dotenv()

class AnalystAgent:
    def __init__(self):
        model_name = os.getenv("MODEL", "gemini-1.5-flash")
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.structured_llm = self.llm.with_structured_output(CatalystList)

    def extract_shocks(self, raw_content: List[str], quarter: str, quarter_start: str, quarter_end: str) -> List[Catalyst]:
        """
        Extracts supply and demand shocks from raw search results.
        Enforces temporal validation to prevent look-ahead bias.
        """
        if not raw_content:
            return []

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior macro-strat analyst. "
                       "You are analyzing data for quarter {quarter} ({quarter_start} to {quarter_end}). "
                       "Extract concrete supply and demand shock events. "
                       "\n"
                       "CRITICAL TEMPORAL RULES: "
                       "1. For each catalyst, you MUST estimate `source_publish_date` — the date the source article was PUBLISHED (not the event date). "
                       "   Look at URL patterns, article text, and context clues to determine this. "
                       "2. REJECT any article that was clearly published AFTER {quarter_end}. "
                       "   For example, if we are analyzing 2023-Q1, an article from 2025 looking back at 2023 events is INVALID — it introduces hindsight bias. "
                       "3. KEEP forward-looking catalysts: if an article published in {quarter} discusses a future supply disruption (e.g., a mine closure expected next year), "
                       "   that IS a valid signal — it reflects information available to traders during the quarter. "
                       "4. `date_detected` should be when the event was first reported/known. "
                       "5. `start_date`/`end_date` represent the impact window of the event on supply/demand. "
                       "\n"
                       "For each catalyst, estimate: "
                       "- likelihood_ratio (0.0 to 1.0) based on source consensus and reporting firmness "
                       "- start_date and end_date of impact (if known) "
                       "- supply_impact_value and unit if cited "
                       "- source_publish_date (YYYY-MM-DD) "
                       "Return a structured CatalystList."),
            ("user", "Quarter: {quarter} ({quarter_start} to {quarter_end})\n\n"
                     "Analyze the following search results and extract relevant catalysts:\n\n{content}")
        ])
        
        full_text = "\n\n---\n\n".join(raw_content)
        
        try:
            result = self.structured_llm.invoke(prompt.format(
                content=full_text,
                quarter=quarter,
                quarter_start=quarter_start,
                quarter_end=quarter_end
            ))
            raw_catalysts = result.catalysts if result else []
        except Exception as e:
            print(f"Error in Analyst extraction: {e}")
            return []

        # === HARD TEMPORAL FILTER (programmatic, not LLM-dependent) ===
        filtered = []
        for cat in raw_catalysts:
            pub_date = cat.source_publish_date or cat.date_detected or ""
            
            # Rule: Source must have been published ON OR BEFORE the quarter end
            if pub_date and pub_date > quarter_end:
                print(f"  [FILTERED] {cat.commodity}: '{cat.description[:60]}' — source published {pub_date} > {quarter_end}")
                continue
            
            filtered.append(cat)
        
        print(f"  Analyst: {len(raw_catalysts)} extracted, {len(raw_catalysts) - len(filtered)} filtered (temporal), {len(filtered)} kept")
        return filtered
