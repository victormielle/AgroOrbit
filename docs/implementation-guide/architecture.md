# Arquitetura

![Diagrama da Arquitetura](arquitetura.png)

## Componentes

### Frontend (Amazon S3)
Site estático (HTML/CSS/JS) hospedado em bucket S3 com acesso público. Permite ao usuário fazer upload de documentos, realizar buscas e interagir com o chat.

### API Flask (Amazon EC2)
Instância EC2 t3.medium rodando a API REST em Python/Flask na porta 5000. Responsável por:

- Receber uploads e processar documentos (PDF/texto)
- Gerar embeddings com SentenceTransformers (all-MiniLM-L6-v2)
- Realizar busca vetorial por similaridade
- Gerar respostas com LLM local (SmolLM2-360M-Instruct) usando RAG

### Banco de Dados (Amazon RDS)
PostgreSQL 15 com extensão pgvector para armazenamento e busca de vetores de alta dimensão (384d).

## Fluxo de Dados

1. O usuário acessa o site estático hospedado no S3
2. O frontend faz requisições HTTP para a API Flask na EC2
3. A API gera embeddings dos textos usando SentenceTransformers
4. Os embeddings são armazenados/consultados no PostgreSQL via pgvector
5. Para o chat, a API busca contexto relevante (RAG) e gera resposta com o LLM local

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/data` | Health check |
| POST | `/upload` | Upload e indexação de documento (PDF/texto) |
| POST | `/ask` | Busca semântica em documento específico |
| POST | `/ask_all` | Busca semântica em todos os documentos |
| GET | `/documents` | Lista documentos indexados |
| POST | `/chat` | Chat com RAG (busca contextual + geração LLM) |
