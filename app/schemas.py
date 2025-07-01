from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    total_chunks: int
    message: str


class AskQuestionRequest(BaseModel):
    question: str


class AskQuestionResponse(BaseModel):
    answer: str
