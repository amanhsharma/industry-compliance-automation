from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DatasetUploadResponse(BaseModel):
    id: str
    tenant_id: str
    filename: str
    file_size_bytes: int
    row_count: int
    violation_count: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionRecordResponse(BaseModel):
    id: str
    dataset_id: str
    transaction_id: str
    account_id: str
    counterparty_name: Optional[str] = None
    counterparty_country: Optional[str] = None
    amount: float
    currency: str
    timestamp: Optional[datetime] = None
    kyc_status: str
    transaction_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
