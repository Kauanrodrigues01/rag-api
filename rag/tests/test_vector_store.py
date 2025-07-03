import re

import pytest
from langchain_core.documents import Document

from rag.vector_store import (
    add_chunks_to_vector_store,
    generate_chunks_ids,
    get_vector_store,
)


def test_get_vector_store_singleton(mocker):
    """
    Valida que get_vector_store funciona como um singleton, instanciando
    Chroma e OpenAIEmbeddings apenas uma vez.
    """
    mock_embeddings = mocker.patch('rag.vector_store.OpenAIEmbeddings')
    mock_chroma = mocker.patch('rag.vector_store.Chroma')

    store1 = get_vector_store()
    store2 = get_vector_store()

    assert store1 is store2
    mock_embeddings.assert_called_once()
    mock_chroma.assert_called_once()


def test_get_vector_store_instantiation_error(mocker):
    """
    Testa o tratamento de erro se a instanciação do Chroma falhar.
    """
    mocker.patch('rag.vector_store.OpenAIEmbeddings')
    mocker.patch('rag.vector_store.Chroma', side_effect=Exception("Falha na conexão com Chroma"))

    with pytest.raises(Exception, match='Falha na conexão com Chroma'):
        get_vector_store()


@pytest.mark.asyncio
async def test_add_chunks_to_vector_store_success(mocker, mock_vector_store, dummy_documents):
    """
    Testa se a função `add_chunks_to_vector_store` chama corretamente
    o método `aadd_documents` da vector store.
    """
    mocker.patch('rag.vector_store.get_vector_store', return_value=mock_vector_store)
    
    chunks_ids = generate_chunks_ids(filename='test.pdf', chunks=dummy_documents)

    await add_chunks_to_vector_store(dummy_documents, chunks_ids)

    mock_vector_store.aadd_documents.assert_awaited_once_with(documents=dummy_documents, ids=chunks_ids)


@pytest.mark.asyncio
async def test_add_chunks_to_vector_store_error(mocker, mock_vector_store, dummy_documents):
    """
    Testa o tratamento de erro quando `aadd_documents` falha.
    """
    mock_vector_store.aadd_documents.side_effect = Exception("Erro ao adicionar documentos")
    mocker.patch('rag.vector_store.get_vector_store', return_value=mock_vector_store)

    chunks_ids = generate_chunks_ids(filename='test.pdf', chunks=dummy_documents)

    with pytest.raises(Exception, match="Erro ao adicionar documentos"):
        await add_chunks_to_vector_store(dummy_documents, chunks_ids)


def test_generate_chunks_ids():
    filename = "example.pdf"
    chunks = [Document(page_content="Chunk 1"), Document(page_content="Chunk 2")]

    chunk_ids = generate_chunks_ids(filename, chunks)

    # Verifica se a lista de IDs tem o mesmo tamanho da lista de chunks
    assert len(chunk_ids) == len(chunks)

    # Verifica se cada ID segue o padrão esperado e contém UUIDs válidos
    for i, chunk_id in enumerate(chunk_ids):
        # Regex para validar formato: example.pdf_chunk_i_uuid
        pattern = rf"^{filename}_chunk_{i}_[0-9a-fA-F-]{{36}}$"
        assert re.match(pattern, chunk_id), f'ID {chunk_id} não está no formato esperado'
