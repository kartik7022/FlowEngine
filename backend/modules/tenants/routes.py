from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List

from backend.core.dependencies import get_db
from backend.modules.tenants.schemas import TenantCreate, TenantUpdate, TenantOut, TenantValidateResponse
from backend.modules.tenants.repository import TenantRepository
from backend.modules.tenants.service import TenantService
from backend.common.responses import SuccessResponse

router = APIRouter()


def get_service(db: Session = Depends(get_db)):
    return TenantService(TenantRepository(db))


@router.get("/tenants/validate/{tenant_id}", response_model=TenantValidateResponse)
def validate_tenant(
    tenant_id: str,
    service: TenantService = Depends(get_service)
):
    """Validate if tenant exists and is active"""
    is_valid = service.validate(tenant_id)
    return TenantValidateResponse(
        valid=is_valid,
        tenant_id=tenant_id if is_valid else None
    )


@router.get("/tenants", response_model=List[TenantOut])
def get_all_tenants(
    active_only: bool = Query(False),
    service: TenantService = Depends(get_service)
):
    """Get all tenants"""
    return service.get_all(active_only)


@router.get("/tenants/{tenant_id}", response_model=TenantOut)
def get_tenant(
    tenant_id: str,
    service: TenantService = Depends(get_service)
):
    """Get a single tenant by ID"""
    return service.get(tenant_id)


@router.post("/tenants", response_model=TenantOut, status_code=status.HTTP_201_CREATED)
def create_tenant(
    payload: TenantCreate,
    service: TenantService = Depends(get_service)
):
    """Create a new tenant"""
    return service.create(payload)


@router.put("/tenants/{tenant_id}", response_model=TenantOut)
def update_tenant(
    tenant_id: str,
    payload: TenantUpdate,
    service: TenantService = Depends(get_service)
):
    """Update an existing tenant"""
    return service.update(tenant_id, payload)


@router.delete("/tenants/{tenant_id}", response_model=SuccessResponse)
def delete_tenant(
    tenant_id: str,
    service: TenantService = Depends(get_service)
):
    """Delete a tenant"""
    service.delete(tenant_id)
    return SuccessResponse(message=f"Tenant '{tenant_id}' deleted successfully")