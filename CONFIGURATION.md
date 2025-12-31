# Guia de Configuração - RAG API

## 📋 Variáveis de Ambiente

Este documento descreve todas as variáveis de ambiente disponíveis para configurar a RAG API.

---

## 🔑 Configuração da API

### `API_KEY` (Obrigatório)
- **Descrição**: Chave secreta para autenticação das rotas protegidas
- **Tipo**: String
- **Exemplo**: `my-super-secret-api-key-2024`
- **Uso**: Enviar no header `X-API-Key` para acessar rotas protegidas

### `OPENAI_API_KEY` (Obrigatório)
- **Descrição**: Chave de API da OpenAI para embeddings e LLM
- **Tipo**: String
- **Formato**: Deve começar com `sk-`
- **Exemplo**: `sk-proj-xxxxxxxxxxxxxxxxxxxxx`
- **Onde obter**: https://platform.openai.com/api-keys

---

## 💾 Configuração do Banco de Dados

### `DATABASE_URL` (Obrigatório)
- **Descrição**: URL de conexão com o PostgreSQL
- **Tipo**: String (formato SQLAlchemy)
- **Exemplo Docker**: `postgresql+asyncpg://user:pass@db:5432/dbname`
- **Exemplo Local**: `postgresql+asyncpg://user:pass@localhost:5432/dbname`
- **Nota**: Use o driver `asyncpg` para suporte assíncrono

---

## 🗂️ Configuração do Vector Store

### `VECTOR_STORE_PATH`
- **Descrição**: Caminho para armazenar o banco de dados vetorial (ChromaDB)
- **Tipo**: String
- **Padrão**: `vector-db`
- **Exemplo**: `/app/vector-db` (Docker) ou `./chroma_db` (Local)

### `EMBEDDING_MODEL`
- **Descrição**: Modelo da OpenAI para gerar embeddings
- **Tipo**: String
- **Padrão**: `text-embedding-3-small`
- **Opções**:
  - `text-embedding-3-small` - Mais rápido e econômico
  - `text-embedding-3-large` - Melhor qualidade
  - `text-embedding-ada-002` - Modelo legado

---

## 🤖 Configuração do LLM

### `LLM_MODEL`
- **Descrição**: Modelo da OpenAI para geração de respostas
- **Tipo**: String
- **Padrão**: `gpt-3.5-turbo`
- **Opções**:
  - `gpt-3.5-turbo` - Rápido e econômico
  - `gpt-4` - Melhor qualidade
  - `gpt-4-turbo` - Equilíbrio entre qualidade e velocidade

### `LLM_TEMPERATURE`
- **Descrição**: Controla a criatividade das respostas (0 = determinístico, 2 = muito criativo)
- **Tipo**: Float
- **Padrão**: `0.7`
- **Intervalo**: `0.0` a `2.0`
- **Recomendação**: `0.3-0.5` para respostas factuais, `0.7-1.0` para respostas criativas

### `LLM_MAX_TOKENS`
- **Descrição**: Número máximo de tokens na resposta
- **Tipo**: Integer
- **Padrão**: `500`
- **Intervalo**: `1` a limite do modelo
- **Nota**: Mais tokens = respostas mais longas e custo maior

---

## 📄 Configuração de Processamento de Documentos

### `CHUNK_SIZE`
- **Descrição**: Tamanho de cada chunk de texto (em caracteres)
- **Tipo**: Integer
- **Padrão**: `1000`
- **Recomendação**: `500-2000` dependendo do tipo de documento
- **Nota**: Chunks maiores = mais contexto, mas menos precisão na busca

### `CHUNK_OVERLAP`
- **Descrição**: Sobreposição entre chunks consecutivos (em caracteres)
- **Tipo**: Integer
- **Padrão**: `200`
- **Intervalo**: Deve ser menor que `CHUNK_SIZE`
- **Recomendação**: `10-20%` do `CHUNK_SIZE`
- **Nota**: Overlap ajuda a manter contexto entre chunks

### `MAX_FILE_SIZE_MB`
- **Descrição**: Tamanho máximo permitido para upload de arquivos PDF
- **Tipo**: Integer
- **Padrão**: `10`
- **Unidade**: Megabytes (MB)
- **Recomendação**: `5-50` dependendo dos recursos disponíveis

---

## 🌐 Configuração CORS

### `CORS_ORIGINS`
- **Descrição**: Origens permitidas para requisições CORS
- **Tipo**: String (separado por vírgulas) ou Lista
- **Padrão**: `*` (todas as origens)
- **Exemplo Desenvolvimento**: `*`
- **Exemplo Produção**: `https://meusite.com,https://app.meusite.com`
- **⚠️ IMPORTANTE**: Use origens específicas em produção por segurança

### `CORS_ALLOW_CREDENTIALS`
- **Descrição**: Permite envio de cookies e credenciais
- **Tipo**: Boolean
- **Padrão**: `true`
- **Opções**: `true` ou `false`

### `CORS_ALLOW_METHODS`
- **Descrição**: Métodos HTTP permitidos
- **Tipo**: String (separado por vírgulas)
- **Padrão**: `*` (todos os métodos)
- **Exemplo**: `GET,POST,DELETE`

