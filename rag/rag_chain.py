from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from rag.vector_store import get_vector_store

llm = ChatOpenAI(model='gpt-3.5-turbo')

system_prompt = '''
Use o contexto para responder as perguntas.
Se não souber, diga que não há informações suficientes para responder a pergunta.
Responda em markdown com visualizações elaboradas.
Contexto: {context}
'''

prompt = ChatPromptTemplate.from_messages(
    [
        ('system', system_prompt),
        ('human', '{input}')
    ]
)

combine_docs_chain = create_stuff_documents_chain(
    llm=llm,
    prompt=prompt
)


async def ask_question(question: str):
    retriever = get_vector_store().as_retriever()

    retrieval_chain = create_retrieval_chain(
        retriever=retriever,
        combine_docs_chain=combine_docs_chain
    )

    response = await retrieval_chain.ainvoke({'input': question})
    return response.get('answer')
