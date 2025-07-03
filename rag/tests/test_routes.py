def test_ask_question_success(mocker, client):
    """
    Testa o caminho de sucesso ao fazer uma pergunta.
    
    Mocka a função `ask_question_rag` para isolar a lógica do RAG e testar
    apenas a funcionalidade do endpoint.
    """
    mocked_answer = 'A resposta para sua pergunta é 42.'
    mock_rag = mocker.patch('rag.routes.ask_question_rag', return_value=mocked_answer)

    payload = {'question': 'Qual o sentido da vida?'}

    response = client.post('/rag/ask-question', json=payload)

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

    response = client.post('/rag/ask-question', json=invalid_payload)

    # 422 é o código padrão do FastAPI para erros de validação
    assert response.status_code == 422
    error_details = response.json()['detail'][0]
    assert error_details['type'] == 'missing'
    assert error_details['loc'] == ['body', 'question']
