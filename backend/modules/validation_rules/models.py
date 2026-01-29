from sqlalchemy import (Column, String, Text, Boolean, Integer, ForeignKey, Index, 
                        ForeignKeyConstraint, UniqueConstraint, DateTime)
from sqlalchemy.orm import relationship
from backend.core.database import Base
from datetime import datetime


class ValidationRule(Base):
    __tablename__ = "validation_rules"
    __table_args__ = (
        # ✅ Composite foreign key to Intent
        ForeignKeyConstraint(
            ['tenant_id', 'intent_id'],
            ['eivs.intents.tenant_id', 'eivs.intents.intent_id'],
            ondelete='CASCADE'
        ),
        # ✅ Composite foreign key to Datasource
        ForeignKeyConstraint(
            ['tenant_id', 'datasource_id'],
            ['eivs.datasources.tenant_id', 'eivs.datasources.datasource_id'],
            ondelete='CASCADE'
        ),
        # ✅ Unique constraint: same rule_code allowed in different intents, but not within same intent
        UniqueConstraint('tenant_id', 'intent_id', 'rule_code', name='uq_validation_rules_tenant_intent_code'),
        Index('idx_validation_rules_intent_lang', 'intent_id', 'language_code', 'execution_order'),
        Index('idx_eivs_validation_rules_tenant', 'tenant_id'),
        {'schema': 'eivs'}
    )
    
    rule_id = Column(Integer, primary_key=True, autoincrement=True)
    intent_id = Column(Integer, nullable=False)
    language_code = Column(String(10), default='multi', nullable=False)
    tenant_id = Column(Text, nullable=False, default='global')
    rule_code = Column(Text, nullable=False)
    rule_name = Column(Text, nullable=False)
    rule_description = Column(Text, nullable=False)
    datasource_id = Column(Integer, nullable=False)
    execution_order = Column(Integer, nullable=False)
    severity = Column(Text, nullable=False, default='CRITICAL')
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    intent = relationship("Intent", back_populates="validation_rules")
    datasource = relationship("Datasource", back_populates="validation_rules")