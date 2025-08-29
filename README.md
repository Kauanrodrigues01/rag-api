# 📚 Portfolio RAG API

**Portfolio RAG API** é uma API moderna e assíncrona desenvolvida com **FastAPI**, projetada para integrar dados pessoais (como currículo, projetos e experiências) em um pipeline **RAG (Retrieval-Augmented Generation)** com LLMs, utilizando **LangChain**, **ChromaDB**, **OpenAI Embeddings** e **Jinja2** para gerenciamento via interface web.

Com esta API, desenvolvedores podem fazer upload de arquivos PDF contendo dados sobre si mesmos e permitir que usuários façam perguntas e obtenham respostas contextuais baseadas nesses dados.

---

## ✨ Funcionalidades

* ✅ Upload de documentos PDF com extração e divisão em *chunks*
* 🔍 Busca semântica via embeddings + ChromaDB
* 🤖 Integração com LLM (OpenAI GPT-3.5) para respostas contextuais via LangChain
* 🧠 Técnica de overlap nos chunks para manter o contexto
* 🗃️ Banco de dados relacional (PostgreSQL) com SQLAlchemy para gerenciar documentos
* 🚮 Deleção automática dos chunks ao excluir um documento
* 🔒 Proteção de rotas via API Key (`X-API-KEY`)
* 🌐 Interface web usando Jinja2 (HTML, CSS, JS) para gerenciar documentos
* ⚡ Uso de `BackgroundTasks` do FastAPI para paralelizar operações no vector store e melhorar performance (+70%)

---

## 🧠 Como funciona o RAG

1. **Upload de PDF**: O arquivo é carregado, processado, dividido em chunks e enviado para a vector store.
2. **Armazenamento**: Os chunks são salvos com identificadores únicos no ChromaDB e os metadados no PostgreSQL.
3. **Pergunta do usuário**: A pergunta é embutida como vetor e comparada com os chunks via LangChain.
4. **Respostas contextuais**: Os melhores chunks são combinados e enviados ao LLM, que retorna uma resposta rica em markdown.

---

## 🛠️ Tecnologias Utilizadas

As principais tecnologias utilizadas neste projeto incluem:

* **FastAPI**: Framework web assíncrono para construção da API.
* **LangChain**: Orquestração do pipeline RAG com LLM.
* **OpenAI**: Embeddings e modelo GPT-3.5 para geração de respostas.
* **ChromaDB**: Armazenamento vetorial para busca semântica.
* **SQLAlchemy Async + PostgreSQL**: Banco relacional para metadados dos documentos.
* **Jinja2**: Renderização de templates para a interface de administração.
* **Docker**: Empacotamento e deploy dos serviços.
* **Pytest**: Testes automatizados e cobertura.

---

## 🚀 Executando Localmente com Docker

### 🔧 Pré-requisitos

* Docker + Docker Compose
* OpenAI API Key

### 1. Crie seu `.env`

```env
OPENAI_API_KEY=sk-...
VECTOR_STORE_PATH=./chroma_db
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/dbname
API_KEY_SECRET=minha-chave-secreta
```

### 2. Suba os containers

```bash
docker compose up --build
```

### 🌐 Acesse:

* API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
* Painel Admin: [http://localhost:8000/admin](http://localhost:8000/admin)
* PGAdmin: [http://localhost:5050](http://localhost:5050)

---

## 📦 Endpoints Principais

| Método | Endpoint            | Protegido por API Key? | Descrição                                                       |
| ------ | ------------------- | ---------------------- | --------------------------------------------------------------- |
| POST   | `/documents`        | ✅                      | Faz upload de 1 ou mais PDFs e envia chunks para o vector store |
| GET    | `/documents`        | ✅                      | Lista os documentos salvos no banco                             |
| DELETE | `/documents/{id}`   | ✅                      | Deleta o documento e seus chunks na vector store                |
| POST   | `/rag/ask-question` | ❌                      | Faz uma pergunta com base nos documentos processados            |

**Para rotas protegidas, envie o header:**

```
X-API-KEY: <sua-chave>
```

---


## 🔒 Segurança

* Todas as rotas de CRUD de documentos são protegidas por API Key.
* `get_api_key()` verifica o header `X-API-KEY` com um segredo definido no `.env`.
* Rodando com usuário não privilegiado no Docker.
* Separação clara entre lógica de LLM e manipulação de arquivos.

---

## 📊 Métricas de Performance

* Utilização de `BackgroundTasks` reduziu o tempo de resposta do endpoint de upload de documentos em \~70%
* Arquitetura desacoplada com ChromaDB e LangChain
* Docker com multi-stage build e imagens otimizadas

---

## 💡 Motivação

Esse projeto nasceu da necessidade de fornecer respostas automáticas, seguras e contextualizadas para perguntas sobre o desenvolvedor (portfólio pessoal), transformando arquivos estáticos em dados consultáveis via IA generativa.

---

## 🧪 Futuras Melhorias

* 🔐 Suporte a autenticação OAuth2/JWT
* 🧠 Acompanhamento de perguntas e estatísticas
* 🌍 Deploy com HTTPS e CI/CD
* 🖼️ Suporte a outros tipos de arquivo além de PDF
* 📦 Plugin para integração com portfólios públicos
