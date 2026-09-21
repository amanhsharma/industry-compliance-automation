from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ViolationRecordSummary(BaseModel):
    transaction_id: str
    account_id: str
    counterparty_name: Optional[str] = None
    counterparty_country: Optional[str] = None
    amount: float
    currency: str
    timestamp: Optional[datetime] = None
    kyc_status: str
    transaction_type: str

    model_config = ConfigDict(from_attributes=True)

class ViolationResponse(BaseModel):
    id: str
    tenant_id: str
    dataset_id: str
    record_id: str
    rule_code: str
    rule_name: str
    severity: str
    status: str
    message: str
    details_json: str
    auditor_notes: Optional[str] = None
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    record: Optional[ViolationRecordSummary] = None

    model_config = ConfigDict(from_attributes=True)

class ViolationUpdate(BaseModel):
    status: Optional[str] = None
    auditor_notes: Optional[str] = None
    assigned_to: Optional[str] = None
