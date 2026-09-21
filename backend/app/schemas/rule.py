from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class RuleResponse(BaseModel):
    id: str
    code: str
    name: str
    description: str
    category: str
    severity: str
    regulatory_framework: str
    parameters_json: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RuleToggle(BaseModel):
    is_active: bool
