from sqlalchemy import Column, Text, DateTime, Boolean
from datetime import datetime
from backend.core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {'schema': 'eivs'}
    
    tenant_id = Column(Text, primary_key=True)
    tenant_name = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)  # ← CHANGE TO nullable=True