from pydantic import BaseModel, Field

from typing import Optional

class EmbedRequest(BaseModel):
    asset_name: Optional[str] = None

class EmbedResponse(BaseModel):
    status: str

class RetrieveRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class RetriveResponse(BaseModel):
    status: str
    retrieved_documents_with_scores: list[dict]

class CollectionInfoResponse(BaseModel):
    status: str
    collection_status: str
    points_count: int
    vectors_config: dict

class ChatResponse(BaseModel):
    status: str
    answer: str
    chat_history: list[dict]