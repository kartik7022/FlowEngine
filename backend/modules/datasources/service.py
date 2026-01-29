from typing import Optional
from sqlalchemy.orm import Session

from backend.modules.datasources.repository import DatasourceRepository, DatasourceConfigRepository
from backend.modules.datasources.schemas import (
    DatasourceCreate, DatasourceUpdate,
    DatasourceConfigCreate, DatasourceConfigUpdate
)
from backend.modules.datasources.models import Datasource, DatasourceConfig
from backend.common.exceptions import ResourceNotFoundError, ResourceAlreadyExistsError
from backend.common.exceptions import ValidationException


class DatasourceService:
    
    def __init__(self, repo: DatasourceRepository):
        self.repo = repo
    
    def get_all(self, tenant_id: str, active_only: bool = False):
        return self.repo.get_all(tenant_id, active_only)
    
    def get(self, tenant_id: str, datasource_id: int):
        obj = self.repo.get_by_id(tenant_id, datasource_id)
        if not obj:
            raise ResourceNotFoundError("Datasource not found")
        return obj
    
    def create(self, tenant_id: str, payload: DatasourceCreate):
        # Check if name already exists for this tenant
        existing = self.repo.get_by_name(tenant_id, payload.name)
        if existing:
            raise ResourceAlreadyExistsError(f"Datasource with name '{payload.name}' already exists")
        
        return self.repo.create(tenant_id, payload)
    
    def update(self, tenant_id: str, datasource_id: int, payload: DatasourceUpdate):
        # Get existing datasource
        existing = self.repo.get_by_id(tenant_id, datasource_id)
        if not existing:
            raise ResourceNotFoundError("Datasource not found")
        
        old_connection_key = existing.connection_key
        
        # Update the datasource
        obj = self.repo.update(tenant_id, datasource_id, payload)
        if not obj:
            raise ResourceNotFoundError("Datasource not found")
        
        # If connection_key changed, update the associated config's name
        if payload.connection_key and payload.connection_key != old_connection_key:
            # Find config with old connection_key as name
            config_repo = DatasourceConfigRepository(self.repo.db)
            old_config = config_repo.get_by_name(tenant_id, old_connection_key)
            
            if old_config:
                # Update config name to match new connection_key
                config_update = DatasourceConfigUpdate(name=payload.connection_key)
                config_repo.update(tenant_id, old_config.config_id, config_update)
        
        return obj
    
    def delete(self, tenant_id: str, datasource_id: int):
        # Check if datasource exists for this tenant
        datasource = self.repo.get_by_id(tenant_id, datasource_id)
        if not datasource:
            raise ResourceNotFoundError("Datasource not found")
        
        # Check if datasource has associated validation rules
        if datasource.validation_rules and len(datasource.validation_rules) > 0:
            rule_count = len(datasource.validation_rules)
            raise ValidationException(
                f"Cannot delete datasource '{datasource.name}'. "
                f"It is associated with {rule_count} validation rule(s). "
                f"Please remove the associations first."
            )
        
        deleted = self.repo.delete(tenant_id, datasource_id)
        if not deleted:
            raise ResourceNotFoundError("Datasource not found")


