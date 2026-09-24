from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime, timezone
import uuid

class Asset(BaseModel):
    id: uuid.UUID | None = None
    asset_project_id: uuid.UUID
    asset_type: str = Field(min_length=1)
    asset_name: str = Field(min_length=1)
    asset_size: int | None = Field(None, ge=0)
    asset_config: dict | None = None
    asset_pushed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        from_attributes=True,
    )