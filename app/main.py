from fastapi import FastAPI, HTTPException, UploadFile, status
import os

from rag.process import process_pdf
from rag.vector_store import add_chunks_to_vector_store
from app.schemas import UploadResponse
from app.settings import settings

os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY

app = FastAPI()


@app.post('/upload-file', response_model=UploadResponse, description='')
async def upload_file(file: UploadFile):
    """
    Recebe um arquivo PDF, extrai seu conteúdo em chunks e indexa no vector store.

    - O arquivo é temporariamente salvo no disco;
    - Em seguida, é processado e dividido em pedaços de texto (chunks);
    - Os chunks são enviados para um vector store para buscas futuras por similaridade.

    Retorna:
    - O nome do arquivo original;
    - A quantidade de chunks extraídos;
    - Uma mensagem de sucesso.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='invalid file format. Only PDF files are supported.'
        )

    chunks = process_pdf(file)

    add_chunks_to_vector_store(chunks=chunks)

    return {
        'filename': file.filename,
        'total_chunks': len(chunks),
        'message': 'File processed and chunks added to vector store successfully.'
    }
