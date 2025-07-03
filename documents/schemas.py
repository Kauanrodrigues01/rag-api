from typing import List

from pydantic import BaseModel


class UploadResponse(BaseModel):
    filenames: List[str]
    total_files: int
    total_chunks: int
    message: str


class FileItem(BaseModel):
    filename: str
