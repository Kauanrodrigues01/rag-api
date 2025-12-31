from typing import List, Optional
from pydantic import BaseModel, Field


class AskQuestionRequest(BaseModel):
    question: str = Field(..., description="Pergunta a ser respondida com base nos documentos")


class Source(BaseModel):
    """Informação sobre a fonte de um trecho da resposta."""
    filename: str = Field(..., description="Nome do arquivo fonte")
    page: Optional[int] = Field(None, description="Número da página (se disponível)")


class AskQuestionResponse(BaseModel):
    answer: str = Field(..., description="Resposta gerada pelo LLM")
    sources: List[Source] = Field(default_factory=list, description="Fontes utilizadas na resposta")
    confidence: Optional[str] = Field(None, description="Nível de confiança da resposta")
