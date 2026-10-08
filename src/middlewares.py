from collections.abc import Awaitable, Callable

from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware для проверки заголовки авторизации в запросе."""

    def __init__(self, app: ASGIApp, x_api_key: str) -> None:
        super().__init__(app)
        self._x_api_key = x_api_key

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """."""
        x_api_key = request.headers.get("X-API-key")
        if x_api_key is None or x_api_key != self._x_api_key:
            return JSONResponse(content={"message": "unauthorized"}, status_code=status.HTTP_401_UNAUTHORIZED)
        return await call_next(request)
