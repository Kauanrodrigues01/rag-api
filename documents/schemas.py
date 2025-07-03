from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class UploadResponse(BaseModel):
    filenames: List[str]
    total_files: int
    total_chunks: int
    message: str


class DocumentRecordSchema(BaseModel):
    id: UUID
    filename: str
    size_mb: float
    chunks_ids: List[str]
    created_at: datetime
