import logging
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api.routers import intelligence, raw_data, skus
from core.config import settings

# Setup standard structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.project_name,
    description="Microservice providing Risk scoring, AI explanations (Amazon Bedrock), and What-if Price Simulation for MarginGuard.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Secure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Request Timing Middleware for monitoring Performance
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log requests tracking (can be piped to CloudWatch/Datadog)
    logger.info(
        f"{request.method} {request.url.path} - Status: {response.status_code} - "
        f"Completed in {process_time:.4f}s"
    )
    return response

# Global Exception Handler prevents stack traces from leaking to the frontend
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "message": str(exc) if settings.debug else "Internal Server Error"}
    )

app.include_router(intelligence.router)
app.include_router(raw_data.router)
app.include_router(skus.router)

@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for ECS/EKS/ALB target group to ping."""
    return {"status": "ok", "service": "marginguard-intelligence"}
