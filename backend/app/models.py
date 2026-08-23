from sqlalchemy import Nullable
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, JSON 
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Mapped, mapped_column
from app.database import Base 

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user")  # user / admin
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    facilities: Mapped[list["Facility"]] = relationship(back_populates="owner")

class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry_type: Mapped[str] = mapped_column(String(100), nullable=False)
    spcb_region: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner: Mapped["User"] = relationship(back_populates="facilities")
    readings: Mapped[list["EmissionReading"]] = relationship(back_populates="facility")
    
class EmissionReading(Base):
    __tablename__ = "emission_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"), nullable=False)
    parameter: Mapped[str] = mapped_column(String(100), nullable=False)  # PM2.5, SO2, BOD, etc.
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    source_file: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    facility: Mapped["Facility"] = relationship(back_populates="readings")
    violations: Mapped[list["Violation"]] = relationship(back_populates="reading")

    
    
class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    parameter: Mapped[str] = mapped_column(String(100), nullable=False)
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    applicable_industry_type: Mapped[str] = mapped_column(String(100), nullable=False)
    regulation_reference: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g. "CPCB-2019-SO2"

    violations: Mapped[list["Violation"]] = relationship(back_populates="rule")


class Violation(Base):
    __tablename__ = "violations"

    id: Mapped[int] = mapped_column(primary_key=True)
    reading_id: Mapped[int] = mapped_column(ForeignKey("emission_readings.id"), nullable=False)
    rule_id: Mapped[int] = mapped_column(ForeignKey("compliance_rules.id"), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)  # low/medium/high
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reading: Mapped["EmissionReading"] = relationship(back_populates="violations")
    rule: Mapped["ComplianceRule"] = relationship(back_populates="violations")

    
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # "UPLOAD_CSV", "LOGIN", etc.
    entity_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    entity_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)