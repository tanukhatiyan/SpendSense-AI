from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import engine, Base
import app.models  # Ensure all SQLAlchemy models are registered
from app.api.v1 import auth, expenses, budgets, reports, ai

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables automatically upon startup
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SpendSense AI — Smart Personal Finance & Expense Management Backend",
    lifespan=lifespan
)

# Configure CORS for Vite and development clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Root health and welcome endpoint."""
    return {
        "app_name": settings.PROJECT_NAME,
        "app name": settings.PROJECT_NAME,  # Backward compatibility for existing frontend
        "message": "Your smart expense manager is running!",
        "version": settings.VERSION,
        "status": "healthy"
    }

@app.get("/health")
def health_check():
    """Dedicated health check endpoint for containerization and load balancers."""
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": settings.VERSION}

# Legacy root routes for backward compatibility
app.include_router(expenses.router, prefix="/expenses")

# API v1 Versioned Routes
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(expenses.router, prefix=f"{settings.API_V1_STR}/expenses")
app.include_router(budgets.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(ai.router, prefix=settings.API_V1_STR)
