from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from documents.routes import router as documents_router
from rag.routes import router as rag_router

app = FastAPI(title='RAG API')
app.mount(
    '/static',
    StaticFiles(directory='app/static'),
    name='static'
)

templates = Jinja2Templates(directory='app/templates')

app.include_router(documents_router, prefix='/api')
app.include_router(rag_router, prefix='/api')


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse('dashboard.html', {'request': request, 'title': 'Home Page'})