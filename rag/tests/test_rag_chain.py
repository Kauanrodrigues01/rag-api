import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_ask_question_success(mocker, mock_vector_store):
    question = 'Qual o sentido da vida?'
    expected_answer = {'answer': '42'}

    mock_get_vector_store = mocker.patch('rag.rag_chain.get_vector_store', return_value=mock_vector_store)

    mock_chain_instance = MagicMock()
    mock_chain_instance.ainvoke = AsyncMock(return_value=expected_answer)
    mock_create_chain = mocker.patch('rag.rag_chain.create_retrieval_chain', return_value=mock_chain_instance)

    mock_prompt = mocker.patch('rag.rag_chain.ChatPromptTemplate')

    from rag.rag_chain import ask_question
    response = await ask_question(question)

    mock_get_vector_store.assert_called_once()

    mock_vector_store.as_retriever.assert_called_once()
    mock_create_chain.assert_called_once()
    mock_chain_instance.ainvoke.assert_awaited_once_with({'input': question})
    assert response == expected_answer['answer']


@pytest.mark.asyncio
async def test_ask_question_chain_exception(mocker, mock_vector_store):
    """
    Testa o tratamento de exceção quando a invocação da cadeia falha.
    """
    question = 'Qualquer pergunta'
    
    mocker.patch('rag.rag_chain.get_vector_store', return_value=mock_vector_store)

    # Mock da cadeia de recuperação para levantar uma exceção
    mock_chain_instance = MagicMock()
    mock_chain_instance.ainvoke = AsyncMock(side_effect=RuntimeError('Erro na API da OpenAI'))
    mocker.patch('rag.rag_chain.create_retrieval_chain', return_value=mock_chain_instance)
    
    from rag.rag_chain import ask_question
    with pytest.raises(RuntimeError, match='Erro na API da OpenAI'):
        await ask_question(question)