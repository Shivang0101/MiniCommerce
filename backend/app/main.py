from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_v1_router
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.logging import LoggingMiddleware
from app.core.errors import api_exception_handler
from app.db.session import engine
from app.db.base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema exists on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="MiniCommerce V2 Laboratory",
    description="Database Engineering, Concurrency & Performance Laboratory",
    version="2.0.0",
    lifespan=lifespan
)

# Exception handlers
app.add_exception_handler(HTTPException, api_exception_handler)

# Custom Middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIdMiddleware)

# CORS configuration (Added last so it wraps all middlewares and exception handlers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router
app.include_router(api_v1_router)

@app.get("/")
async def root():
    return {"name": "MiniCommerce V2 Laboratory API", "version": "2.0.0", "status": "running", "docs": "/docs"}
