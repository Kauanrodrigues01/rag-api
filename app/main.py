import os
from typing import List

from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.schemas import AskQuestionRequest, AskQuestionResponse, UploadResponse
from app.settings import settings
from rag.process import process_pdf
from rag.rag_chain import ask_question as ask_question_rag
from rag.vector_store import add_chunks_to_vector_store

os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY

app = FastAPI()


@app.post('/upload-files', response_model=UploadResponse, description='')
async def upload_file(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    """
    Recebe um arquivo PDF, extrai seu conteúdo em chunks e indexa no vector store.
    """
    all_chunks = []
    for file in files:
        if file.content_type != 'application/pdf' or not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file format for '{file.filename}'. Only PDF files are supported."
            )

        chunks = await process_pdf(file)
        all_chunks.extend(chunks)

    background_tasks.add_task(add_chunks_to_vector_store, all_chunks)

    return {
        'filenames': [file.filename for file in files],
        'total_files': len(files),
        'total_chunks': len(all_chunks),
        'message': 'File processed and chunks added to vector store successfully.'
    }


@app.post('/ask-question', response_model=AskQuestionResponse)
async def ask_question(data: AskQuestionRequest):
    """
    Processa uma pergunta e retorna uma resposta gerada com base em documentos vetorizados.
    """
    answer = await ask_question_rag(data.question)
    return {'answer': answer}
