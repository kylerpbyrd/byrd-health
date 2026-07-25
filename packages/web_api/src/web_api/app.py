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

STATIC_DIR = os.environ.get("STATIC_DIR", "/app/static")


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    import logging
    _log = logging.getLogger(__name__)

    from .dependencies import _engine, _async_sessionmaker, set_ha_bridge
    from ha_bridge.bridge import HABridge
    from ha_bridge.config import read_ha_config

    async with _engine.begin() as conn:
        from data_service.models import Base

        await conn.run_sync(Base.metadata.create_all)

    bridge_config = read_ha_config()
    bridge = HABridge(bridge_config)
    set_ha_bridge(bridge)

    try:
        from data_service.service import DataService
        from .analysis import run_cycle_analysis

        async with _async_sessionmaker() as session:
            data_svc = DataService(session)
            profiles = await data_svc.profiles.get_all()
            for profile in profiles:
                if not profile.is_active:
                    continue
                cycle = await data_svc.cycles.get_or_create_current(profile.id)
                insights = await run_cycle_analysis(
                    data_svc=data_svc,
                    cycle_id=cycle.id,
                    profile_id=profile.id,
                    cycle_start_date=cycle.start_date,
                    cycle_end_date=cycle.end_date,
                )
                await bridge.publish_insights(
                    slug=profile.slug,
                    name=profile.name,
                    temp_unit=profile.temp_unit,
                    insights=insights,
                    next_period=insights.get("next_period_date"),
                )
            _log.info("Published HA entities for %d profile(s)", len(profiles))
    except Exception:
        _log.exception("Failed to publish initial HA entities")

    yield

    await bridge.stop_polling()
    set_ha_bridge(None)
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

    return app


app = create_app()
