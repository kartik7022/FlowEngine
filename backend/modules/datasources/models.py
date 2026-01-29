from sqlalchemy import (Column,Text,Boolean,DateTime,Integer,JSON,Index,UniqueConstraint)
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.core.database import Base


class Datasource(Base):
    __tablename__ = "datasources"
    __table_args__ = (
        Index("idx_eivs_datasources_tenant", "tenant_id"),
        UniqueConstraint("tenant_id", "name", name="uq_eivs_datasources_tenant_name"),
        UniqueConstraint("tenant_id", "datasource_id", name="uq_eivs_datasources_tenant_id"),  # ✅ ADDED
        {"schema": "eivs"},
    )

    datasource_id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(Text, nullable=False)
    datasource_type: str = Column(Text, nullable=False)
    connection_key: str = Column(Text, nullable=False)
    description: str = Column(Text)
    tenant_id: str = Column(Text, nullable=False, default="global")
    is_active: bool = Column(Boolean, nullable=False, default=True)
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    

    validation_rules = relationship(
        "ValidationRule",
        back_populates="datasource",
        cascade="all, delete-orphan",
    )


class DatasourceConfig(Base):
    __tablename__ = "datasource_configs"
    __table_args__ = (
        Index("idx_eivs_datasource_configs_tenant", "tenant_id"),
        UniqueConstraint("tenant_id", "name", name="uq_eivs_datasource_configs_tenant_name"),
        {"schema": "eivs"},
    )
    
    config_id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(Text, nullable=False)
    tenant_id: str = Column(Text, nullable=False, default="global")
    protocol: str = Column(Text, nullable=False)
    driver_family: str = Column(Text, nullable=False)
    base_url: str = Column(Text, nullable=True)
    auth_type: str = Column(Text, nullable=True)
    auth_config: dict = Column(JSON, nullable=True)
    connection_json: dict = Column(JSON, nullable=True)
    metadata_ref: str = Column(Text, nullable=True)
    is_active: bool = Column(Boolean, nullable=False, default=True)
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    router_base_url: str = Column(Text, nullable=True)