from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson.objectid import ObjectId

class Chunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id") # if no value passed set id to None
    chunk_text: str = Field(..., min_length=1) # must pass value for it with min length 1
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId

    model_config = ConfigDict(
        arbitrary_types_allowed = True #don't complain about ObjectId as unkown type. validate it too.
    )