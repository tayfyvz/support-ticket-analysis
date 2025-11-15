from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

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

    @app.get("/healthz")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(tickets_router)

    return app


app = create_app()