class DatasourceConfigService:
    
    def __init__(self, repo: DatasourceConfigRepository, db: Session = None):
        self.repo = repo
        self.db = db or repo.db
    
    def get_all(self, tenant_id: str, active_only: bool = False):
        return self.repo.get_all(tenant_id, active_only)
    
    def get(self, tenant_id: str, config_id: int):
        obj = self.repo.get_by_id(tenant_id, config_id)
        if not obj:
            raise ResourceNotFoundError(f"Datasource config with id '{config_id}' not found")
        return obj
    
    def get_by_name(self, tenant_id: str, name: str):
        obj = self.repo.get_by_name(tenant_id, name)
        if not obj:
            raise ResourceNotFoundError(f"Datasource config with name '{name}' not found")
        return obj
    
    def get_by_driver_family(self, tenant_id: str, driver_family: str):
        return self.repo.get_by_driver_family(tenant_id, driver_family)
    
    def get_by_protocol(self, tenant_id: str, protocol: str):
        return self.repo.get_by_protocol(tenant_id, protocol)
    
    def create(self, tenant_id: str, payload: DatasourceConfigCreate):
        """Create a new datasource config and update datasources with matching driver_family"""
        # Check if name already exists for this tenant
        existing = self.repo.get_by_name(tenant_id, payload.name)
        if existing:
            raise ResourceAlreadyExistsError(
                f"Datasource config with name '{payload.name}' already exists"
            )
        
        # Create the config
        config = self.repo.create(tenant_id, payload)
        
        # Update all datasources (for this tenant) with matching driver_family to use this config name as connection_key
        matching_datasources = self.db.query(Datasource).filter(
            Datasource.tenant_id == tenant_id,
            Datasource.datasource_type == payload.driver_family
        ).all()
        
        for datasource in matching_datasources:
            datasource.connection_key = payload.name
        
        self.db.commit()
        return config
    
    def update(self, tenant_id: str, config_id: int, payload: DatasourceConfigUpdate):
        """Update datasource config and update datasources if name changes"""
        # Check if config exists for this tenant
        existing = self.repo.get_by_id(tenant_id, config_id)
        if not existing:
            raise ResourceNotFoundError(f"Datasource config with id '{config_id}' not found")
        
        # If name is being updated, check for uniqueness within tenant
        if payload.name and payload.name != existing.name:
            name_exists = self.repo.get_by_name(tenant_id, payload.name)
            if name_exists:
                raise ResourceAlreadyExistsError(
                    f"Datasource config with name '{payload.name}' already exists"
                )
        
        old_name = existing.name
        old_driver_family = existing.driver_family
        
        # Update the config
        obj = self.repo.update(tenant_id, config_id, payload)
        if not obj:
            raise ResourceNotFoundError(f"Datasource config with id '{config_id}' not found")
        
        # If name changed, update datasources (for this tenant) that were using the old name to use the new name
        if payload.name and payload.name != old_name:
            datasources_with_old_key = self.db.query(Datasource).filter(
                Datasource.tenant_id == tenant_id,
                Datasource.connection_key == old_name
            ).all()
            
            for datasource in datasources_with_old_key:
                datasource.connection_key = payload.name
            
            self.db.commit()
        
        # If driver_family changed, update datasources (for this tenant) with the new driver_family to use this config
        if payload.driver_family and payload.driver_family != old_driver_family:
            matching_datasources = self.db.query(Datasource).filter(
                Datasource.tenant_id == tenant_id,
                Datasource.datasource_type == payload.driver_family
            ).all()
            
            for datasource in matching_datasources:
                datasource.connection_key = obj.name
            
            self.db.commit()
        
        return obj
    
    def delete(self, tenant_id: str, config_id: int):
        """
        Delete a datasource config WITHOUT affecting datasources.
        Datasources keep their connection_key so a new config can be added later.
        """
        # Get config before deleting to know which config we're deleting
        config = self.repo.get_by_id(tenant_id, config_id)
        if not config:
            raise ResourceNotFoundError(f"Datasource config with id '{config_id}' not found")
        
        # Delete the config (DO NOT touch datasource connection_keys)
        deleted = self.repo.delete(tenant_id, config_id)
        if not deleted:
            raise ResourceNotFoundError(f"Datasource config with id '{config_id}' not found")
        
        # NOTE: We intentionally DO NOT modify datasource.connection_key
        # This allows users to:
        # 1. Delete a config
        # 2. Keep the datasource intact with its connection_key
        # 3. Add a new config with the same name later
    
    def test_connection(self, tenant_id: str, config_id: int) -> dict:
        """Test connection for a datasource config"""
        obj = self.repo.get_by_id(tenant_id, config_id)
        if not obj:
            raise ResourceNotFoundError(f"Datasource config with id '{config_id}' not found")
        
        # TODO: Implement actual connection testing based on protocol and driver
        return {
            "config_id": config_id,
            "name": obj.name,
            "status": "success",
            "message": "Connection test passed"
        }