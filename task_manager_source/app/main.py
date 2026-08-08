from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,
)

from app.api.task_routes import router as task_router
from app.config.database import Base, engine
from app.errors.api_exception import ApiException
from app.middleware.correlation_id import (
    CORRELATION_ID_HEADER,
    CorrelationIdMiddleware,
)
from app.models.api_response import ApiResponse
from app.models.task_entity import TaskEntity

from fastapi.staticfiles import StaticFiles

from app.ui.dashboard_routes import router as dashboard_router

from app.ui.task_excel_routes import (
    router as task_excel_router,
)

Base.metadata.create_all(bind=engine)



app = FastAPI(
    title="Task API",
    description="Local personal task management application",
    version="1.0.0",
)


app.add_middleware(CorrelationIdMiddleware)

app.mount(
    "/static",  
    StaticFiles(directory="static"),name="static",)


app.include_router(
    task_router,
    prefix="/api/v1",
)

app.include_router(dashboard_router)

app.include_router(task_excel_router)

def get_correlation_id(
    request: Request,
) -> str:
    return getattr(
        request.state,
        "correlation_id",
        "unknown",
    )


def create_json_response(
    *,
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    correlation_id = get_correlation_id(request)

    response_body = ApiResponse[None](
        success=False,
        code=code,
        message=message,
        data=None,
        correlation_id=correlation_id,
        details=details,
    )

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(
            response_body.model_dump()
        ),
        headers={
            CORRELATION_ID_HEADER: correlation_id,
        },
    )


@app.exception_handler(ApiException)
async def api_exception_handler(
    request: Request,
    exception: ApiException,
) -> JSONResponse:
    return create_json_response(
        request=request,
        status_code=exception.status_code,
        code=exception.code,
        message=exception.message,
        details=exception.details,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    return create_json_response(
        request=request,
        status_code=(
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ),
        code="VALIDATION_ERROR",
        message=(
            "The request contains invalid "
            "or missing values."
        ),
        details=jsonable_encoder(
            exception.errors()
        ),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exception: StarletteHTTPException,
) -> JSONResponse:
    if exception.status_code == 404:
        code = "RESOURCE_NOT_FOUND"
    elif exception.status_code == 405:
        code = "METHOD_NOT_ALLOWED"
    else:
        code = "HTTP_ERROR"

    return create_json_response(
        request=request,
        status_code=exception.status_code,
        code=code,
        message=str(exception.detail),
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    correlation_id = get_correlation_id(request)

    print(
        "Unexpected error "
        f"[correlation_id={correlation_id}]: "
        f"{exception}"
    )

    return create_json_response(
        request=request,
        status_code=(
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
        code="INTERNAL_ERROR",
        message=(
            "An unexpected server error occurred."
        ),
    )


@app.get(
    "/",
    response_model=ApiResponse[dict[str, str]],
)
def root(
    request: Request,
) -> ApiResponse[dict[str, str]]:
    return ApiResponse[dict[str, str]](
        success=True,
        code="API_RUNNING",
        message="Task API is running.",
        data={
            "application": "Task API",
            "version": "1.0.0",
            "api_base_path": "/api/v1",
        },
        correlation_id=request.state.correlation_id,
    )


@app.get(
    "/health",
    response_model=ApiResponse[dict[str, str]],
)
def health_check(
    request: Request,
) -> ApiResponse[dict[str, str]]:
    return ApiResponse[dict[str, str]](
        success=True,
        code="API_HEALTHY",
        message="Task API is healthy.",
        data={
            "status": "healthy",
        },
        correlation_id=request.state.correlation_id,
    )