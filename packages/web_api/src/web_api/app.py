import logging
import os
import re
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .ingress import IngressMiddleware, get_application_prefix

_log = logging.getLogger(__name__)

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

    app.add_middleware(IngressMiddleware)

    from .routers import profiles, entries, cycles, insights

    app.include_router(profiles.router)
    app.include_router(entries.router)
    app.include_router(cycles.router)
    app.include_router(insights.router)

    @app.get("/api/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    # ---- TEMPORARY DEBUG endpoints — remove after Ingress fix ----

    @app.get("/api/debug/request")
    async def debug_request(request: Request) -> dict:
        """TEMPORARY: Debug endpoint — dumps request diagnostics."""
        headers = dict(request.headers)
        return {
            "url": str(request.url),
            "base_url": str(request.base_url),
            "path": request.scope.get("path", "N/A"),
            "root_path": request.scope.get("root_path", "N/A"),
            "script_name": request.scope.get("script_name", "N/A"),
            "ingress_header": headers.get("x-ingress-path", "NOT SET"),
            "headers": {
                k: v for k, v in headers.items()
                if "ingress" in k.lower() or "x-" in k.lower()
            },
            "static_dir": STATIC_DIR,
            "static_dir_exists": os.path.isdir(STATIC_DIR),
        }

    @app.get("/api/debug/html", response_class=HTMLResponse)
    async def debug_html(request: Request) -> str:
        """TEMPORARY: Debug endpoint — returns final HTML after base tag injection."""
        index_path = os.path.join(STATIC_DIR, "index.html")
        if not os.path.isfile(index_path):
            return "<h1>index.html not found at {}</h1>".format(index_path)

        html = open(index_path).read()
        prefix = get_application_prefix(request)

        if prefix:
            head_match = re.search(r"<head[^>]*>", html, re.IGNORECASE)
            if head_match:
                insert_pos = head_match.end()
                injection = (
                    f'\n<base href="{prefix}/">'
                    f'\n<script>window.__INGRESS_PATH__ = "{prefix}";</script>'
                )
                html = html[:insert_pos] + injection + html[insert_pos:]

        diagnostic_comment = (
            f"<!-- TEMPORARY DEBUG: script_name='{prefix}' "
            f"base_href='{prefix}/' static_dir='{STATIC_DIR}' -->\n"
        )
        return diagnostic_comment + html

    @app.get("/api/debug/static")
    async def debug_static() -> dict:
        """TEMPORARY: Debug endpoint — list static files."""
        result = {"static_dir": STATIC_DIR, "exists": os.path.isdir(STATIC_DIR)}
        if os.path.isdir(STATIC_DIR):
            result["files"] = os.listdir(STATIC_DIR)
            assets_dir = os.path.join(STATIC_DIR, "assets")
            if os.path.isdir(assets_dir):
                result["assets"] = os.listdir(assets_dir)[:10]
        return result

    # ---- END TEMPORARY DEBUG ----

    # TEMPORARY DEBUG: log all registered routes
    for route in app.routes:
        if hasattr(route, 'path'):
            _log.info("ROUTE: %s %s", getattr(route, 'methods', ['GET']), route.path)
    # END TEMPORARY DEBUG

    # Serve frontend static files and SPA fallback (after all API routes)
    if os.path.isdir(STATIC_DIR):
        app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str, request: Request) -> HTMLResponse:
            # Don't intercept API, docs, or static asset requests
            if full_path.startswith(("api/", "docs", "openapi.json")):
                raise HTTPException(status_code=404)

            index_path = os.path.join(STATIC_DIR, "index.html")
            if not os.path.isfile(index_path):
                raise HTTPException(status_code=404)

            html = open(index_path).read()
            prefix = get_application_prefix(request)
            if prefix:
                head_match = re.search(r"<head[^>]*>", html, re.IGNORECASE)
                if head_match:
                    insert_pos = head_match.end()
                    injection = (
                        f'\n<base href="{prefix}/">'
                        f'\n<script>window.__INGRESS_PATH__ = "{prefix}";</script>'
                    )
                    html = html[:insert_pos] + injection + html[insert_pos:]
            return HTMLResponse(content=html)

    # ---- TEMPORARY DEBUG: startup diagnostics ----

    _log.info("=== Byrd Health Startup Diagnostics ===")
    _log.info("STATIC_DIR: %s", STATIC_DIR)
    _log.info("STATIC_DIR exists: %s", os.path.isdir(STATIC_DIR))
    if os.path.isdir(STATIC_DIR):
        _log.info("STATIC_DIR contents: %s", os.listdir(STATIC_DIR)[:20])
        assets = os.path.join(STATIC_DIR, "assets")
        if os.path.isdir(assets):
            _log.info("Assets dir contents: %s", os.listdir(assets)[:10])
    _log.info(
        "DATABASE_URL: %s",
        os.environ.get("BYRD_DATABASE_URL", os.environ.get("DATABASE_URL", "NOT SET")),
    )
    _log.info("PYTHONPATH: %s", os.environ.get("PYTHONPATH", "NOT SET"))
    _log.info("========================================")

    # ---- END TEMPORARY DEBUG ----

    return app


app = create_app()
