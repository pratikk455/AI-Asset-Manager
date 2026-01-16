"""
Shrestha Capital - FastAPI Application

Main entry point for the REST API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import init_db
from api.routes import analyze, funds, discover, risk, portfolio, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown"""
    # Startup
    print("Starting Shrestha Capital API...")
    await init_db()
    print("Database initialized")
    yield
    # Shutdown
    print("Shutting down Shrestha Capital API...")


# Create app
app = FastAPI(
    title="Shrestha Capital API",
    description="AI-Powered Asset Management System",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(funds.router, prefix="/api", tags=["Funds"])
app.include_router(discover.router, prefix="/api", tags=["Discovery"])
app.include_router(risk.router, prefix="/api", tags=["Risk"])
app.include_router(portfolio.router, prefix="/api", tags=["Portfolio"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "name": "Shrestha Capital API",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}
