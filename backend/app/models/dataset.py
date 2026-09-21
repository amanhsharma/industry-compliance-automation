import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class DatasetUpload(Base):
    __tablename__ = "dataset_uploads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, default=0, nullable=False)
    row_count = Column(Integer, default=0, nullable=False)
    violation_count = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="PROCESSING", nullable=False) # PROCESSING, COMPLETED, FAILED
    uploaded_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    tenant = relationship("Tenant", back_populates="datasets")
    uploader = relationship("User", back_populates="uploads")
    records = relationship("TransactionRecord", back_populates="dataset", cascade="all, delete-orphan")
    violations = relationship("Violation", back_populates="dataset", cascade="all, delete-orphan")
