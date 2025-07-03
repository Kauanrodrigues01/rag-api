from typing import List, Optional
from uuid import uuid4

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from app.settings import settings

_global_instance_vector_store: Optional[Chroma] = None


def get_vector_store():
    global _global_instance_vector_store

    if _global_instance_vector_store:
        return _global_instance_vector_store

    try:
        _global_instance_vector_store = Chroma(
            persist_directory=settings.VECTOR_STORE_PATH,
            embedding_function=OpenAIEmbeddings(
                model='text-embedding-3-small'
            )
        )
        return _global_instance_vector_store
    except Exception as e:
        print(f'Error retrieving Vector Store: {e}')
        raise Exception(e)


async def add_chunks_to_vector_store(chunks: List[Document], ids: List[str]):
    vector_store = get_vector_store()
    await vector_store.aadd_documents(documents=chunks, ids=ids)


async def delete_chunks_by_ids(ids: List[str]):
    vector_store = get_vector_store()
    await vector_store.adelete(ids=ids)


def generate_chunks_ids(filename: str, chunks: List[Document]) -> List[str]:
    chunk_ids = [f'{filename}_chunk_{i}_{uuid4()}' for i in range(len(chunks))]
    return chunk_ids
