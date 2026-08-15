"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.health import router as health_router
from app.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title="Student Support AI",
        description="Student-only agentic support layer for EdTech platforms.",
        version="0.1.0",
    )
    app.include_router(health_router)
    app.state.settings = settings
    return app


app = create_app()
