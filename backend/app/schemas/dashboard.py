from typing import List, Dict
from pydantic import BaseModel

class SeverityCount(BaseModel):
    severity: str
    count: int

class StatusCount(BaseModel):
    status: str
    count: int

class RuleBreakdown(BaseModel):
    rule_code: str
    rule_name: str
    severity: str
    count: int

class TrendItem(BaseModel):
    date: str
    violations: int
    clean_records: int

class DashboardSummaryResponse(BaseModel):
    total_records: int
    total_datasets: int
    total_violations: int
    open_violations: int
    under_review_violations: int
    resolved_violations: int
    compliance_score: float # Percentage 0.0 - 100.0%
    severity_breakdown: List[SeverityCount]
    status_breakdown: List[StatusCount]
    rule_distribution: List[RuleBreakdown]
    trends: List[TrendItem]
