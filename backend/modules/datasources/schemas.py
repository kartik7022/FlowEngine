from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime


# ============ DATASOURCE SCHEMAS ============

class DatasourceBase(BaseModel):
	name: str = Field(..., min_length=1, description="Logical name (e.g., CRM_DB, LOAN_CORE_DB)")
	datasource_type: str = Field(..., min_length=1, description="Type: postgres, snowflake, api, rest, graphql, etc.")
	connection_key: str = Field(..., min_length=1, description="Key for Adapter/middleware routing - will be updated with config name")
	description: Optional[str] = Field(None, description="Description of the datasource")
	tenant_id: str = Field(default='global', description="Tenant ID for multi-tenancy")
	is_active: bool = True


class DatasourceCreate(DatasourceBase):
	pass


class DatasourceUpdate(BaseModel):
	name: Optional[str] = Field(None, min_length=1)
	datasource_type: Optional[str] = Field(None, min_length=1)
	connection_key: Optional[str] = Field(None, min_length=1)
	description: Optional[str] = None
	tenant_id: Optional[str] = None
	is_active: Optional[bool] = None


class DatasourceOut(DatasourceBase):
	datasource_id: int
	
	class Config:
		from_attributes = True


# ============ DATASOURCE CONFIG SCHEMAS ============

class DatasourceConfigBase(BaseModel):
	name: str = Field(..., min_length=1, max_length=255, description="Unique config name, e.g., SERVICENOW_ITSM_PROD")
	protocol: str = Field(..., description="Protocol: 'sql', 'rest', 'graphql', 'file', 'stream'")
	driver_family: str = Field(..., description="Driver family: 'postgres', 'cdata', 'datadirect', 'servicenow', etc.")
	base_url: Optional[str] = Field(None, description="Base URL for REST/GraphQL")
	auth_type: Optional[str] = Field(None, description="Auth type: 'oauth2', 'apikey', 'basic', 'none'")
	auth_config: Optional[Dict[str, Any]] = Field(None, description="Auth configuration")
	connection_json: Optional[Dict[str, Any]] = Field(None, description="Connection details (DSN, JDBC URL, ODBC, etc.)")
	metadata_ref: Optional[str] = Field(None, description="Metadata reference URL (OpenAPI, GraphQL SDL, etc.)")
	is_active: bool = Field(default=True)
	router_base_url: Optional[str] = Field(None, description="Router base URL for API routing")
	tenant_id: str = Field(default='global', description="Tenant ID for multi-tenancy")

	@field_validator('protocol')
	@classmethod
	def validate_protocol(cls, v):
		allowed = ['sql', 'rest', 'graphql', 'file', 'stream']
		if v not in allowed:
			raise ValueError(f'protocol must be one of {allowed}')
		return v

	@field_validator('auth_type')
	@classmethod
	def validate_auth_type(cls, v):
		if v is None:
			return v
		allowed = ['oauth2', 'apikey', 'basic', 'none']
		if v not in allowed:
			raise ValueError(f'auth_type must be one of {allowed}')
		return v


class DatasourceConfigCreate(DatasourceConfigBase):
	pass


class DatasourceConfigUpdate(BaseModel):
	name: Optional[str] = Field(None, min_length=1, max_length=255)
	protocol: Optional[str] = None
	driver_family: Optional[str] = None
	base_url: Optional[str] = None
	auth_type: Optional[str] = None
	auth_config: Optional[Dict[str, Any]] = None
	connection_json: Optional[Dict[str, Any]] = None
	metadata_ref: Optional[str] = None
	is_active: Optional[bool] = None
	router_base_url: Optional[str] = None
	tenant_id: Optional[str] = None

	@field_validator('protocol')
	@classmethod
	def validate_protocol(cls, v):
		if v is None:
			return v
		allowed = ['sql', 'rest', 'graphql', 'file', 'stream']
		if v not in allowed:
			raise ValueError(f'protocol must be one of {allowed}')
		return v

	@field_validator('auth_type')
	@classmethod
	def validate_auth_type(cls, v):
		if v is None:
			return v
		allowed = ['oauth2', 'apikey', 'basic', 'none']
		if v not in allowed:
			raise ValueError(f'auth_type must be one of {allowed}')
		return v


class DatasourceConfigOut(DatasourceConfigBase):
	config_id: int
	created_at: datetime
	updated_at: datetime
	
	class Config:
		from_attributes = True