from uuid import uuid4

import pytest
from fastapi import UploadFile
from langchain_core.documents import Document
from sqlalchemy import insert, select

from documents.models import DocumentRecord


# Test POST /documents
@pytest.mark.asyncio
async def test_add_douments_success(mocker, client, session, fake_pdf_upload_file: UploadFile):
    """
    Successful single PDF upload with chunk generation and DB persistence
    """
    mock_add_chunks = mocker.patch('documents.routes.add_chunks_to_vector_store')

    fake_pdf_upload_file.file.seek(0)
    file_content = fake_pdf_upload_file.file.read()

    files_to_upload = [
        ('files', (fake_pdf_upload_file.filename, file_content, 'application/pdf')),
    ]

    response = await client.post('/documents', files=files_to_upload)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data['filenames'] == [fake_pdf_upload_file.filename]
    assert response_data['total_files'] == 1
    assert response_data['total_chunks'] >= 1
    assert response_data['message'] == 'Files processed and chunks sent for indexing.'

    mock_add_chunks.assert_called_once()
    call_args = mock_add_chunks.call_args[0][0]
    assert isinstance(call_args, list)
    assert all(isinstance(chunk, Document) for chunk in call_args)
    assert len(call_args) == response_data['total_chunks']

    stmt = select(DocumentRecord).where(DocumentRecord.filename == fake_pdf_upload_file.filename)
    result = await session.execute(stmt)
    document_record_db = result.scalar_one_or_none()
    assert document_record_db is not None
    assert document_record_db.chunks_ids[0].startswith(f'{fake_pdf_upload_file.filename}_chunk_0_')


@pytest.mark.asyncio
async def test_add_documents_multiple_files_coverage(mocker, client, fake_pdf_upload_file):
    mocker.patch('documents.routes.add_chunks_to_vector_store')

    fake_pdf_upload_file.file.seek(0)
    file_bytes = fake_pdf_upload_file.file.read()

    files_to_upload = [
        ('files', (f'one_{fake_pdf_upload_file.filename}', file_bytes, 'application/pdf')),
        ('files', (f'two_{fake_pdf_upload_file.filename}', file_bytes, 'application/pdf')),
    ]

    response = await client.post('/documents', files=files_to_upload)

    assert response.status_code == 200
    data = response.json()
    assert data['total_files'] == 2
    assert 'one_' in data['filenames'][0] or 'two_' in data['filenames'][0]
    assert 'Files processed and chunks sent for indexing.' in data['message']


@pytest.mark.asyncio
async def test_add_douments_invalid_content_type(client, session):
    """
    Rejects non-PDF file upload with 400 error
    """
    files_to_upload = [
        ('files', ('test.txt', b'not a pdf', 'text/plain'))
    ]

    response = await client.post('/documents', files=files_to_upload)

    assert response.status_code == 400
    assert response.json()['detail'] == "Invalid file format for 'test.txt'. Only PDF files are supported."

    stmt = select(DocumentRecord)
    result = await session.execute(stmt)
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_add_douments_processing_error(mocker, client, session):
    """
    Handles PDF processing failure with 500 error
    """
    mocker.patch('documents.routes.process_pdf', side_effect=Exception('Simulated failure'))

    files_to_upload = [
        ('files', ('error.pdf', b'pdf content', 'application/pdf'))
    ]

    response = await client.post('/documents', files=files_to_upload)

    assert response.status_code == 500
    assert response.json() == {'detail': 'Error processing file: error.pdf'}

    stmt = select(DocumentRecord)
    result = await session.execute(stmt)
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_add_multiple_files_success(mocker, client, session, fake_pdf_upload_file):
    """
    Uploads multiple PDF files and persists each
    """
    mocker.patch('documents.routes.add_chunks_to_vector_store')
    fake_pdf_upload_file.file.seek(0)
    content = fake_pdf_upload_file.file.read()

    files_to_upload = [
        ('files', (f'copy1_{fake_pdf_upload_file.filename}', content, 'application/pdf')),
        ('files', (f'copy2_{fake_pdf_upload_file.filename}', content, 'application/pdf')),
    ]

    response = await client.post('/documents', files=files_to_upload)
    assert response.status_code == 200
    data = response.json()
    assert data['total_files'] == 2
    assert len(data['filenames']) == 2
    assert data['total_chunks'] >= 2


@pytest.mark.asyncio
async def test_chunk_id_format(client, session, fake_pdf_upload_file, mocker):
    """
    Ensures chunk_ids follow naming pattern
    """
    mocker.patch('documents.routes.add_chunks_to_vector_store')
    fake_pdf_upload_file.file.seek(0)
    content = fake_pdf_upload_file.file.read()

    files_to_upload = [
        ('files', (fake_pdf_upload_file.filename, content, 'application/pdf')),
    ]

    response = await client.post('/documents', files=files_to_upload)
    assert response.status_code == 200

    stmt = select(DocumentRecord).where(DocumentRecord.filename == fake_pdf_upload_file.filename)
    result = await session.execute(stmt)
    doc = result.scalar_one_or_none()
    assert doc
    assert all(cid.startswith(f'{fake_pdf_upload_file.filename}_chunk_') for cid in doc.chunks_ids)


