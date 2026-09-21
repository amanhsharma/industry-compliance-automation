from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.rule import ComplianceRule
from app.schemas.rule import RuleResponse, RuleToggle
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/rules", tags=["Compliance Rules"])

@router.get("", response_model=List[RuleResponse])
def list_compliance_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Retrieve tenant-specific and global rules
    rules = db.query(ComplianceRule).filter(
        (ComplianceRule.tenant_id == current_user.tenant_id) | (ComplianceRule.tenant_id == None)
    ).order_by(ComplianceRule.code.asc()).all()
    return rules

@router.patch("/{rule_id}/toggle", response_model=RuleResponse)
def toggle_rule_state(
    rule_id: str,
    payload: RuleToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    rule = db.query(ComplianceRule).filter(
        ComplianceRule.id == rule_id,
        (ComplianceRule.tenant_id == current_user.tenant_id) | (ComplianceRule.tenant_id == None)
    ).first()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.is_active = payload.is_active
    db.commit()
    db.refresh(rule)
    return rule
