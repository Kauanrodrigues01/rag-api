from fastapi import FastAPI, HTTPException, UploadFile, status

from rag.process import process_pdf

app = FastAPI()


@app.post('/upload-file')
def upload_file(file: UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='invalid file format'
        )

    chunks = process_pdf(file)

    return {'chunks': chunks}
