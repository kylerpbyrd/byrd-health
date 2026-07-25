"""Single ingress abstraction for deployment prefix logic.

Every subsystem MUST use `get_application_prefix()` for:
    - HTML generation (base tag, window.__INGRESS_PATH__)
    - Static asset URLs
    - API URL generation
    - WebSocket endpoints
"""

from collections.abc import Awaitable, MutableMapping
from typing import Any

from fastapi import Request


class IngressMiddleware:
    """ASGI middleware that strips the Home Assistant Ingress path prefix.

    Reads X-Ingress-Path from request headers, strips it from PATH_INFO,
    and sets SCRIPT_NAME so downstream FastAPI routes see clean paths.

    This middleware is deployment-agnostic: it adapts to whatever prefix
    the reverse proxy sends via the X-Ingress-Path header.
    """

    def __init__(self, app):
        self._app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        ingress_path = (
            headers.get(b"x-ingress-path", b"")
            .decode("latin-1")
            .rstrip("/")
        )

        if ingress_path:
            path = scope.get("path", "/")
            # HA Supervisor may already strip the prefix before forwarding.
            # Strip only when the path still includes it (safety net),
            # but ALWAYS set script_name so downstream code knows the prefix.
            if path.startswith(ingress_path):
                scope["path"] = path[len(ingress_path):] or "/"
            scope["script_name"] = ingress_path

        await self._app(scope, receive, send)


def get_application_prefix(request: Request) -> str:
    """Return the deployment prefix for the current request.

    Returns the ingress path (e.g., '/app/5bb02542_byrd_health_fertility')
    or '' if not behind an ingress proxy.

    This is the SINGLE SOURCE OF TRUTH for all deployment prefix logic.
    Every subsystem that generates URLs MUST use this function.
    """
    return request.scope.get("script_name", "")
