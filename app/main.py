import os

from fastapi import FastAPI, HTTPException, UploadFile, status

from app.schemas import AskQuestionRequest, AskQuestionResponse, UploadResponse
from app.settings import settings
from rag.process import process_pdf
from rag.rag_chain import ask_question as ask_question_rag
from rag.vector_store import add_chunks_to_vector_store

os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY

app = FastAPI()


@app.post('/upload-file', response_model=UploadResponse, description='')
async def upload_file(file: UploadFile):
    """
    Recebe um arquivo PDF, extrai seu conteúdo em chunks e indexa no vector store.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='invalid file format. Only PDF files are supported.'
        )

    chunks = await process_pdf(file)

    await add_chunks_to_vector_store(chunks=chunks)

    return {
        'filename': file.filename,
        'total_chunks': len(chunks),
        'message': 'File processed and chunks added to vector store successfully.'
    }


@app.post('/ask-question', response_model=AskQuestionResponse)
async def ask_question(data: AskQuestionRequest):
    """
    Processa uma pergunta e retorna uma resposta gerada com base em documentos vetorizados.
    """
    answer = await ask_question_rag(data.question)
    return {'answer': answer}
