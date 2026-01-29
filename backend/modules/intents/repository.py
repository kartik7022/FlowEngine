# backend/modules/intents/repository.py

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from backend.modules.intents.models import Intent, IntentPolicy
from backend.modules.intents.schemas import IntentCreate, IntentUpdate, IntentPolicyCreate, IntentPolicyUpdate


class IntentRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, tenant_id: str, active_only: bool = False) -> List[Intent]:
        query = self.db.query(Intent).filter(Intent.tenant_id == tenant_id)
        if active_only:
            query = query.filter(Intent.is_active == True)
        return query.order_by(Intent.intent_id.desc()).all()
    
    def get_by_id(self, tenant_id: str, intent_id: int) -> Optional[Intent]:
        return self.db.query(Intent).filter(
            Intent.tenant_id == tenant_id,
            Intent.intent_id == intent_id
        ).first()
    
    def get_by_code(self, tenant_id: str, intent_code: str) -> Optional[Intent]:
        return self.db.query(Intent).filter(
            Intent.tenant_id == tenant_id,
            Intent.intent_code == intent_code
        ).first()
    
    def create(self, tenant_id: str, payload: IntentCreate) -> Intent:
        # Create intent with tenant_id
        intent_data = payload.model_dump(exclude={'policies'})
        intent_data['tenant_id'] = tenant_id  # Override with provided tenant_id
        obj = Intent(**intent_data)
        self.db.add(obj)
        self.db.flush()
        
        # Create policies with tenant_id
        for policy_data in payload.policies:
            policy_dict = policy_data.model_dump()
            policy_dict['tenant_id'] = tenant_id  # Override with provided tenant_id
            policy = IntentPolicy(intent_id=obj.intent_id, **policy_dict)
            self.db.add(policy)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, tenant_id: str, intent_id: int, payload: IntentUpdate) -> Optional[Intent]:
        obj = self.get_by_id(tenant_id, intent_id)
        if not obj:
            return None
        
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, tenant_id: str, intent_id: int) -> bool:
        obj = self.get_by_id(tenant_id, intent_id)
        if not obj:
            return False
        
        self.db.delete(obj)
        self.db.commit()
        return True


class IntentPolicyRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_with_intent(self, tenant_id: str):
        """Get all policies with their intent information for a specific tenant"""
        return self.db.query(IntentPolicy).join(Intent).filter(
            IntentPolicy.tenant_id == tenant_id
        ).order_by(
            Intent.intent_code, IntentPolicy.language_code
        ).all()
    
    def get_all(self, tenant_id: str) -> List[IntentPolicy]:
        """Get all policies across all intents for a specific tenant"""
        return self.db.query(IntentPolicy).filter(
            IntentPolicy.tenant_id == tenant_id
        ).order_by(
            IntentPolicy.intent_id, IntentPolicy.language_code
        ).all()
    
    def get_by_intent(self, tenant_id: str, intent_id: int) -> List[IntentPolicy]:
        return self.db.query(IntentPolicy).filter(
            IntentPolicy.tenant_id == tenant_id,
            IntentPolicy.intent_id == intent_id
        ).order_by(IntentPolicy.language_code).all()
    
    def get_by_intent_and_language(self, tenant_id: str, intent_id: int, language_code: str) -> Optional[IntentPolicy]:
        return self.db.query(IntentPolicy).filter(
            IntentPolicy.tenant_id == tenant_id,
            IntentPolicy.intent_id == intent_id,
            IntentPolicy.language_code == language_code
        ).first()
    
    def create(self, tenant_id: str, intent_id: int, payload: IntentPolicyCreate) -> IntentPolicy:
        policy_data = payload.model_dump()
        policy_data['tenant_id'] = tenant_id  # Override with provided tenant_id
        obj = IntentPolicy(intent_id=intent_id, **policy_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, tenant_id: str, intent_id: int, language_code: str, payload: IntentPolicyUpdate) -> Optional[IntentPolicy]:
        obj = self.get_by_intent_and_language(tenant_id, intent_id, language_code)
        if not obj:
            return None
        
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, tenant_id: str, intent_id: int, language_code: str) -> bool:
        obj = self.get_by_intent_and_language(tenant_id, intent_id, language_code)
        if not obj:
            return False
        
        self.db.delete(obj)
        self.db.commit()
        return True