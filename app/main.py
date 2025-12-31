from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.settings import settings
from app.health import get_health_status
from documents.routes import router as documents_router
from rag.routes import router as rag_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Configure CORS with settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
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
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/health/detailed", tags=["Health"])
async def health_detailed():
    """Detailed health check with all system components."""
    return await get_health_status()


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse('dashboard.html', {'request': request, 'title': 'Home Page'})