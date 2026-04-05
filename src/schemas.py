from pydantic import BaseModel, Field
from typing import List, Optional

class Catalyst(BaseModel):
    """Represents a specific supply or demand shock event."""
    description: str = Field(description="Brief summary of the event")
    commodity: str = Field(description="Impacted commodity (e.g., Crude Oil, Copper)")
    impact_type: str = Field(description="Supply Shock, Demand Shock, or Geopolitical")
    severity: int = Field(description="1-10 scale of impact (10 being critical)")
    likelihood_ratio: float = Field(default=1.0, description="0-1 probability of the event being real/impactful")
    region: str = Field(description="Geographic region of the event")
    date_detected: str = Field(description="Date the event was noted in the search")
    start_date: Optional[str] = Field(None, description="Estimated start date of the event impact")
    end_date: Optional[str] = Field(None, description="Estimated end date of the event impact")
    supply_impact_value: Optional[float] = Field(None, description="Numerical volume of supply affected")
    supply_impact_unit: Optional[str] = Field(None, description="Unit for volume (e.g., bpd, tonnes)")
    source_url: Optional[str] = Field(description="Source of the information")
    source_publish_date: Optional[str] = Field(None, description="Estimated publication date of the source article (YYYY-MM-DD)")

class Signal(BaseModel):
    """Trading signal derived from catalysts with technical context."""
    commodity: str
    direction: str = Field(description="LONG or SHORT")
    weight_equal: float = Field(description="Equal-weighted allocation")
    weight_severity: float = Field(description="Severity-weighted allocation")
    
    # Advanced Trading Metrics
    take_profit: float = Field(description="Target exit price")
    stop_loss: float = Field(description="Stop loss exit price")
    asymmetry_ratio: float = Field(description="Reward/Risk ratio")
    upside_potential: float = Field(description="Estimated % gain to TP")
    downside_risk: float = Field(description="Estimated % loss to SL")
    is_priced_in: bool = Field(description="Whether the event appears already reflected in price")
    technical_context: str = Field(description="MA positions, recent highs/lows used for reasoning")
    
    rationale: str
    catalysts: List[Catalyst]

class QuarterResult(BaseModel):
    """Performance evaluation for a quarter."""
    quarter: str
    signals: List[Signal]
    pnl_equal: float
    pnl_severity: float
    pnl_likelihood_weighted: float = Field(description="PnL weighted by catalyst likelihood")
    pnl_active_risk: float = Field(description="PnL including TP/SL exits")
    summary: str

class CatalystList(BaseModel):
    """Container for a list of catalysts (for structured output)."""
    catalysts: List[Catalyst]
