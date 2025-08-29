from typing import List
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    Path,
    UploadFile,
    status,
    Depends
)
from sqlalchemy import delete, select

from app.dependencies import T_Session
from app.security import get_api_key
from rag.process import process_pdf
from rag.vector_store import (
    add_chunks_to_vector_store,
    delete_chunks_by_ids,
    generate_chunks_ids,
    get_chunks_by_ids
)

from .models import DocumentRecord
from .schemas import DocumentRecordSchema, UploadResponse

router = APIRouter(
    prefix='/documents',
    tags=['Documents'],
    dependencies=[Depends(get_api_key)]
)

@router.post('', response_model=UploadResponse)
async def add_documents(
    session: T_Session, 
    background_tasks: BackgroundTasks, 
    files: List[UploadFile] = File(...),
):
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

        # Calcula o tamanho em MB do arquivo
        content = await file.read()
        size_mb = round(len(content) / (1024 * 1024), 2)  # bytes -> MB
        await file.seek(0)  # reposiciona ponteiro, se precisar reutilizar

        # Salva no DB
        document_record = DocumentRecord(
            filename=file.filename,
            chunks_ids=chunk_ids,
            size_mb=size_mb
        )
        session.add(document_record)
        await session.commit()

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


@router.get('', response_model=List[DocumentRecordSchema])
async def list_files(session: T_Session):
    try:
        result = await session.execute(select(DocumentRecord))
        documents = result.scalars().all()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/{document_id}', description='Remove um arquivo e seus chunks usando o ID.')
async def delete_document(
    session: T_Session,
    document_id: UUID = Path(..., description='ID do documento a ser removido')
):
    """
    Deleta todos os chunks relacionados ao ID do arquivo PDF e remove o registro no banco.
    """

    result = await session.execute(select(DocumentRecord).where(DocumentRecord.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail='Document not found.')

    chunk_ids = document.chunks_ids

    if not chunk_ids:
        raise HTTPException(status_code=404, detail='No associated chunks found for this document.')

    try:
        # Deleta os chunks da vector store
        await delete_chunks_by_ids(chunk_ids)
        
        print(await get_chunks_by_ids(chunk_ids))

        # Deleta registro do documento no Postgres
        await session.execute(delete(DocumentRecord).where(DocumentRecord.id == document_id))
        await session.commit()

        return {'message': f"{len(chunk_ids)} chunk(s) deleted and document removed successfully."}

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error deleting document and chunks: {str(e)}'
        )
