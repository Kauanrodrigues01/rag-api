from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from documents.routes import router as documents_router
from rag.routes import router as rag_router

app = FastAPI(title='RAG API')

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (para desenvolvimento)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os headers
)
app.mount(
    '/static',
    StaticFiles(directory='app/static'),
    name='static'
)

templates = Jinja2Templates(directory='app/templates')


app.include_router(documents_router, prefix='/api')
app.include_router(rag_router, prefix='/api')

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse('dashboard.html', {'request': request, 'title': 'Home Page'})