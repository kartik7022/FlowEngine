from sqlalchemy import (Column,String,Text,Boolean,Integer,ForeignKey,Numeric,Index,ForeignKeyConstraint,UniqueConstraint,DateTime)
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.core.database import Base

class Intent(Base):
    __tablename__ = "intents"
    __table_args__ = (
        Index("idx_eivs_intents_tenant", "tenant_id"),
        UniqueConstraint("tenant_id", "intent_code", name="uq_eivs_intents_tenant_code"),
        UniqueConstraint("tenant_id", "intent_id", name="uq_eivs_intents_tenant_id"),  # ✅ ADDED
        {"schema": "eivs"},
    )
    
    intent_id: int = Column(Integer, primary_key=True, autoincrement=True)
    intent_code: str = Column(Text, nullable=False)
    tenant_id: str = Column(Text, nullable=False, default="global")
    display_name = Column(Text, nullable=False)
    description = Column(Text)
    category = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    # Relationships
    policies = relationship("IntentPolicy", back_populates="intent", cascade="all, delete-orphan")
    validation_rules = relationship("ValidationRule", back_populates="intent", cascade="all, delete-orphan")

class IntentPolicy(Base):
    __tablename__ = "intent_policies"
    __table_args__ = (
        ForeignKeyConstraint(
            ['tenant_id', 'intent_id'],
            ['eivs.intents.tenant_id', 'eivs.intents.intent_id'],
            ondelete='CASCADE'
        ),
        Index('idx_eivs_intent_policies_tenant', 'tenant_id'),
        {'schema': 'eivs'}
    )
    
    # PRIMARY KEY: tenant_id, intent_id, language_code (all three!)
    tenant_id = Column(Text, primary_key=True, nullable=False, default='global')
    intent_id = Column(Integer, primary_key=True, nullable=False)
    language_code = Column(String(10), primary_key=True, nullable=False, default='multi')
    
    # Other columns
    n8n_orchestration_url = Column(Text, nullable=True)
    auto_process_min_conf = Column(Numeric(5, 2), nullable=False)
    manual_review_min_conf = Column(Numeric(5, 2), nullable=False)
    reroute_email = Column(Text, nullable=True)
    multi_intent_mode = Column(Text, nullable=False, default='STRICT_SINGLE')
    allow_multi_auto = Column(Boolean, nullable=False, default=False)
    allow_subset_auto = Column(Boolean, nullable=False, default=False)
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    intent = relationship("Intent", back_populates="policies")