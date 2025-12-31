import asyncio
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.settings import settings
from rag.vector_store import get_vector_store


async def check_database_health() -> Dict[str, Any]:
    """
    Verifica a saúde da conexão com o banco de dados PostgreSQL.
    """
    try:
        async with AsyncSessionLocal() as session:
            # Tenta executar uma query simples
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            
            # Verifica o tempo de resposta
            start_time = datetime.now()
            await session.execute(text("SELECT COUNT(*) FROM document_records"))
            response_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'status': 'healthy',
                'response_time_seconds': round(response_time, 3),
                'message': 'Database connection is working'
            }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'message': 'Database connection failed'
        }


async def check_vector_store_health() -> Dict[str, Any]:
    """
    Verifica a saúde do vector store (ChromaDB).
    """
    try:
        start_time = datetime.now()
        vector_store = get_vector_store()
        
        # Tenta obter informações do vector store
        collection = vector_store._collection
        count = collection.count()
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'status': 'healthy',
            'response_time_seconds': round(response_time, 3),
            'documents_count': count,
            'path': settings.VECTOR_STORE_PATH,
            'message': 'Vector store is accessible'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'message': 'Vector store connection failed'
        }


async def check_openai_health() -> Dict[str, Any]:
    """
    Verifica a configuração da API da OpenAI.
    """
    try:
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith('sk-your'):
            return {
                'status': 'unhealthy',
                'message': 'OpenAI API key not configured properly'
            }
        
        # Verifica se a chave tem o formato correto
        if not settings.OPENAI_API_KEY.startswith('sk-'):
            return {
                'status': 'unhealthy',
                'message': 'Invalid OpenAI API key format'
            }
        
        return {
            'status': 'healthy',
            'model': settings.LLM_MODEL,
            'embedding_model': settings.EMBEDDING_MODEL,
            'message': 'OpenAI configuration is valid'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'message': 'OpenAI configuration check failed'
        }


async def get_health_status() -> Dict[str, Any]:
    """
    Executa todos os health checks e retorna o status geral do sistema.
    """
    start_time = datetime.now()
    
    # Executa todos os checks em paralelo com timeout
    try:
        database_check, vector_store_check, openai_check = await asyncio.wait_for(
            asyncio.gather(
                check_database_health(),
                check_vector_store_health(),
                check_openai_health(),
                return_exceptions=True
            ),
            timeout=settings.HEALTH_CHECK_TIMEOUT
        )
    except asyncio.TimeoutError:
        return {
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': 'Health check timeout',
            'message': f'Health checks exceeded {settings.HEALTH_CHECK_TIMEOUT}s timeout'
        }
    
    # Trata exceções retornadas pelo gather
    if isinstance(database_check, Exception):
        database_check = {'status': 'unhealthy', 'error': str(database_check)}
    if isinstance(vector_store_check, Exception):
        vector_store_check = {'status': 'unhealthy', 'error': str(vector_store_check)}
    if isinstance(openai_check, Exception):
        openai_check = {'status': 'unhealthy', 'error': str(openai_check)}
    
    # Determina o status geral
    all_healthy = all([
        database_check.get('status') == 'healthy',
        vector_store_check.get('status') == 'healthy',
        openai_check.get('status') == 'healthy'
    ])
    
    total_time = (datetime.now() - start_time).total_seconds()
    
    return {
        'status': 'healthy' if all_healthy else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'total_check_time_seconds': round(total_time, 3),
        'application': {
            'name': settings.APP_NAME,
            'version': settings.APP_VERSION,
            'debug_mode': settings.DEBUG
        },
        'checks': {
            'database': database_check,
            'vector_store': vector_store_check,
            'openai': openai_check
        }
    }
