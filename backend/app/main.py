import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .database.connection import engine, Base, SessionLocal
from .models.models import ModelInfo
from .api.endpoints import router

# 1. Initialize Slowapi Limiter
limiter = Limiter(key_func=get_remote_address)

# 2. FastAPI instance
app = FastAPI(
    title="TrustLens AI Decision Backend",
    description="Backend API for TrustLens dark pattern analysis, feedback tracking, and model statistics.",
    version="1.0.0"
)

# Attach limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 3. Configure CORS
# Allow cross-origin requests from the Chrome Extension and the Admin Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Wildcard for easy local integration. In production, narrow this scope.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Include API routers
app.include_router(router)


@app.on_event("startup")
def startup_populate_db():
    """
    Bootstrap database tables and seed ModelInfo parameters on server start.
    """
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if ModelInfo table is populated
        if db.query(ModelInfo).count() == 0:
            print("Seeding ModelInfo metadata...")
            current_dir = os.path.dirname(os.path.abspath(__file__))
            disk_path = os.path.join(current_dir, "ml", "modelInfo.json")
            
            if os.path.exists(disk_path):
                with open(disk_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
                    
                    seed_model = ModelInfo(
                        version=info.get("version", "1.0.0"),
                        accuracy=info.get("accuracy", 1.0),
                        precision=info.get("precision", 1.0),
                        recall=info.get("recall", 1.0),
                        f1_score=info.get("f1", 1.0),
                        trained_date=info.get("trainingDate", "2026-07-14")
                    )
                    db.add(seed_model)
                    db.commit()
                    print(f"Successfully seeded database with model version {seed_model.version}.")
            else:
                print(f"Warning: modelInfo.json backup file not found at {disk_path}. Seeding default.")
                seed_model = ModelInfo(
                    version="1.0.0",
                    accuracy=1.0,
                    precision=1.0,
                    recall=1.0,
                    f1_score=1.0,
                    trained_date="2026-07-14"
                )
                db.add(seed_model)
                db.commit()
    except Exception as e:
        print(f"Error during startup seeding: {e}")
    finally:
        db.close()


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "status": "online",
        "app": "TrustLens Backend Services",
        "mode": "production" if os.getenv("DATABASE_URL") else "development/sqlite-fallback"
    }
