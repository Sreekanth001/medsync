from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS - allow all origins (update in production if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1 import dashboard, hospitals, hospital_resources, doctors, nurses, patients, emergency, workflow_api

@app.get("/")
def root():
    return {"message": "Welcome to MedSync AI API (LangGraph Edition)"}

@app.on_event("startup")
async def startup_event():
    """Seed database with initial data if empty."""
    from app.db.database import SessionLocal
    from app.models.domain import Doctor
    db = SessionLocal()
    try:
        if db.query(Doctor).count() == 0:
            from app.db.seed import seed_db
            seed_db()
    finally:
        db.close()

app.include_router(workflow_api.router, prefix=f"{settings.API_V1_STR}/workflow", tags=["Workflow"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
app.include_router(hospitals.router, prefix=f"{settings.API_V1_STR}/hospitals", tags=["Hospitals"])
app.include_router(hospital_resources.router, prefix=f"{settings.API_V1_STR}/hospital-admin", tags=["Hospital Resources"])
app.include_router(doctors.router, prefix=f"{settings.API_V1_STR}/doctors", tags=["Doctors"])
app.include_router(nurses.router, prefix=f"{settings.API_V1_STR}/nurses", tags=["Nurses"])
app.include_router(patients.router, prefix=f"{settings.API_V1_STR}/patients", tags=["Patients"])
app.include_router(emergency.router, prefix=f"{settings.API_V1_STR}/emergency", tags=["Emergency"])
