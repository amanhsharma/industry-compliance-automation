from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    tenant_name: str
    full_name: str
    email: EmailStr
    password: str
    role: Optional[str] = "compliance_officer"

class UserResponse(BaseModel):
    id: str
    tenant_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    tenant: Optional[TenantResponse] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
