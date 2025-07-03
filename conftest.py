import io
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from fpdf import FPDF
from langchain_core.documents import Document
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.main import app
from rag import vector_store as vector_store_module


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def dummy_documents():
    """Fixture que retorna uma lista de documentos LangChain simulados."""
    return [
        Document(page_content='Este é o primeiro documento.', metadata={'source': 'doc1'}),
        Document(page_content='Este é o segundo documento, um pouco mais longo para teste.', metadata={'source': 'doc2'}),
    ]


@pytest.fixture
def fake_pdf_upload_file():
    """
    Cria um UploadFile simulado com um conteúdo PDF gerado dinamicamente.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Conteúdo de teste do PDF.", ln=1, align='L')

    # output como string (dest='S') e depois converter para bytes
    pdf_content_str = pdf.output(dest='S')
    pdf_bytes = io.BytesIO(pdf_content_str.encode('latin1'))  # fpdf usa latin1
    pdf_bytes.seek(0)

    return StarletteUploadFile(filename="fake_test.pdf", file=pdf_bytes)


@pytest.fixture
def mock_retriever():
    """Fixture que simula um retriever com um método ainvoke."""
    retriever = MagicMock()
    retriever.ainvoke = AsyncMock(return_value='Resposta simulada da LLM.')
    return retriever


@pytest.fixture
def mock_vector_store(mock_retriever):
    """Fixture que simula a vector store com métodos async e as_retriever."""
    store = MagicMock()
    store.as_retriever.return_value = mock_retriever
    store.aadd_documents = AsyncMock(return_value=None)
    return store


@pytest.fixture(autouse=True)
def reset_vector_store_singleton():
    """
    Fixture que reseta o singleton da vector store antes e depois de cada teste.
    `autouse=True` garante que será executado para todos os testes.
    """
    # Antes do teste
    vector_store_module._global_instance_vector_store = None
    yield
    # Depois do teste
    vector_store_module._global_instance_vector_store = None
