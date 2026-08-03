from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        correlation_id = (
            request.headers.get(CORRELATION_ID_HEADER)
            or str(uuid4())
        )

        request.state.correlation_id = correlation_id

        response = await call_next(request)

        response.headers[CORRELATION_ID_HEADER] = correlation_id

        return response