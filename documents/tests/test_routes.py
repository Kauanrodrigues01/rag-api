from fastapi import UploadFile
from langchain_core.documents import Document


def test_add_files_success(mocker, client, fake_pdf_upload_file: UploadFile):
    """
    Testa o caminho de sucesso do upload de múltiplos arquivos PDF.
    
    Este é um teste de integração que usa um PDF real (da fixture) para garantir 
    que o `process_pdf` é chamado corretamente. Apenas a tarefa de background 
    é mockada para verificar seu agendamento.
    """
    mock_add_chunks = mocker.patch('documents.routes.add_chunks_to_vector_store')

    fake_pdf_upload_file.file.seek(0)
    file_content = fake_pdf_upload_file.file.read()

    files_to_upload = [
        ('files', (fake_pdf_upload_file.filename, file_content, 'application/pdf')),
    ]

    response = client.post('/documents', files=files_to_upload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['filenames'] == [fake_pdf_upload_file.filename]
    assert response_data['total_files'] == 1
    # O processamento real acontece, então verificamos se ao menos 1 chunk foi criado
    assert response_data['total_chunks'] >= 1
    assert 'Files processed and chunks sent for indexing.' == response_data['message']

    # O TestClient do FastAPI executa tarefas de background imediatamente.
    # Verificamos se a função foi chamada com os chunks corretos.
    mock_add_chunks.assert_called_once()
    call_args = mock_add_chunks.call_args[0][0]  # Pega o primeiro argumento posicional
    assert isinstance(call_args, list)
    assert all(isinstance(chunk, Document) for chunk in call_args)
    assert len(call_args) == response_data['total_chunks']


def test_add_files_invalid_content_type(client):
    """
    Testa a falha ao tentar fazer upload de um arquivo não-PDF.
    Valida se a aplicação retorna um erro 400 Bad Request com a mensagem correta.
    """
    files_to_upload = [
        ('files', ('test.txt', b"este nao e um pdf", 'text/plain'))
    ]

    response = client.post('/documents', files=files_to_upload)

    assert response.status_code == 400
    assert response.json()['detail'] == "Invalid file format for 'test.txt'. Only PDF files are supported."


def test_add_files_processing_error(mocker, client):
    """
    Testa o tratamento de erro se `process_pdf` levantar uma exceção.
    
    Garante que a aplicação lida com falhas internas e retorna 500 Internal Server Error.
    """
    # Simula uma falha inesperada durante o processamento do PDF
    mocker.patch('documents.routes.process_pdf', side_effect=Exception('Falha de processamento simulada'))

    files_to_upload = [
        ('files', ('error.pdf', b'pdf content', 'application/pdf'))
    ]

    response = client.post('/documents', files=files_to_upload)

    assert response.status_code == 500
    assert response.json() == {'detail': 'Error processing file: error.pdf'}