from fastapi import APIRouter, Depends, status, Query, Header
from sqlalchemy.orm import Session
from typing import List

from backend.core.dependencies import get_db
from backend.modules.datasources.schemas import (
    DatasourceCreate, DatasourceUpdate, DatasourceOut,
    DatasourceConfigCreate, DatasourceConfigUpdate, DatasourceConfigOut
)
from backend.modules.datasources.repository import DatasourceRepository, DatasourceConfigRepository
from backend.modules.datasources.service import DatasourceService, DatasourceConfigService
from backend.common.responses import SuccessResponse
from backend.common.exceptions import ResourceNotFoundError

router = APIRouter()


def get_datasource_service(db: Session = Depends(get_db)):
    return DatasourceService(DatasourceRepository(db))


def get_config_service(db: Session = Depends(get_db)):
    return DatasourceConfigService(DatasourceConfigRepository(db), db)


# ============ DATASOURCE ENDPOINTS ============

@router.get("/datasources", response_model=List[DatasourceOut])
def get_all_datasources(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    active_only: bool = Query(False),
    service: DatasourceService = Depends(get_datasource_service)
):
    """Get all datasources for a tenant"""
    return service.get_all(tenant_id, active_only)


@router.get("/datasources/{datasource_id}", response_model=DatasourceOut)
def get_datasource(
    datasource_id: int,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: DatasourceService = Depends(get_datasource_service)
):
    """Get a single datasource by ID"""
    return service.get(tenant_id, datasource_id)


@router.post("/datasources", response_model=DatasourceOut, status_code=status.HTTP_201_CREATED)
def create_datasource(
    payload: DatasourceCreate,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: DatasourceService = Depends(get_datasource_service)
):
    """Create a new datasource"""
    return service.create(tenant_id, payload)


@router.put("/datasources/{datasource_id}", response_model=DatasourceOut)
def update_datasource(
    datasource_id: int,
    payload: DatasourceUpdate,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: DatasourceService = Depends(get_datasource_service)
):
    """Update an existing datasource"""
    return service.update(tenant_id, datasource_id, payload)


@router.delete("/datasources/{datasource_id}", response_model=SuccessResponse)
def delete_datasource(
    datasource_id: int,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: DatasourceService = Depends(get_datasource_service),
    config_service: DatasourceConfigService = Depends(get_config_service)
):
    """
    Delete a datasource and its associated config (CASCADE DELETE).
    
    When a datasource is deleted, this endpoint will:
    1. Find and delete the associated datasource-config (if exists)
    2. Delete the datasource itself
    """
    # Get the datasource to find its connection_key
    datasource = service.get(tenant_id, datasource_id)
    
    # Try to delete the associated config first (if it exists)
    if datasource.connection_key:
        try:
            config = config_service.get_by_name(tenant_id, datasource.connection_key)
            if config:
                config_service.delete(tenant_id, config.config_id)
        except ResourceNotFoundError:
            # Config doesn't exist, that's fine - continue with datasource deletion
            pass
    
    # Now delete the datasource
    service.delete(tenant_id, datasource_id)
    
    return SuccessResponse(message="Datasource and associated config deleted successfully")


# ============ DATASOURCE CONFIG ENDPOINTS ============

@router.get("/datasource-configs", response_model=List[DatasourceConfigOut])
def get_all_configs(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    active_only: bool = Query(False),
    service: DatasourceConfigService = Depends(get_config_service)
):
    """Get all datasource configs for a tenant"""
    return service.get_all(tenant_id, active_only)


@router.get("/datasource-configs/{config_id}", response_model=DatasourceConfigOut)
def get_config(
    config_id: int,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: DatasourceConfigService = Depends(get_config_service)
):
    """Get a single datasource config by ID"""
    return service.get(tenant_id, config_id)


@router.get("/datasource-configs/by-name/{name}", response_model=DatasourceConfigOut)
def get_config_by_name(
    name: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: DatasourceConfigService = Depends(get_config_service)
):
    """Get a datasource config by name"""
    return service.get_by_name(tenant_id, name)


@router.get("/datasource-configs/driver/{driver_family}", response_model=List[DatasourceConfigOut])
def get_configs_by_driver(
    driver_family: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: DatasourceConfigService = Depends(get_config_service)
):
    """Get all configs for a specific driver family"""
    return service.get_by_driver_family(tenant_id, driver_family)


@router.get("/datasource-configs/protocol/{protocol}", response_model=List[DatasourceConfigOut])
def get_configs_by_protocol(
    protocol: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: DatasourceConfigService = Depends(get_config_service)
):
    """Get all configs for a specific protocol"""
    return service.get_by_protocol(tenant_id, protocol)


@router.post("/datasource-configs", response_model=DatasourceConfigOut, status_code=status.HTTP_201_CREATED)
def create_config(
    payload: DatasourceConfigCreate,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: DatasourceConfigService = Depends(get_config_service)
):
    """
    Create a new datasource config.
    
    When created, automatically updates all datasources with matching driver_family
    to use this config's name as their connection_key.
    """
    return service.create(tenant_id, payload)


@router.put("/datasource-configs/{config_id}", response_model=DatasourceConfigOut)
def update_config(
    config_id: int,
    payload: DatasourceConfigUpdate,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: DatasourceConfigService = Depends(get_config_service)
):
    """
    Update an existing datasource config.
    
    When name changes, automatically updates datasources using the old name
    to use the new name as connection_key.
    """
    return service.update(tenant_id, config_id, payload)


@router.delete("/datasource-configs/{config_id}", response_model=SuccessResponse)
def delete_config(
    config_id: int,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: DatasourceConfigService = Depends(get_config_service)
):
    """
    Delete a datasource config WITHOUT affecting datasources.
    
    Datasources keep their connection_key so a new config can be added later.
    This allows the workflow:
    1. Delete config
    2. Datasource remains intact
    3. Add new config with same or different name
    """
    service.delete(tenant_id, config_id)
    return SuccessResponse(message="Datasource config deleted successfully")


@router.post("/datasource-configs/{config_id}/test", response_model=dict)
def test_connection(
    config_id: int,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: DatasourceConfigService = Depends(get_config_service)
):
    """Test connection for a datasource config"""
    return service.test_connection(tenant_id, config_id)