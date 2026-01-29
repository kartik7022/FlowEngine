from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.core.config import settings
from backend.core.database import init_db

# Import all routers
from backend.modules.intents.routes import router as intents_router
from backend.modules.validation_rules.routes import router as validation_rules_router
from backend.modules.datasources.routes import router as datasources_router
from backend.modules.tenants.routes import router as tenants_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FlowEngine - Enterprise Email Management System",
    debug=settings.DEBUG
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routers
app.include_router(intents_router, tags=["Intents"])
app.include_router(validation_rules_router, tags=["Validation Rules"])
app.include_router(datasources_router, tags=["Datasources"])
app.include_router(tenants_router, tags=["Tenants"])

# Root endpoints
@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "dashboard": "/static/index.html"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )