import pytest


@pytest.mark.asyncio
async def test_ask_question_success(mocker, client):
    """
    Test the path to success by asking a question.
    """
    mocked_answer = 'A resposta para sua pergunta é 42.'
    mock_rag = mocker.patch('rag.routes.ask_question_rag', return_value=mocked_answer)

    payload = {'question': 'Qual o sentido da vida?'}

    response = await client.post('/api/rag/ask-question', json=payload)

    assert response.status_code == 200
    assert response.json() == {'answer': mocked_answer}
    mock_rag.assert_awaited_once_with(payload['question'])


@pytest.mark.asyncio
async def test_ask_question_invalid_payload(client):
    """
    Tests the validation of an invalid request payload.
    """
    # Payload inválido: a chave 'query' não existe no schema `AskQuestionRequest`
    invalid_payload = {'query': 'Essa pergunta vai falhar'}

    response = await client.post('/api/rag/ask-question', json=invalid_payload)

    # 422 é o código padrão do FastAPI para erros de validação
    assert response.status_code == 422
    error_details = response.json()['detail'][0]
    assert error_details['type'] == 'missing'
    assert error_details['loc'] == ['body', 'question']
