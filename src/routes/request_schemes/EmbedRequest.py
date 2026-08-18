from pydantic import BaseModel, Field

from typing import Optional

class EmbedRequest(BaseModel):
    asset_name: Optional[str] = None