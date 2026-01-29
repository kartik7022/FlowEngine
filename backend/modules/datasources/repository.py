from sqlalchemy.orm import Session
from typing import List, Optional

from backend.modules.datasources.models import Datasource, DatasourceConfig
from backend.modules.datasources.schemas import (
    DatasourceCreate, DatasourceUpdate,
    DatasourceConfigCreate, DatasourceConfigUpdate
)


class DatasourceRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, tenant_id: str, active_only: bool = False) -> List[Datasource]:
        query = self.db.query(Datasource).filter(Datasource.tenant_id == tenant_id)
        if active_only:
            query = query.filter(Datasource.is_active == True)
        return query.order_by(Datasource.datasource_id.desc()).all()
    
    def get_by_id(self, tenant_id: str, datasource_id: int) -> Optional[Datasource]:
        return self.db.query(Datasource).filter(
            Datasource.tenant_id == tenant_id,
            Datasource.datasource_id == datasource_id
        ).first()
    
    def get_by_name(self, tenant_id: str, name: str) -> Optional[Datasource]:
        return self.db.query(Datasource).filter(
            Datasource.tenant_id == tenant_id,
            Datasource.name == name
        ).first()
    
    def create(self, tenant_id: str, payload: DatasourceCreate) -> Datasource:
        data = payload.model_dump()
        data['tenant_id'] = tenant_id
        obj = Datasource(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, tenant_id: str, datasource_id: int, payload: DatasourceUpdate) -> Optional[Datasource]:
        obj = self.get_by_id(tenant_id, datasource_id)
        if not obj:
            return None
        
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, tenant_id: str, datasource_id: int) -> bool:
        obj = self.get_by_id(tenant_id, datasource_id)
        if not obj:
            return False
        
        self.db.delete(obj)
        self.db.commit()
        return True


class DatasourceConfigRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, tenant_id: str, active_only: bool = False) -> List[DatasourceConfig]:
        query = self.db.query(DatasourceConfig).filter(DatasourceConfig.tenant_id == tenant_id)
        if active_only:
            query = query.filter(DatasourceConfig.is_active == True)
        return query.order_by(DatasourceConfig.config_id.desc()).all()
    
    def get_by_id(self, tenant_id: str, config_id: int) -> Optional[DatasourceConfig]:
        return self.db.query(DatasourceConfig).filter(
            DatasourceConfig.tenant_id == tenant_id,
            DatasourceConfig.config_id == config_id
        ).first()
    
    def get_by_name(self, tenant_id: str, name: str) -> Optional[DatasourceConfig]:
        return self.db.query(DatasourceConfig).filter(
            DatasourceConfig.tenant_id == tenant_id,
            DatasourceConfig.name == name
        ).first()
    
    def get_by_driver_family(self, tenant_id: str, driver_family: str) -> List[DatasourceConfig]:
        return self.db.query(DatasourceConfig).filter(
            DatasourceConfig.tenant_id == tenant_id,
            DatasourceConfig.driver_family == driver_family
        ).order_by(DatasourceConfig.name).all()
    
    def get_by_protocol(self, tenant_id: str, protocol: str) -> List[DatasourceConfig]:
        return self.db.query(DatasourceConfig).filter(
            DatasourceConfig.tenant_id == tenant_id,
            DatasourceConfig.protocol == protocol
        ).order_by(DatasourceConfig.name).all()
    
    def create(self, tenant_id: str, payload: DatasourceConfigCreate) -> DatasourceConfig:
        data = payload.model_dump()
        data['tenant_id'] = tenant_id
        obj = DatasourceConfig(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, tenant_id: str, config_id: int, payload: DatasourceConfigUpdate) -> Optional[DatasourceConfig]:
        obj = self.get_by_id(tenant_id, config_id)
        if not obj:
            return None
        
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, tenant_id: str, config_id: int) -> bool:
        obj = self.get_by_id(tenant_id, config_id)
        if not obj:
            return False
        
        self.db.delete(obj)
        self.db.commit()
        return True