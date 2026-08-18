from typing import Literal
from pydantic import BaseModel


class DependencyHealth(BaseModel):
    mongodb: Literal["ok", "unhealthy"]
    vectordb: Literal["ok", "unhealthy"]


class ReadinessResponse(BaseModel):
    status: Literal["ok", "unhealthy"]
    dependencies: DependencyHealth
