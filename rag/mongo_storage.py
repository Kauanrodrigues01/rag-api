from typing import List, Optional
from app.db.mongo import documents_collection


async def save_chunk_ids(filename: str, chunk_ids: List[str]):
    """
    Salva os chunk_ids associados a um arquivo PDF.
    Se o filename já existir, ele será sobrescrito.
    """
    await documents_collection.update_one(
        {'filename': filename},
        {'$set': {'chunk_ids': chunk_ids}},
        upsert=True
    )


async def get_all_filenames() -> List[str]:
    """
    Retorna uma lista com todos os filenames salvos no MongoDB.
    """
    cursor = documents_collection.find({}, {'_id': 0, 'filename': 1})
    return [doc['filename'] async for doc in cursor]


async def get_chunk_ids_by_filename(filename: str) -> Optional[List[str]]:
    """
    Retorna os chunk_ids associados ao nome do arquivo.
    """
    doc = await documents_collection.find_one({'filename': filename})
    if doc:
        return doc.get('chunk_ids', [])
    return None


async def delete_by_filename(filename: str):
    """
    Remove o registro do MongoDB pelo nome do arquivo.
    """
    await documents_collection.delete_one({'filename': filename})
