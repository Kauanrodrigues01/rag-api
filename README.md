# 🧠 KnowMe RAG - Sistema de Respostas Inteligentes sobre Você

<p align="center">
  <img src="URL_DA_IMAGEM_1" alt="Screenshot 1" width="700"/>
</p>

<p align="center">
  <img src="URL_DA_IMAGEM_2" alt="Screenshot 2" width="700"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain"/>
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/ChromaDB-FF6B6B?style=for-the-badge&logo=databricks&logoColor=white" alt="ChromaDB"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/Uvicorn-009688?style=for-the-badge&logo=gunicorn&logoColor=white" alt="Uvicorn"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/>
  <img src="https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest"/>
</p>

---

## 📋 Sobre o Projeto

**KnowMe RAG** é uma API moderna e assíncrona desenvolvida com **FastAPI**, projetada para integrar dados pessoais (como currículo, projetos e experiências) em um pipeline **RAG (Retrieval-Augmented Generation)** com LLMs, utilizando **LangChain**, **ChromaDB**, **OpenAI Embeddings** e **Jinja2** para gerenciamento via interface web.

Com o **KnowMe RAG**, desenvolvedores podem fazer upload de arquivos PDF contendo dados sobre si mesmos e permitir que usuários façam perguntas e obtenham respostas contextuais baseadas nesses dados, como se estivessem conversando diretamente com você.

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
* **Uvicorn**: Servidor ASGI de alta performance.

---

## 🚀 Executando Localmente com Docker

### 🔧 Pré-requisitos

* Docker + Docker Compose
* OpenAI API Key

### 1. Crie seu `.env`

Copie o arquivo `.env.example` e configure suas variáveis:

```bash
cp .env.example .env
```

Configure pelo menos as variáveis obrigatórias:

```env
# Obrigatórias
API_KEY=your-secret-api-key-here
OPENAI_API_KEY=sk-your-openai-api-key-here
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/dbname

# Opcionais (com valores padrão)
VECTOR_STORE_PATH=./chroma_db
LLM_MODEL=gpt-3.5-turbo
CHUNK_SIZE=1000
MAX_FILE_SIZE_MB=10
```

📖 **Para documentação completa de todas as variáveis de ambiente, veja [CONFIGURATION.md](./CONFIGURATION.md)**

### 2. Suba os containers

```bash
docker compose up --build
```

### 🌐 Acesse:

* API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
* Health Check Simples: [http://localhost:8000/health](http://localhost:8000/health)
* Health Check Detalhado: [http://localhost:8000/health/detailed](http://localhost:8000/health/detailed)
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
* Validação de tamanho máximo de arquivo (configurável via `MAX_FILE_SIZE_MB`).
* CORS configurável para ambientes de desenvolvimento e produção.
* Rodando com usuário não privilegiado no Docker.
* Separação clara entre lógica de LLM e manipulação de arquivos.
* Health checks detalhados para monitoramento de todos os componentes.

---

## ⚙️ Configurações Avançadas

O projeto oferece ampla configurabilidade via variáveis de ambiente:

* **LLM**: Escolha o modelo (GPT-3.5/GPT-4), temperatura e tokens máximos
* **Embeddings**: Configure o modelo de embeddings da OpenAI
* **Chunking**: Ajuste tamanho e overlap dos chunks
* **CORS**: Configure origens permitidas para produção
* **Limites**: Defina tamanho máximo de arquivos
* **Health Checks**: Configure timeout dos health checks

📖 **Veja a [documentação completa de configuração](./CONFIGURATION.md) para todos os detalhes**

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

---

## 👨‍💻 Autor

**Kauan Rodrigues Lima**

* GitHub: [Kauanrodrigues01](https://github.com/Kauanrodrigues01)
* LinkedIn: [Kauan Rodrigues](https://www.linkedin.com/in/kauan-rodrigues-lima/)
