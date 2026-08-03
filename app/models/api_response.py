from typing import Any, Generic, TypeVar

from pydantic import BaseModel


DataType = TypeVar("DataType")


class ApiResponse(BaseModel, Generic[DataType]):
    success: bool
    code: str
    message: str
    data: DataType | None = None
    correlation_id: str
    details: list[dict[str, Any]] | None = None