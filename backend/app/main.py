from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.analysis import router as analysis_router
from app.api.tickets import router as tickets_router
from app.core.config import get_settings
from app.db.session import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    try:
        yield
    finally:
        await async_engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    # Configure CORS for browser requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(tickets_router)
    app.include_router(analysis_router)

    return app


app = create_app()

