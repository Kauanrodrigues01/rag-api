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
    """
    answer = await ask_question_rag(data.question)
    return {'answer': answer}
