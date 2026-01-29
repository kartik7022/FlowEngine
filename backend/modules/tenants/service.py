from backend.modules.tenants.repository import TenantRepository
from backend.modules.tenants.schemas import TenantCreate, TenantUpdate
from backend.common.exceptions import ResourceNotFoundError, ResourceAlreadyExistsError


class TenantService:
    
    def __init__(self, repo: TenantRepository):
        self.repo = repo
    
    def get_all(self, active_only: bool = False):
        return self.repo.get_all(active_only)
    
    def get(self, tenant_id: str):
        obj = self.repo.get_by_id(tenant_id)
        if not obj:
            raise ResourceNotFoundError(f"Tenant '{tenant_id}' not found")
        return obj
    
    def validate(self, tenant_id: str) -> bool:
        return self.repo.exists(tenant_id)
    
    def create(self, payload: TenantCreate):
        existing = self.repo.get_by_id(payload.tenant_id)
        if existing:
            raise ResourceAlreadyExistsError(f"Tenant '{payload.tenant_id}' already exists")
        
        return self.repo.create(payload)
    
    def update(self, tenant_id: str, payload: TenantUpdate):
        obj = self.repo.update(tenant_id, payload)
        if not obj:
            raise ResourceNotFoundError(f"Tenant '{tenant_id}' not found")
        return obj
    
    def delete(self, tenant_id: str):
        deleted = self.repo.delete(tenant_id)
        if not deleted:
            raise ResourceNotFoundError(f"Tenant '{tenant_id}' not found")