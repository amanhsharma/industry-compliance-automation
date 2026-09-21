from typing import List, Dict
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.user import User
from app.models.dataset import DatasetUpload
from app.models.record import TransactionRecord
from app.models.violation import Violation
from app.schemas.dashboard import (
    DashboardSummaryResponse, SeverityCount, StatusCount, RuleBreakdown, TrendItem
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Multi-tenant query scoping: strictly bound to current_user.tenant_id
    tenant_id = current_user.tenant_id

    total_records = db.query(func.count(TransactionRecord.id))\
        .filter(TransactionRecord.tenant_id == tenant_id).scalar() or 0

    total_datasets = db.query(func.count(DatasetUpload.id))\
        .filter(DatasetUpload.tenant_id == tenant_id).scalar() or 0

    total_violations = db.query(func.count(Violation.id))\
        .filter(Violation.tenant_id == tenant_id).scalar() or 0

    open_violations = db.query(func.count(Violation.id))\
        .filter(Violation.tenant_id == tenant_id, Violation.status == "OPEN").scalar() or 0

    under_review_violations = db.query(func.count(Violation.id))\
        .filter(Violation.tenant_id == tenant_id, Violation.status == "UNDER_REVIEW").scalar() or 0

    resolved_violations = db.query(func.count(Violation.id))\
        .filter(Violation.tenant_id == tenant_id, Violation.status == "RESOLVED").scalar() or 0

    # Calculate compliance rate
    if total_records > 0:
        clean_records = max(0, total_records - total_violations)
        compliance_score = round((clean_records / total_records) * 100.0, 1)
    else:
        compliance_score = 100.0

    # Severity breakdown
    sev_query = db.query(Violation.severity, func.count(Violation.id))\
        .filter(Violation.tenant_id == tenant_id)\
        .group_by(Violation.severity).all()
    sev_map = {s: c for s, c in sev_query}
    severity_breakdown = [
        SeverityCount(severity="CRITICAL", count=sev_map.get("CRITICAL", 0)),
        SeverityCount(severity="HIGH", count=sev_map.get("HIGH", 0)),
        SeverityCount(severity="MEDIUM", count=sev_map.get("MEDIUM", 0)),
        SeverityCount(severity="LOW", count=sev_map.get("LOW", 0)),
    ]

    # Status breakdown
    status_query = db.query(Violation.status, func.count(Violation.id))\
        .filter(Violation.tenant_id == tenant_id)\
        .group_by(Violation.status).all()
    stat_map = {s: c for s, c in status_query}
    status_breakdown = [
        StatusCount(status="OPEN", count=stat_map.get("OPEN", 0)),
        StatusCount(status="UNDER_REVIEW", count=stat_map.get("UNDER_REVIEW", 0)),
        StatusCount(status="RESOLVED", count=stat_map.get("RESOLVED", 0)),
    ]

    # Rule distribution
    rule_query = db.query(Violation.rule_code, Violation.rule_name, Violation.severity, func.count(Violation.id))\
        .filter(Violation.tenant_id == tenant_id)\
        .group_by(Violation.rule_code, Violation.rule_name, Violation.severity)\
        .order_by(func.count(Violation.id).desc()).all()
    rule_distribution = [
        RuleBreakdown(
            rule_code=code,
            rule_name=name,
            severity=sev,
            count=cnt
        )
        for code, name, sev, cnt in rule_query
    ]

    # Trend items (last 7 days)
    trends = []
    today = datetime.now(timezone.utc).date()
    for i in range(6, -1, -1):
        day_date = today - timedelta(days=i)
        day_str = day_date.strftime("%b %d")
        
        # Get count of violations created on this day
        v_day_count = db.query(func.count(Violation.id))\
            .filter(
                Violation.tenant_id == tenant_id,
                func.date(Violation.created_at) == day_date
            ).scalar() or 0

        # Get count of records created on this day
        r_day_count = db.query(func.count(TransactionRecord.id))\
            .filter(
                TransactionRecord.tenant_id == tenant_id,
                func.date(TransactionRecord.created_at) == day_date
            ).scalar() or 0

        clean_day = max(0, r_day_count - v_day_count)
        trends.append(TrendItem(date=day_str, violations=v_day_count, clean_records=clean_day))

    return DashboardSummaryResponse(
        total_records=total_records,
        total_datasets=total_datasets,
        total_violations=total_violations,
        open_violations=open_violations,
        under_review_violations=under_review_violations,
        resolved_violations=resolved_violations,
        compliance_score=compliance_score,
        severity_breakdown=severity_breakdown,
        status_breakdown=status_breakdown,
        rule_distribution=rule_distribution,
        trends=trends
    )
