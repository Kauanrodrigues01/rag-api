import os
import tempfile
from typing import List

from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from rag.splitter import split_documents


async def process_pdf(file: UploadFile, filename: str) -> List[Document]:
    temp_file_path = None

    try:
        content = await file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        loader = PyPDFLoader(file_path=temp_file_path)
        docs = loader.load()

        # Atualiza o campo 'source' de todos os documentos
        for doc in docs:
            doc.metadata["source"] = filename

        return split_documents(docs=docs)

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)