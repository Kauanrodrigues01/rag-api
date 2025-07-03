from langchain_core.documents import Document

from rag.splitter import split_documents


def test_split_documents_default_parameters(dummy_documents):
    """
    Valida a divisão de documentos com os parâmetros padrão.
    """
    chunks = split_documents(dummy_documents)

    assert isinstance(chunks, list)
    assert all(isinstance(chunk, Document) for chunk in chunks)
    assert len(chunks) > 0


def test_split_documents_custom_parameters():
    """
    Valida a divisão de documentos com chunk_size e chunk_overlap customizados,
    garantindo que a lógica de divisão seja respeitada.
    """
    long_text = 'a' * 150
    doc = [Document(page_content=long_text)]

    chunks = split_documents(doc, chunk_size=100, chunk_overlap=20)

    assert len(chunks) == 2
    assert len(chunks[0].page_content) <= 100
    assert chunks[0].page_content.endswith(chunks[1].page_content[:20])


def test_split_documents_no_split():
    """
    Valida que documentos menores que o chunk_size não são divididos.
    """
    short_doc = [Document(page_content="Texto curto.")]

    chunks = split_documents(short_doc, chunk_size=1000, chunk_overlap=200)

    assert len(chunks) == 1
    assert chunks[0].page_content == "Texto curto."
