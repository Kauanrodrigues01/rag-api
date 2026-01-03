from typing import List, Set

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.settings import settings
from rag.schemas import Source
from rag.vector_store import get_vector_store

llm = ChatOpenAI(
    model=settings.LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    max_tokens=settings.LLM_MAX_TOKENS,
    api_key=settings.OPENAI_API_KEY,
)

system_prompt = """
Você é um assistente especializado em responder perguntas com base em documentos fornecidos.

## INSTRUÇÕES IMPORTANTES:

1. **Baseie-se APENAS no contexto fornecido** - Não invente informações ou use conhecimento externo.

2. **Se não souber a resposta** - Seja honesto e diga "Não encontrei informações suficientes nos documentos para responder essa pergunta."

3. **Seja específico e direto** - Responda de forma clara e objetiva, indo direto ao ponto.

4. **Use formatação Markdown** para melhor legibilidade:
   - Use **negrito** para destacar pontos importantes
   - Use listas quando apropriado
   - Use código inline com `backticks` para termos técnicos
   - Use > para citações diretas dos documentos

5. **Estruture respostas longas** com:
   - Resumo inicial (se necessário)
   - Desenvolvimento com detalhes
   - Conclusão ou próximos passos (se aplicável)

6. **Para perguntas comparativas** - Organize a informação em tabelas ou listas comparativas

7. **Mantenha o tom profissional** mas acessível e amigável

## CONTEXTO DOS DOCUMENTOS:
{context}

## IMPORTANTE:
- NÃO mencione fontes ou arquivos na resposta
- NÃO mencione nível de confiança na resposta
- Responda apenas com o conteúdo solicitado
- Se a pergunta for ambígua, peça esclarecimentos
- Se houver múltiplas interpretações, apresente todas
"""

prompt = ChatPromptTemplate.from_messages([
    ('system', system_prompt),
    ('human', '{input}'),
])

combine_docs_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)


async def ask_question(question: str):
    """Processa uma pergunta e retorna resposta com fontes."""
    retriever = get_vector_store().as_retriever(
        search_kwargs={
            'k': 5  # Retorna top 5 documentos mais relevantes
        }
    )

    retrieval_chain = create_retrieval_chain(
        retriever=retriever, combine_docs_chain=combine_docs_chain
    )

    response = await retrieval_chain.ainvoke({'input': question})

    # Extrai fontes dos documentos utilizados
    sources = _extract_sources(response.get('context', []))

    # Extrai nível de confiança da resposta (se mencionado)
    answer = response.get('answer', '')
    confidence = _extract_confidence(answer)

    return {'answer': answer, 'sources': sources, 'confidence': confidence}


def _extract_sources(documents: List) -> List[Source]:
    """Extrai informações únicas de fonte dos documentos."""
    sources_set: Set[tuple] = set()
    sources_list: List[Source] = []

    for doc in documents:
        metadata = doc.metadata if hasattr(doc, 'metadata') else {}
        filename = metadata.get('source', 'Desconhecido')
        page = metadata.get('page')

        # Evita duplicatas
        source_tuple = (filename, page)
        if source_tuple not in sources_set:
            sources_set.add(source_tuple)
            sources_list.append(Source(filename=filename, page=page))

    return sources_list


def _extract_confidence(answer: str) -> str:
    """Tenta extrair o nível de confiança mencionado na resposta."""
    answer_lower = answer.lower()

    if 'confiança: alta' in answer_lower or 'alta confiança' in answer_lower:
        return 'Alta'
    elif (
        'confiança: média' in answer_lower or 'média confiança' in answer_lower
    ):
        return 'Média'
    elif (
        'confiança: baixa' in answer_lower or 'baixa confiança' in answer_lower
    ):
        return 'Baixa'

    # Se não encontrou menção explícita, retorna None
    return None
