from typing import Optional

from pydantic import BaseModel
from ..enums.ResponseEnums import ResponseStatus

class AssetUploadResponse(BaseModel):
    status: str
    asset_name: Optional[str] = None
    project_id: Optional[str] = None
    asset_id: Optional[str] = None

class ProcessRequest(BaseModel):
    asset_name: Optional[str] = None
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0

class ProcessResponse(BaseModel):
    status: str
    total_chunks_created: int
    successful_asset_processed: int