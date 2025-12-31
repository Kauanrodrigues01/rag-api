from typing import List, Optional

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.settings import settings


def split_documents(
    docs: List[Document], 
    chunk_size: Optional[int] = None, 
    chunk_overlap: Optional[int] = None
):
    """
    Divide documentos em chunks usando configurações do settings ou parâmetros customizados.
    
    Args:
        docs: Lista de documentos para dividir
        chunk_size: Tamanho do chunk (usa settings.CHUNK_SIZE se None)
        chunk_overlap: Overlap entre chunks (usa settings.CHUNK_OVERLAP se None)
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.CHUNK_SIZE,
        chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents=docs)
    return chunks
