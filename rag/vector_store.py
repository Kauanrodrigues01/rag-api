from typing import List

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from app.settings import settings

_global_instance_vector_store = None


def get_vector_store():
    global _global_instance_vector_store

    if _global_instance_vector_store:
        print('Usou a instancia')
        return _global_instance_vector_store

    try:
        print('Criou uma nova')
        _global_instance_vector_store = Chroma(
            persist_directory=settings.VECTOR_STORE_PATH,
            embedding_function=OpenAIEmbeddings(
                model='text-embedding-3-small'
            )
        )
        return _global_instance_vector_store
    except Exception as e:
        print(f'Error retrieving Vector Store: {e}')
        return None


async def add_chunks_to_vector_store(chunks: List[Document]):
    vector_store = get_vector_store()
    await vector_store.aadd_documents(documents=chunks)
    return vector_store
