from sqlalchemy.orm import Session
from typing import List, Optional

from backend.modules.validation_rules.models import ValidationRule
from backend.modules.validation_rules.schemas import ValidationRuleCreate, ValidationRuleUpdate


class ValidationRuleRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(
        self,
        tenant_id: str,
        intent_id: Optional[int] = None, 
        language_code: Optional[str] = None,
        active_only: bool = False
    ) -> List[ValidationRule]:
        """Get all validation rules with optional filters, ordered by intent, language, and execution order"""
        query = self.db.query(ValidationRule).filter(ValidationRule.tenant_id == tenant_id)
        
        if intent_id:
            query = query.filter(ValidationRule.intent_id == intent_id)
        
        if language_code:
            query = query.filter(ValidationRule.language_code == language_code)
        
        if active_only:
            query = query.filter(ValidationRule.is_active == True)
        
        # This ordering matches the composite index for optimal performance
        return query.order_by(
            ValidationRule.intent_id,
            ValidationRule.language_code,
            ValidationRule.execution_order
        ).all()
    
    def get_by_id(self, tenant_id: str, rule_id: int) -> Optional[ValidationRule]:
        """Get a single validation rule by ID"""
        return self.db.query(ValidationRule).filter(
            ValidationRule.tenant_id == tenant_id,
            ValidationRule.rule_id == rule_id
        ).first()
    
    def get_by_rule_code(self, tenant_id: str, rule_code: str) -> Optional[ValidationRule]:
        """Get a validation rule by its unique rule code within tenant"""
        return self.db.query(ValidationRule).filter(
            ValidationRule.tenant_id == tenant_id,
            ValidationRule.rule_code == rule_code
        ).first()
    
    def get_by_intent_and_language(self, tenant_id: str, intent_id: int, language_code: str) -> List[ValidationRule]:
        """Get all validation rules for a specific intent and language, ordered by execution_order"""
        return self.db.query(ValidationRule)\
            .filter(
                ValidationRule.tenant_id == tenant_id,
                ValidationRule.intent_id == intent_id,
                ValidationRule.language_code == language_code,
                ValidationRule.is_active == True
            )\
            .order_by(ValidationRule.execution_order)\
            .all()
    
    def get_max_execution_order(self, tenant_id: str, intent_id: int, language_code: str) -> int:
        """Get the maximum execution order for a given intent and language"""
        result = self.db.query(ValidationRule.execution_order)\
            .filter(
                ValidationRule.tenant_id == tenant_id,
                ValidationRule.intent_id == intent_id,
                ValidationRule.language_code == language_code
            )\
            .order_by(ValidationRule.execution_order.desc())\
            .first()
        
        return result[0] if result else 0
    
    def create(self, tenant_id: str, payload: ValidationRuleCreate) -> ValidationRule:
        """Create a new validation rule"""
        data = payload.model_dump()
        data['tenant_id'] = tenant_id  # Override with provided tenant_id
        obj = ValidationRule(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, tenant_id: str, rule_id: int, payload: ValidationRuleUpdate) -> Optional[ValidationRule]:
        """Update an existing validation rule"""
        obj = self.get_by_id(tenant_id, rule_id)
        if not obj:
            return None
        
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, tenant_id: str, rule_id: int) -> bool:
        """Delete a validation rule by ID"""
        obj = self.get_by_id(tenant_id, rule_id)
        if not obj:
            return False
        
        self.db.delete(obj)
        self.db.commit()
        return True