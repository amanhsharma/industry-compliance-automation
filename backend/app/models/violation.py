import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class Violation(Base):
    __tablename__ = "violations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_id = Column(String(36), ForeignKey("dataset_uploads.id", ondelete="CASCADE"), nullable=False, index=True)
    record_id = Column(String(36), ForeignKey("transaction_records.id", ondelete="CASCADE"), nullable=False, index=True)

    rule_code = Column(String(50), nullable=False, index=True)
    rule_name = Column(String(150), nullable=False)
    severity = Column(String(20), default="HIGH", nullable=False, index=True) # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(50), default="OPEN", nullable=False, index=True) # OPEN, UNDER_REVIEW, RESOLVED
    message = Column(Text, nullable=False)
    details_json = Column(Text, default="{}", nullable=False)

    auditor_notes = Column(Text, nullable=True)
    assigned_to = Column(String(100), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    tenant = relationship("Tenant", back_populates="violations")
    dataset = relationship("DatasetUpload", back_populates="violations")
    record = relationship("TransactionRecord", back_populates="violations")
