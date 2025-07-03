import pytest

from rag.process import process_pdf


@pytest.mark.asyncio
async def test_process_pdf_success(fake_pdf_upload_file):
    """
    Testa se process_pdf processa um PDF válido com sucesso.
    """
    chunks = await process_pdf(fake_pdf_upload_file, 'test.pdf')

    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(hasattr(chunk, 'page_content') for chunk in chunks)


@pytest.mark.asyncio
async def test_process_pdf_file_read_error(mocker, fake_pdf_upload_file):
    """
    Testa o tratamento de erro quando a leitura do UploadFile falha.
    """
    mocker.patch.object(fake_pdf_upload_file, 'read', side_effect=IOError('Erro simulado'))

    with pytest.raises(IOError, match='Erro simulado'):
        await process_pdf(fake_pdf_upload_file, 'test.pdf')


@pytest.mark.asyncio
async def test_process_pdf_loader_error(mocker, fake_pdf_upload_file):
    """
    Testa o tratamento de erro quando o PyPDFLoader falha.
    """
    # Mockar a classe PyPDFLoader para lançar exceção
    mock_loader = mocker.patch('rag.process.PyPDFLoader')
    instance = mock_loader.return_value
    instance.load.side_effect = Exception('Erro ao carregar PDF')

    # Pula split_documents pois nem será chamado
    mocker.patch('rag.process.split_documents')

    with pytest.raises(Exception, match='Erro ao carregar PDF'):
        await process_pdf(fake_pdf_upload_file, 'test.pdf')
