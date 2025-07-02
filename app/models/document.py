from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DocumentRecord(BaseModel):
    filename: str
    chunk_ids: List[str]
    uploaded_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
