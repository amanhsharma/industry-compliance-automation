import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from app.db.session import Base

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True) # Null for system default
    code = Column(String(50), index=True, nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False) # AML, SANCTIONS, KYC, FRAUD, VELOCITY
    severity = Column(String(20), default="HIGH", nullable=False) # CRITICAL, HIGH, MEDIUM, LOW
    regulatory_framework = Column(String(100), default="BSA / AML / OFAC", nullable=False)
    parameters_json = Column(Text, default="{}", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uix_tenant_rule_code'),
    )
