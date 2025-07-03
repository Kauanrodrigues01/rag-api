from fastapi import FastAPI

from documents.routes import router as documents_router
from rag.routes import router as rag_router

app = FastAPI(title='RAG API')

app.include_router(documents_router, prefix='/documents', tags=['Documents'])
app.include_router(rag_router, prefix='/rag', tags=['RAG'])