# Test GET /documents
@pytest.mark.asyncio
async def test_list_documents_returns_all_documents(client, session):
    """
    Returns all document records in DB
    """
    # Cria documentos no banco
    docs = [
        {'filename': 'file1.pdf', 'size_mb': 0.5, 'chunks_ids': ['file1_chunk_0']},
        {'filename': 'file2.pdf', 'size_mb': 1.2, 'chunks_ids': ['file2_chunk_0', 'file2_chunk_1']}
    ]
    await session.execute(insert(DocumentRecord), docs)
    await session.commit()

    response = await client.get('/documents')
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    filenames = [doc['filename'] for doc in data]
    assert 'file1.pdf' in filenames
    assert 'file2.pdf' in filenames


@pytest.mark.asyncio
async def test_list_documents_returns_empty_list(client):
    """
    Returns empty list when no documents exist
    """
    response = await client.get('/documents')
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_documents_schema_format(client, session):
    """
    Response matches schema: filename, size_mb, chunks_ids, created_at
    """
    document = DocumentRecord(
        filename='example.pdf',
        size_mb=1.0,
        chunks_ids=['chunk_1', 'chunk_2']
    )
    session.add(document)
    await session.commit()

    response = await client.get('/documents')
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    item = data[0]

    assert set(item.keys()) == {'id', 'filename', 'size_mb', 'chunks_ids', 'created_at'}
    assert item['filename'] == 'example.pdf'
    assert item['size_mb'] == 1.0
    assert isinstance(item['chunks_ids'], list)
    assert len(item['chunks_ids']) == 2


@pytest.mark.asyncio
async def test_list_documents_db_error_handled(mocker, client, session):
    """
    Simulates DB error and ensures 500 is returned
    """
    mocker.patch.object(session, 'execute', side_effect=Exception('DB failure'))

    response = await client.get('/documents')

    assert response.status_code == 500


# Test DELETE /documents
@pytest.mark.asyncio
async def test_delete_document_success(mocker, client, session):
    """
    Deletes document and chunks successfully, checking DB integration.
    """
    fake_chunk_ids = ['chunk1', 'chunk2']

    # Cria e salva documento no banco real de teste
    document = DocumentRecord(filename='test.pdf', chunks_ids=fake_chunk_ids, size_mb=1.0)
    session.add(document)
    await session.commit()

    # Mock delete_chunks_by_ids para simular sucesso sem executar a função real
    mock_delete_chunks = mocker.patch('documents.routes.delete_chunks_by_ids', return_value=None)

    response = await client.delete(f'/documents/{document.id}')

    assert response.status_code == 200
    assert response.json() == {'message': f"{len(fake_chunk_ids)} chunk(s) deleted and document removed successfully."}
    mock_delete_chunks.assert_called_once_with(fake_chunk_ids)

    # Verifica se o documento realmente foi removido do DB
    deleted_doc = await session.get(DocumentRecord, document.id)
    assert deleted_doc is None


@pytest.mark.asyncio
async def test_delete_document_not_found(client):
    """
    Returns 404 if document does not exist.
    """
    non_existent_uuid = uuid4()  # UUID válido, mas inexistente no DB

    response = await client.delete(f'/documents/{non_existent_uuid}')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Document not found.'


@pytest.mark.asyncio
async def test_delete_document_no_chunks(client, session):
    """
    Returns 404 if document has no associated chunks.
    """
    # Cria documento sem chunks
    document = DocumentRecord(filename='empty.pdf', chunks_ids=[], size_mb=1.0)
    session.add(document)
    await session.commit()

    response = await client.delete(f'/documents/{document.id}')
    assert response.status_code == 404
    assert response.json()['detail'] == 'No associated chunks found for this document.'


@pytest.mark.asyncio
async def test_delete_document_internal_error(mocker, client, session):
    """
    Returns 500 if an error occurs during chunk deletion.
    """
    fake_chunk_ids = ['chunk1']

    document = DocumentRecord(filename='error.pdf', chunks_ids=fake_chunk_ids, size_mb=1.0)
    session.add(document)
    await session.commit()

    # Força erro na função de deletar chunks
    mocker.patch('documents.routes.delete_chunks_by_ids', side_effect=Exception('Vector store error'))

    response = await client.delete(f'/documents/{document.id}')

    assert response.status_code == 500
    assert 'Error deleting document and chunks' in response.json()['detail']

    await session.refresh(document)

    assert document is not None
    assert document.id == document.id
