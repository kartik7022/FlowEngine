from typing import Optional, List
from sqlalchemy.orm import Session

from backend.modules.validation_rules.repository import ValidationRuleRepository
from backend.modules.validation_rules.schemas import ValidationRuleCreate, ValidationRuleUpdate
from backend.modules.validation_rules.models import ValidationRule
from backend.common.exceptions import ResourceNotFoundError, ResourceAlreadyExistsError
from backend.modules.datasources.models import Datasource
from backend.modules.intents.models import Intent


class ValidationRuleService:
    """Service layer for validation rules business logic"""
    
    def __init__(self, repo: ValidationRuleRepository, db: Session = None):
        self.repo = repo
        self.db = db or repo.db
    
    def get_all(
        self,
        tenant_id: str,
        intent_id: Optional[int] = None,
        language_code: Optional[str] = None,
        active_only: bool = False
    ) -> List[ValidationRule]:
        """Get all validation rules with optional filters"""
        return self.repo.get_all(tenant_id, intent_id, language_code, active_only)
    
    def get(self, tenant_id: str, rule_id: int) -> ValidationRule:
        """Get a single validation rule by ID"""
        obj = self.repo.get_by_id(tenant_id, rule_id)
        if not obj:
            raise ResourceNotFoundError(f"Validation rule with id '{rule_id}' not found")
        return obj
    
    def get_by_intent_and_language(self, tenant_id: str, intent_id: int, language_code: str) -> List[ValidationRule]:
        """Get all active validation rules for a specific intent and language"""
        return self.repo.get_by_intent_and_language(tenant_id, intent_id, language_code)
    
    def create(self, tenant_id: str, payload: ValidationRuleCreate) -> ValidationRule:
        """Create a new validation rule with validations"""
        # Validate that the intent exists for this tenant
        intent = self.db.query(Intent).filter(
            Intent.tenant_id == tenant_id,
            Intent.intent_id == payload.intent_id
        ).first()
        if not intent:
            raise ResourceNotFoundError(f"Intent with id '{payload.intent_id}' not found")
        
        # Validate that the datasource exists and is active for this tenant
        datasource = self.db.query(Datasource).filter(
            Datasource.tenant_id == tenant_id,
            Datasource.datasource_id == payload.datasource_id
        ).first()
        
        if not datasource:
            raise ResourceNotFoundError(f"Datasource with id '{payload.datasource_id}' not found")
        
        if not datasource.is_active:
            raise ValueError(f"Datasource '{datasource.name}' is not active. Cannot create validation rule with inactive datasource.")
        
        # FIXED: Check if rule_code already exists ONLY WITHIN THE SAME INTENT AND TENANT
        # Same rule_code is allowed in different intents or different tenants
        existing = self.db.query(ValidationRule).filter(
            ValidationRule.tenant_id == tenant_id,
            ValidationRule.rule_code == payload.rule_code,
            ValidationRule.intent_id == payload.intent_id
        ).first()
        
        if existing:
            raise ResourceAlreadyExistsError(
                f"Validation rule with code '{payload.rule_code}' already exists in this intent"
            )
        
        # Validate execution_order is positive
        if payload.execution_order < 1:
            raise ValueError("execution_order must be >= 1")
        
        # Validate severity
        if payload.severity not in ['CRITICAL', 'WARNING']:
            raise ValueError("severity must be either 'CRITICAL' or 'WARNING'")
        
        return self.repo.create(tenant_id, payload)
    
    def update(self, tenant_id: str, rule_id: int, payload: ValidationRuleUpdate) -> ValidationRule:
        """Update an existing validation rule with validations"""
        # Check if the rule exists first for this tenant
        existing_rule = self.repo.get_by_id(tenant_id, rule_id)
        if not existing_rule:
            raise ResourceNotFoundError(f"Validation rule with id '{rule_id}' not found")
        
        # If datasource_id is being updated, validate it for this tenant
        if payload.datasource_id is not None:
            datasource = self.db.query(Datasource).filter(
                Datasource.tenant_id == tenant_id,
                Datasource.datasource_id == payload.datasource_id
            ).first()
            
            if not datasource:
                raise ResourceNotFoundError(f"Datasource with id '{payload.datasource_id}' not found")
            
            if not datasource.is_active:
                raise ValueError(f"Datasource '{datasource.name}' is not active. Cannot update to inactive datasource.")
        
        # If intent_id is being updated, validate it for this tenant
        if payload.intent_id is not None:
            intent = self.db.query(Intent).filter(
                Intent.tenant_id == tenant_id,
                Intent.intent_id == payload.intent_id
            ).first()
            if not intent:
                raise ResourceNotFoundError(f"Intent with id '{payload.intent_id}' not found")
        
        # If execution_order is being updated, validate it
        if payload.execution_order is not None and payload.execution_order < 1:
            raise ValueError("execution_order must be >= 1")
        
        # If severity is being updated, validate it
        if payload.severity is not None and payload.severity not in ['CRITICAL', 'WARNING']:
            raise ValueError("severity must be either 'CRITICAL' or 'WARNING'")
        
        obj = self.repo.update(tenant_id, rule_id, payload)
        if not obj:
            raise ResourceNotFoundError(f"Validation rule with id '{rule_id}' not found")
        return obj
    
    def delete(self, tenant_id: str, rule_id: int) -> None:
        """Delete a validation rule"""
        deleted = self.repo.delete(tenant_id, rule_id)
        if not deleted:
            raise ResourceNotFoundError(f"Validation rule with id '{rule_id}' not found")
    
    def get_next_execution_order(self, tenant_id: str, intent_id: int, language_code: str = 'multi') -> int:
        """Get the next available execution order for a given intent and language"""
        max_order = self.repo.get_max_execution_order(tenant_id, intent_id, language_code)
        return max_order + 1