### `CORS_ALLOW_HEADERS`
- **Descrição**: Headers HTTP permitidos
- **Tipo**: String (separado por vírgulas)
- **Padrão**: `*` (todos os headers)
- **Exemplo**: `Content-Type,Authorization,X-API-Key`

---

## 📱 Configuração da Aplicação

### `APP_NAME`
- **Descrição**: Nome da aplicação (aparece na documentação)
- **Tipo**: String
- **Padrão**: `RAG API`

### `APP_VERSION`
- **Descrição**: Versão da aplicação
- **Tipo**: String
- **Padrão**: `1.0.0`
- **Formato**: Semantic Versioning (MAJOR.MINOR.PATCH)

### `DEBUG`
- **Descrição**: Ativa modo de debug com logs detalhados
- **Tipo**: Boolean
- **Padrão**: `false`
- **⚠️ ATENÇÃO**: Nunca use `true` em produção

---

## 🏥 Configuração de Health Check

### `HEALTH_CHECK_TIMEOUT`
- **Descrição**: Timeout em segundos para health checks
- **Tipo**: Integer
- **Padrão**: `5`
- **Intervalo**: Deve ser maior que `0`
- **Nota**: Tempo máximo para verificar todos os componentes

---

## 📝 Exemplos de Configuração

### Desenvolvimento Local
```env
API_KEY=dev-api-key-local
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/rag_dev
VECTOR_STORE_PATH=./vector-db
DEBUG=true
CORS_ORIGINS=*
```

### Produção
```env
API_KEY=prod-secure-random-key-here
OPENAI_API_KEY=sk-your-production-key
DATABASE_URL=postgresql+asyncpg://user:pass@db.production.com:5432/rag_prod
VECTOR_STORE_PATH=/app/vector-db
LLM_MODEL=gpt-4-turbo
LLM_TEMPERATURE=0.3
MAX_FILE_SIZE_MB=50
DEBUG=false
CORS_ORIGINS=https://myapp.com,https://api.myapp.com
CORS_ALLOW_METHODS=GET,POST,DELETE
```

### Otimização de Custos
```env
# Usa modelos mais econômicos
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-3.5-turbo
LLM_MAX_TOKENS=300
LLM_TEMPERATURE=0.3

# Chunks menores para menos tokens no contexto
CHUNK_SIZE=800
CHUNK_OVERLAP=150
```

### Alta Qualidade
```env
# Usa modelos de melhor qualidade
EMBEDDING_MODEL=text-embedding-3-large
LLM_MODEL=gpt-4-turbo
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.5

# Chunks maiores para mais contexto
CHUNK_SIZE=1500
CHUNK_OVERLAP=300
```

---

## 🔍 Health Check Endpoints

### `GET /health`
Retorna status simples da aplicação:
```json
{
  "status": "ok"
}
```

### `GET /health/detailed`
Retorna status detalhado de todos os componentes:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-31T10:30:00",
  "total_check_time_seconds": 0.245,
  "application": {
    "name": "RAG API",
    "version": "1.0.0",
    "debug_mode": false
  },
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_seconds": 0.012,
      "message": "Database connection is working"
    },
    "vector_store": {
      "status": "healthy",
      "response_time_seconds": 0.089,
      "documents_count": 1523,
      "path": "/app/vector-db",
      "message": "Vector store is accessible"
    },
    "openai": {
      "status": "healthy",
      "model": "gpt-3.5-turbo",
      "embedding_model": "text-embedding-3-small",
      "message": "OpenAI configuration is valid"
    }
  }
}
```

---

## 🚨 Validações e Restrições

1. **CHUNK_OVERLAP** deve ser menor que **CHUNK_SIZE**
2. **OPENAI_API_KEY** deve começar com `sk-`
3. **LLM_TEMPERATURE** deve estar entre 0.0 e 2.0
4. **MAX_FILE_SIZE_MB** deve ser maior que 0
5. **HEALTH_CHECK_TIMEOUT** deve ser maior que 0

---

## 💡 Dicas de Configuração

1. **Em desenvolvimento**: Use `DEBUG=true` e `CORS_ORIGINS=*`
2. **Em produção**: Sempre defina origens CORS específicas
3. **Para economia**: Use `gpt-3.5-turbo` e chunks menores
4. **Para qualidade**: Use `gpt-4` e chunks maiores
5. **Para documentos técnicos**: Use `CHUNK_SIZE=1500` e `CHUNK_OVERLAP=300`
6. **Para perguntas simples**: Use `LLM_TEMPERATURE=0.3`
7. **Para respostas criativas**: Use `LLM_TEMPERATURE=0.8`

---

## 📚 Recursos Adicionais

- [Documentação OpenAI](https://platform.openai.com/docs)
- [Documentação LangChain](https://python.langchain.com/docs/get_started/introduction)
- [Documentação ChromaDB](https://docs.trychroma.com/)
- [Documentação FastAPI](https://fastapi.tiangolo.com/)
