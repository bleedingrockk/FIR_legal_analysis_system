"""
Main entry point for FIR Legal Analysis API application.
"""

import sys
import io
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app.routes import api_router
from app.routes.config import STATIC_DIR

# Initialize FastAPI app
app = FastAPI(
    title="FIR Legal Analysis API",
    description="API for analyzing FIR documents and mapping legal sections",
    version="1.0.0"
)

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routes
app.include_router(api_router)


def main():
    """Launch the FastAPI application server."""
    print("=" * 80)
    print("🚀 Starting FIR Legal Analysis API Server")
    print("=" * 80)
    print("📄 API Documentation: http://localhost:8000/docs")
    print("📋 Upload Page: http://localhost:8000/")
    print("=" * 80)
    
    # Use string reference for reload to work properly
    uvicorn.run(
        "main:app",  # String reference required for auto-reload
        host="0.0.0.0",
        port=8000,
        reload=False,  # Enable auto-reload during development
        log_level="info"
    )


if __name__ == "__main__":
    main()
