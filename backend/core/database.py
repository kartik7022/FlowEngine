from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create schema if not exists on engine connection
@event.listens_for(engine, "connect")
def create_schema(dbapi_conn, connection_record):
    """Create eivs schema if it doesn't exist"""
    cursor = dbapi_conn.cursor()
    cursor.execute("CREATE SCHEMA IF NOT EXISTS eivs")
    cursor.close()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

def init_db():
    """Initialize database - create all tables"""
    # Import all models so SQLAlchemy registers them
    from backend.modules.intents.models import Intent
    from backend.modules.validation_rules.models import ValidationRule
    from backend.modules.datasources.models import Datasource
    from backend.modules.tenants.models import Tenant
    Base.metadata.create_all(bind=engine)