from fastapi.testclient import TestClient
from fastapi import UploadFile
from langchain_core.documents import Document


def test_upload_files_success(mocker, client, fake_pdf_upload_file: UploadFile):
    """
    Testa o caminho de sucesso do upload de múltiplos arquivos PDF.
    
    Este é um teste de integração que usa um PDF real (da fixture) para garantir 
    que o `process_pdf` é chamado corretamente. Apenas a tarefa de background 
    é mockada para verificar seu agendamento.
    """
    mock_add_chunks = mocker.patch('app.main.add_chunks_to_vector_store')

    fake_pdf_upload_file.file.seek(0)
    file_content = fake_pdf_upload_file.file.read()
    
    files_to_upload = [
        ('files', (fake_pdf_upload_file.filename, file_content, 'application/pdf')),
    ]

    response = client.post("/upload-files", files=files_to_upload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['filenames'] == [fake_pdf_upload_file.filename]
    assert response_data['total_files'] == 1
    # O processamento real acontece, então verificamos se ao menos 1 chunk foi criado
    assert response_data['total_chunks'] >= 1
    assert 'processed and chunks added' in response_data['message']

    # O TestClient do FastAPI executa tarefas de background imediatamente.
    # Verificamos se a função foi chamada com os chunks corretos.
    mock_add_chunks.assert_called_once()
    call_args = mock_add_chunks.call_args[0][0] # Pega o primeiro argumento posicional
    assert isinstance(call_args, list)
    assert all(isinstance(chunk, Document) for chunk in call_args)
    assert len(call_args) == response_data['total_chunks']


def test_upload_files_invalid_content_type(client):
    """
    Testa a falha ao tentar fazer upload de um arquivo não-PDF.
    Valida se a aplicação retorna um erro 400 Bad Request com a mensagem correta.
    """
    files_to_upload = [
        ('files', ('test.txt', b"este nao e um pdf", 'text/plain'))
    ]

    response = client.post("/upload-files", files=files_to_upload)

    assert response.status_code == 400
    assert response.json()['detail'] == "Invalid file format for 'test.txt'. Only PDF files are supported."


def test_upload_files_processing_error(mocker, client):
    """
    Testa o tratamento de erro se `process_pdf` levantar uma exceção.
    
    Garante que a aplicação lida com falhas internas e retorna 500 Internal Server Error.
    """
    # Simula uma falha inesperada durante o processamento do PDF
    mocker.patch('app.main.process_pdf', side_effect=Exception('Falha de processamento simulada'))
    
    files_to_upload = [
        ('files', ('error.pdf', b'pdf content', 'application/pdf'))
    ]

    response = client.post('/upload-files', files=files_to_upload)

    assert response.status_code == 500
    assert 'Internal Server Error' in response.text


def test_ask_question_success(mocker, client):
    """
    Testa o caminho de sucesso ao fazer uma pergunta.
    
    Mocka a função `ask_question_rag` para isolar a lógica do RAG e testar
    apenas a funcionalidade do endpoint.
    """
    mocked_answer = 'A resposta para sua pergunta é 42.'
    mock_rag = mocker.patch('app.main.ask_question_rag', return_value=mocked_answer)
    
    payload = {'question': 'Qual o sentido da vida?'}

    response = client.post('/ask-question', json=payload)

    assert response.status_code == 200
    assert response.json() == {'answer': mocked_answer}
    mock_rag.assert_awaited_once_with(payload['question'])


def test_ask_question_invalid_payload(client):
    """
    Testa a validação de um payload de requisição inválido.
    
    Verifica se o FastAPI retorna um erro 422 Unprocessable Entity quando
    o corpo da requisição não corresponde ao schema Pydantic.
    """
    # Payload inválido: a chave 'query' não existe no schema `AskQuestionRequest`
    invalid_payload = {'query': 'Essa pergunta vai falhar'}

    response = client.post('/ask-question', json=invalid_payload)

    # 422 é o código padrão do FastAPI para erros de validação
    assert response.status_code == 422
    error_details = response.json()['detail'][0]
    assert error_details['type'] == 'missing'
    assert error_details['loc'] == ['body', 'question']
