import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class TransactionRecord(Base):
    __tablename__ = "transaction_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_id = Column(String(36), ForeignKey("dataset_uploads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    transaction_id = Column(String(100), nullable=False, index=True)
    account_id = Column(String(100), nullable=False, index=True)
    counterparty_name = Column(String(255), nullable=True)
    counterparty_country = Column(String(10), nullable=True, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    timestamp = Column(DateTime, nullable=True)
    kyc_status = Column(String(50), default="VERIFIED", nullable=False) # VERIFIED, UNVERIFIED, PENDING
    transaction_type = Column(String(50), default="WIRE_OUT", nullable=False)
    raw_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    tenant = relationship("Tenant", back_populates="records")
    dataset = relationship("DatasetUpload", back_populates="records")
    violations = relationship("Violation", back_populates="record", cascade="all, delete-orphan")
