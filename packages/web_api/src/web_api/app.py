import os
from collections.abc import Awaitable, Callable, MutableMapping
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from .config import settings

STATIC_DIR = os.environ.get("STATIC_DIR", "/app/static")


class IngressMiddleware:
    """ASGI middleware that strips the HA Ingress path prefix.

    Reads X-Ingress-Path from headers and strips it from PATH_INFO,
    setting SCRIPT_NAME so downstream apps see clean paths.
    """

    def __init__(self, app: Callable[..., Awaitable[None]]) -> None:
        self._app = app

    async def __call__(
        self,
        scope: MutableMapping[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        ingress_path = headers.get(b"x-ingress-path", b"").decode("latin-1").rstrip("/")
        if ingress_path:
            path = scope.get("path", "/")
            if path.startswith(ingress_path):
                scope["path"] = path[len(ingress_path):] or "/"
                scope["script_name"] = ingress_path

        await self._app(scope, receive, send)


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

    app.add_middleware(IngressMiddleware)

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
        async def serve_spa(full_path: str, request: Request) -> Response:
            # Don't intercept API, docs, or static asset requests
            if full_path.startswith(("api/", "docs", "openapi.json")):
                raise HTTPException(status_code=404)

            index_path = os.path.join(STATIC_DIR, "index.html")
            if not os.path.isfile(index_path):
                raise HTTPException(status_code=404)

            html = open(index_path).read()
            script_name = request.scope.get("script_name", "")
            if script_name:
                html = html.replace("<head>", f'<head><base href="{script_name}/">')
            return HTMLResponse(content=html)

    return app


app = create_app()
