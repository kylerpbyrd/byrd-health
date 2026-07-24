import os
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings

STATIC_DIR = os.environ.get("STATIC_DIR", "/app/static")


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    from .dependencies import _engine

    async with _engine.begin() as conn:
        from data_service.models import Base

        await conn.run_sync(Base.metadata.create_all)
    yield
    await _engine.dispose()


def create_app(lifespan: Optional[Callable[..., Any]] = None) -> FastAPI:
    effective_lifespan = lifespan if lifespan is not None else _lifespan
    app = FastAPI(
        title="Byrd Health API",
        version="1.0.0",
        lifespan=effective_lifespan,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from .routers import profiles, entries, cycles, insights

    app.include_router(profiles.router)
    app.include_router(entries.router)
    app.include_router(cycles.router)
    app.include_router(insights.router)

    @app.get("/api/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    # Serve frontend static files and SPA fallback (after all API routes)
    if os.path.isdir(STATIC_DIR):
        app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str) -> FileResponse:
            # Don't intercept API, docs, or static asset requests
            if full_path.startswith(("api/", "docs", "openapi.json")):
                raise HTTPException(status_code=404)

            index_path = os.path.join(STATIC_DIR, "index.html")
            if not os.path.isfile(index_path):
                raise HTTPException(status_code=404)
            return FileResponse(index_path)

    return app


app = create_app()
