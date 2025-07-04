import io
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fpdf import FPDF
from httpx import ASGITransport, AsyncClient
from langchain_core.documents import Document
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.database import get_async_session, table_registry
from app.main import app
from app.settings import settings
from app.utils.db import (
    create_test_database,
    drop_test_database,
    generate_test_db_name,
    get_test_db_url,
)
from rag import vector_store as vector_store_module

TEST_DB_NAME = generate_test_db_name()
TEST_DB_URL = get_test_db_url(settings.DATABASE_URL, TEST_DB_NAME)


@pytest.fixture(scope='session')
def test_db():
    # Funções sincronas para criar e deletar base de dados
    create_test_database(settings.DATABASE_URL, TEST_DB_NAME)
    yield
    drop_test_database(settings.DATABASE_URL, TEST_DB_NAME)


@pytest_asyncio.fixture(scope='function')
async def engine(test_db):
    engine = create_async_engine(TEST_DB_URL)
    yield engine


@pytest_asyncio.fixture(scope='function')
async def session(engine):
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def client(session):
    async def override_get_async_session():
        yield session

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testserver') as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def api_key():
    return settings.API_KEY

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
