from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from time import time
import os
from app.database import engine
from app.models import Base
from app.routers import tasks
from app.monitoring import log_api_call, setup_cloudwatch_logging

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Management API",
    description="A simple REST API for managing tasks",
    version="1.0.0",
)

# Setup CloudWatch logging
if os.getenv("ENVIRONMENT") == "production":
    setup_cloudwatch_logging()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all API requests"""
    start_time = time()
    response = await call_next(request)
    latency = (time() - start_time) * 1000

    log_api_call(
        endpoint=request.url.path,
        method=request.method,
        status_code=response.status_code,
        latency=latency,
    )

    return response


@app.get("/")
def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Task Management API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for ECS"""
    return {"status": "healthy", "service": "task-management-api"}


# Include routers
app.include_router(tasks.router)
