import os
import re
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .ingress import IngressMiddleware, get_application_prefix

STATIC_DIR = os.environ.get("STATIC_DIR", "/app/static")


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    import logging
    _log = logging.getLogger(__name__)

    from device_adapters.registry import DeviceRegistry
    from ha_bridge.bridge import HABridge
    from ha_bridge.config import read_ha_config

    from .dependencies import (
        _async_sessionmaker,
        _engine,
        set_device_registry,
        set_ha_bridge,
        set_ws_broker,
    )
    from .websocket import WebSocketBroker

    broker = WebSocketBroker()
    set_ws_broker(broker)
    _log.info("WebSocket broker started")

    registry = DeviceRegistry()
    set_device_registry(registry)

    # Create database tables (migrations for upgrades are managed via alembic)
    async with _engine.begin() as conn:
        from data_service.models import Base
        await conn.run_sync(Base.metadata.create_all)

    bridge_config = read_ha_config()
    bridge = HABridge(bridge_config)
    set_ha_bridge(bridge)
    await bridge.startup()

    # Wire HA sensor entity as device adapter if configured
    if bridge_config.ha_sensor_entity:
        try:
            from device_adapters.adapters.ha_sensor import HASensorAdapter
            adapter = HASensorAdapter(
                entity_id=bridge_config.ha_sensor_entity,
                client=bridge.client,
                poll_interval_seconds=bridge_config.poll_interval_seconds,
            )
            registry.register(adapter)
            await adapter.connect()
            _log.info("HA sensor adapter registered: %s", bridge_config.ha_sensor_entity)
        except Exception:
            _log.exception("Failed to register HA sensor adapter")

    try:
        from data_service.service import DataService

        from .analysis import enrich_insights_for_publishing, run_cycle_analysis

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
                enriched = await enrich_insights_for_publishing(
                    data_svc, cycle.id, profile.id, insights
                )
                await bridge.publish_insights(
                    slug=profile.slug,
                    name=profile.name,
                    temp_unit=profile.temp_unit,
                    insights=enriched,
                    next_period=enriched.get("next_period_date"),
                )
            _log.info("Published HA entities for %d profile(s)", len(profiles))
    except Exception:
        _log.exception("Failed to publish initial HA entities")

    try:
        await bridge.register_dashboard_card("ha-card.js")
    except Exception:
        _log.exception("Failed to register Lovelace dashboard card")

    yield

    await bridge.shutdown()
    set_ha_bridge(None)
    set_device_registry(None)
    set_ws_broker(None)
    _log.info("WebSocket broker stopped")
    await _engine.dispose()


def create_app(lifespan: Callable[..., Any] | None = None) -> FastAPI:
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

    from .routers import calendar, cycles, devices, entries, insights, profiles, ws

    app.include_router(profiles.router)
    app.include_router(entries.router)
    app.include_router(cycles.router)
    app.include_router(insights.router)
    app.include_router(ws.router)
    app.include_router(devices.router)
    app.include_router(calendar.router)

    @app.get("/api/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    _card_paths = [
        Path(__file__).resolve().parent.parent.parent.parent.parent
        / "packages" / "ha_bridge" / "src" / "ha_bridge" / "card" / "ha-card.js",
        Path(STATIC_DIR) / "ha-card.js",
    ]

    @app.get("/ha-card.js")
    async def serve_card() -> FileResponse:
        for p in _card_paths:
            if p.is_file():
                return FileResponse(str(p), media_type="application/javascript")
        raise HTTPException(status_code=404, detail="Card module not found")

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

            with open(index_path) as f:
                html = f.read()
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
