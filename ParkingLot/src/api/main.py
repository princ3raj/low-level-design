"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import parking_lots, parking, payments
from src.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Parking Lot Management System",
    description="API for managing parking lots, vehicle entry/exit, and payments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(parking_lots.router, prefix="/api/v1", tags=["Parking Lots"])
app.include_router(parking.router, prefix="/api/v1", tags=["Parking"])
app.include_router(payments.router, prefix="/api/v1", tags=["Payments"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Parking Lot Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
