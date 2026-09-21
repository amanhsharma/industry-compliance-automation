from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.db.session import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.dataset import DatasetUpload
from app.models.record import TransactionRecord
from app.models.violation import Violation
from app.api.deps import get_current_user
from app.services.pdf_generator import generate_compliance_pdf_report

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/pdf")
def download_compliance_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Multi-tenant query scoping: aggregate metrics and records strictly for current user's tenant
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    total_records = db.query(func.count(TransactionRecord.id))\
        .filter(TransactionRecord.tenant_id == current_user.tenant_id).scalar() or 0

    total_violations = db.query(func.count(Violation.id))\
        .filter(Violation.tenant_id == current_user.tenant_id).scalar() or 0

    open_violations = db.query(func.count(Violation.id))\
        .filter(Violation.tenant_id == current_user.tenant_id, Violation.status == "OPEN").scalar() or 0

    clean_records = max(0, total_records - total_violations)
    compliance_score = round((clean_records / total_records) * 100.0, 1) if total_records > 0 else 100.0

    summary_data = {
        "compliance_score": compliance_score,
        "total_records": total_records,
        "total_violations": total_violations,
        "open_violations": open_violations
    }

    # Fetch violations with joined records
    violations = db.query(Violation).options(joinedload(Violation.record))\
        .filter(Violation.tenant_id == current_user.tenant_id)\
        .order_by(Violation.created_at.desc())\
        .limit(100)\
        .all()

    violations_data = []
    for v in violations:
        violations_data.append({
            "transaction_id": v.record.transaction_id if v.record else "N/A",
            "rule_code": v.rule_code,
            "rule_name": v.rule_name,
            "severity": v.severity,
            "status": v.status,
            "message": v.message
        })

    pdf_bytes = generate_compliance_pdf_report(
        tenant_name=tenant.name,
        summary_data=summary_data,
        violations_data=violations_data
    )

    filename = f"compliance_audit_report_{tenant.slug}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
