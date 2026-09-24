import uuid

from pydantic import BaseModel, Field, ConfigDict


class Chunk(BaseModel):
    id: uuid.UUID | None = None # if no value passed set id to None
    chunk_text: str = Field(min_length=1) # must pass value for it with min length 1
    chunk_metadata: dict
    chunk_order: int = Field(gt=0)
    chunk_project_id: uuid.UUID
    chunk_asset_id: uuid.UUID
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed = True #don't complain about ObjectId as unkown type. validate it too.
    )