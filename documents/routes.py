from typing import List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)

from rag.mongo_storage import (
    delete_by_filename,
    get_all_filenames,
    get_chunk_ids_by_filename,
    save_chunk_ids,
)
from rag.process import process_pdf
from rag.vector_store import (
    add_chunks_to_vector_store,
    delete_chunks_by_ids,
    generate_chunks_ids,
)

from .schemas import FileItem, UploadResponse

router = APIRouter()


@router.post('', response_model=UploadResponse, description='')
async def add_file(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    """
    Recebe um arquivo PDF, extrai seu conteúdo em chunks e indexa no vector store.
    """
    filenames = []
    total_chunks = 0

    for file in files:
        if file.content_type != 'application/pdf' or not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file format for '{file.filename}'. Only PDF files are supported."
            )

        try:
            chunks = await process_pdf(file, file.filename)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Error processing file: {file.filename}'
            )

        # Gera chunk_ids únicos por arquivo
        chunk_ids = generate_chunks_ids(filename=file.filename, chunks=chunks)

        # Salva os IDs no Mongo por filename
        await save_chunk_ids(file.filename, chunk_ids)

        # Adiciona tarefa assíncrona para adicionar os chunks ao vector store
        background_tasks.add_task(add_chunks_to_vector_store, chunks, chunk_ids)

        filenames.append(file.filename)
        total_chunks += len(chunks)

    return {
        'filenames': filenames,
        'total_files': len(filenames),
        'total_chunks': total_chunks,
        'message': 'Files processed and chunks sent for indexing.'
    }


@router.get('', response_model=List[FileItem])
async def list_uploaded_files():
    """
    Retorna todos os arquivos salvos como uma lista de objetos.
    """
    filenames = await get_all_filenames()
    return [{'filename': name} for name in filenames]


@router.delete('')
async def delete_file(filename: str = Query(..., description="Nome do arquivo para remoção")):
    """
    Deleta todos os chunks relacionados ao nome do arquivo PDF, baseado nos chunk_ids salvos no MongoDB.
    """
    chunk_ids = await get_chunk_ids_by_filename(filename)
    if not chunk_ids:
        raise HTTPException(status_code=404, detail='File not found or no associated chunks.')

    try:
        await delete_chunks_by_ids(chunk_ids)
        await delete_by_filename(filename)  # remove do Mongo também
        return {'message': f"{len(chunk_ids)} chunk(s) of the file '{filename}' deleted successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error deleting chunks: {str(e)}'
        )
