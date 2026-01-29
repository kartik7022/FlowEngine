from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TenantBase(BaseModel):
    tenant_id: str
    tenant_name: Optional[str] = None
    is_active: bool = True


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    tenant_name: Optional[str] = None
    is_active: Optional[bool] = None


class TenantOut(TenantBase):
    created_at: datetime
    
    class Config:
        from_attributes = True


class TenantValidateResponse(BaseModel):
    valid: bool
    tenant_id: Optional[str] = None