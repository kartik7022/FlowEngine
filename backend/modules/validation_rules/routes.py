from fastapi import APIRouter, Depends, status, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.dependencies import get_db
from backend.modules.validation_rules.schemas import ValidationRuleCreate, ValidationRuleUpdate, ValidationRuleOut
from backend.modules.validation_rules.repository import ValidationRuleRepository
from backend.modules.validation_rules.service import ValidationRuleService
from backend.common.responses import SuccessResponse

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> ValidationRuleService:
    """Dependency injection for ValidationRuleService"""
    return ValidationRuleService(ValidationRuleRepository(db), db)


@router.get("/validation-rules", response_model=List[ValidationRuleOut])
def get_all_validation_rules(
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    intent_id: Optional[int] = Query(None, description="Filter by intent ID"),
    language_code: Optional[str] = Query(None, description="Filter by language code"),
    active_only: bool = Query(False, description="Return only active rules"),
    service: ValidationRuleService = Depends(get_service)
):
    """
    Get all validation rules with optional filters.
    Rules are returned ordered by intent_id, language_code, and execution_order.
    """
    return service.get_all(tenant_id, intent_id, language_code, active_only)


@router.get("/validation-rules/{rule_id}", response_model=ValidationRuleOut)
def get_validation_rule(
    rule_id: int,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: ValidationRuleService = Depends(get_service)
):
    """Get a single validation rule by ID"""
    return service.get(tenant_id, rule_id)


@router.get("/validation-rules/intent/{intent_id}/language/{language_code}", response_model=List[ValidationRuleOut])
def get_rules_by_intent_and_language(
    intent_id: int,
    language_code: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: ValidationRuleService = Depends(get_service)
):
    """
    Get all active validation rules for a specific intent and language.
    Rules are returned in execution order.
    """
    return service.get_by_intent_and_language(tenant_id, intent_id, language_code)


@router.get("/validation-rules/next-order/{intent_id}")
def get_next_execution_order(
    intent_id: int,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    language_code: str = Query(default='multi', description="Language code, defaults to 'multi'"),
    service: ValidationRuleService = Depends(get_service)
):
    """
    Get the next available execution order for a given intent and language.
    Useful when creating new validation rules.
    """
    next_order = service.get_next_execution_order(tenant_id, intent_id, language_code)
    return {
        "intent_id": intent_id,
        "language_code": language_code,
        "next_execution_order": next_order
    }


@router.post("/validation-rules", response_model=ValidationRuleOut, status_code=status.HTTP_201_CREATED)
def create_validation_rule(
    payload: ValidationRuleCreate,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: ValidationRuleService = Depends(get_service)
):
    """
    Create a new validation rule.
    
    Validates:
    - Intent exists
    - Datasource exists and is active
    - Rule code is unique
    - Execution order is >= 1
    - Severity is CRITICAL or WARNING
    """
    return service.create(tenant_id, payload)


@router.put("/validation-rules/{rule_id}", response_model=ValidationRuleOut)
def update_validation_rule(
    rule_id: int,
    payload: ValidationRuleUpdate,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: ValidationRuleService = Depends(get_service)
):
    """
    Update an existing validation rule.
    
    Validates:
    - Rule exists
    - If datasource_id provided: datasource exists and is active
    - If intent_id provided: intent exists
    - If execution_order provided: >= 1
    - If severity provided: CRITICAL or WARNING
    """
    return service.update(tenant_id, rule_id, payload)


@router.delete("/validation-rules/{rule_id}", response_model=SuccessResponse)
def delete_validation_rule(
    rule_id: int,
    tenant_id: str = Header(..., alias="X-Tenant-ID"),
    service: ValidationRuleService = Depends(get_service)
):
    """
    Delete a validation rule by ID.
    Due to CASCADE, this will also clean up any related data.
    """
    service.delete(tenant_id, rule_id)
    return SuccessResponse(message=f"Validation rule {rule_id} deleted successfully")