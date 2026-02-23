from datetime import datetime

from pydantic import BaseModel


class PrognosisReportOut(BaseModel):
    report_json: dict
    generated_at: datetime
    rate_limited: bool = False

    class Config:
        from_attributes = True


class RiskMetrics(BaseModel):
    burn_rate: float
    runway_months: float
    stability_ratio: float
    savings_ratio: float
    risk_score: int
    risk_label: str


class GoalEvaluation(BaseModel):
    goal_id: str
    goal_name: str
    status: str
    projected_value: float
    success_probability: float
    goal_pressure: float
    required_monthly_savings: float
    actual_monthly_savings: float


class AllocationRecommendation(BaseModel):
    recommended: dict[str, float]
    aggressive_alternative: dict[str, float] | None = None


class NarratorOutput(BaseModel):
    summary_bullets: list[str]
    cashflow_section: str
    goals_section: str
    allocation_section: str
    changes_since_last: str
    disclaimer: str
    markdown_body: str | None = None
