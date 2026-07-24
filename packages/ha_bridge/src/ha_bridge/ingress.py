from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any


class IngressMiddleware:
    """ASGI middleware that handles Home Assistant Ingress path rewriting.

    Reads X-Ingress-Path from request headers and uses it to strip the
    prefix from PATH_INFO, setting SCRIPT_NAME for downstream ASGI apps.
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
        ingress_path_raw = headers.get(b"x-ingress-path")
        if ingress_path_raw:
            ingress_path = ingress_path_raw.decode("latin-1").rstrip("/")
            path = scope.get("path", "/")
            if path.startswith(ingress_path):
                scope["path"] = path[len(ingress_path):] or "/"
                scope["script_name"] = ingress_path

        await self._app(scope, receive, send)
