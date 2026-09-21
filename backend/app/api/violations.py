from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.user import User
from app.models.violation import Violation
from app.models.record import TransactionRecord
from app.schemas.violation import ViolationResponse, ViolationUpdate
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/violations", tags=["Violations"])

@router.get("", response_model=List[ViolationResponse])
def list_violations(
    severity: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    rule_code: Optional[str] = Query(None),
    dataset_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Multi-tenant query scoping: strictly bound to current_user.tenant_id
    query = db.query(Violation).options(joinedload(Violation.record))\
        .filter(Violation.tenant_id == current_user.tenant_id)

    if severity:
        query = query.filter(Violation.severity == severity.upper())
    if status_filter:
        query = query.filter(Violation.status == status_filter.upper())
    if rule_code:
        query = query.filter(Violation.rule_code == rule_code)
    if dataset_id:
        query = query.filter(Violation.dataset_id == dataset_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.join(TransactionRecord, Violation.record_id == TransactionRecord.id)\
            .filter(
                (Violation.message.ilike(search_pattern)) |
                (Violation.rule_name.ilike(search_pattern)) |
                (TransactionRecord.transaction_id.ilike(search_pattern)) |
                (TransactionRecord.counterparty_name.ilike(search_pattern))
            )

    violations = query.order_by(Violation.created_at.desc()).offset(skip).limit(limit).all()
    return violations

@router.get("/{violation_id}", response_model=ViolationResponse)
def get_violation(
    violation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Multi-tenant query scoping: Ensure violation belongs to tenant
    violation = db.query(Violation).options(joinedload(Violation.record))\
        .filter(
            Violation.id == violation_id,
            Violation.tenant_id == current_user.tenant_id
        ).first()

    if not violation:
        raise HTTPException(status_code=404, detail="Violation record not found")

    return violation

@router.patch("/{violation_id}", response_model=ViolationResponse)
def update_violation_status(
    violation_id: str,
    payload: ViolationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "compliance_officer"]))
):
    # Multi-tenant query scoping: Only allow updates within tenant domain
    violation = db.query(Violation).options(joinedload(Violation.record)).filter(
        Violation.id == violation_id,
        Violation.tenant_id == current_user.tenant_id
    ).first()

    if not violation:
        raise HTTPException(status_code=404, detail="Violation record not found")

    if payload.status:
        new_status = payload.status.upper()
        if new_status not in ["OPEN", "UNDER_REVIEW", "RESOLVED"]:
            raise HTTPException(status_code=400, detail="Invalid status transition")
        violation.status = new_status
        if new_status == "RESOLVED":
            violation.resolved_at = datetime.now(timezone.utc)
            violation.resolved_by_id = current_user.id
        elif violation.status != "RESOLVED":
            violation.resolved_at = None
            violation.resolved_by_id = None

    if payload.auditor_notes is not None:
        violation.auditor_notes = payload.auditor_notes

    if payload.assigned_to is not None:
        violation.assigned_to = payload.assigned_to

    db.commit()
    db.refresh(violation)
    return violation
