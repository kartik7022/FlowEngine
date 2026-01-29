from sqlalchemy.orm import Session
from typing import List, Optional
from backend.modules.tenants.models import Tenant
from backend.modules.tenants.schemas import TenantCreate, TenantUpdate


class TenantRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, active_only: bool = False) -> List[Tenant]:
        query = self.db.query(Tenant)
        if active_only:
            query = query.filter(Tenant.is_active == True)
        return query.order_by(Tenant.created_at.desc()).all()
    
    def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        return self.db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    
    def exists(self, tenant_id: str) -> bool:
        return self.db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first() is not None
    
    def create(self, payload: TenantCreate) -> Tenant:
        obj = Tenant(**payload.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, tenant_id: str, payload: TenantUpdate) -> Optional[Tenant]:
        obj = self.get_by_id(tenant_id)
        if not obj:
            return None
        
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, tenant_id: str) -> bool:
        obj = self.get_by_id(tenant_id)
        if not obj:
            return False
        
        self.db.delete(obj)
        self.db.commit()
        return True