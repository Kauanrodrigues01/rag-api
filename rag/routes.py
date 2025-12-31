from fastapi import APIRouter

from rag.rag_chain import ask_question as ask_question_rag

from .schemas import AskQuestionRequest, AskQuestionResponse

router = APIRouter(
    prefix='/rag',
    tags=['RAG']
)


@router.post('/ask-question', response_model=AskQuestionResponse)
async def ask_question(data: AskQuestionRequest):
    """
    Processa uma pergunta e retorna uma resposta gerada com base em documentos vetorizados.
    
    A resposta inclui:
    - **answer**: Resposta formatada em Markdown
    - **sources**: Lista de documentos/páginas utilizados como fonte
    - **confidence**: Nível de confiança da resposta (Alta/Média/Baixa)
    
    ## Exemplo de Requisição:
    ```json
    {
        "question": "Quais são as principais habilidades técnicas?"
    }
    ```
    
    ## Exemplo de Resposta:
    ```json
    {
        "answer": "**Principais habilidades técnicas:**\\n\\n1. Python\\n2. FastAPI\\n3. Machine Learning\\n\\n[Fonte: curriculo.pdf]\\n\\n**Confiança: Alta**",
        "sources": [
            {
                "filename": "curriculo.pdf",
                "page": 1
            }
        ],
        "confidence": "Alta"
    }
    ```
    """
    result = await ask_question_rag(data.question)
    return result
