from pydantic import BaseModel

class RetrievedDocument(BaseModel):
    retrieved_text: str
    score: float