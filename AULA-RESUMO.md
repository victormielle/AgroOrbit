# Aula Prática — Deploy de API RAG com Flask + Azure Container Apps

## O que foi construído

Uma API de **Retrieval-Augmented Generation (RAG)** em Python/Flask que:
- Recebe upload de documentos (PDF ou texto)
- Divide em chunks e gera embeddings vetoriais com `sentence-transformers`
- Armazena no PostgreSQL com extensão `pgvector`
- Responde perguntas em linguagem natural buscando os trechos mais relevantes por similaridade vetorial

---

## Stack Utilizada

| Camada | Tecnologia |
|--------|-----------|
| API | Python + Flask |
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2) |
| Banco de dados | PostgreSQL + pgvector (AWS RDS) |
| Servidor WSGI | Gunicorn |
| Container | Docker |
| Registry | Azure Container Registry (ACR) |
| Deploy | Azure Container Apps |
| CI/CD | GitHub Actions |

---

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/data` | Health check |
| POST | `/upload` | Upload de PDF/texto, indexa em chunks |
| GET | `/documents` | Lista documentos indexados |
| POST | `/ask` | Busca semântica em documento específico |
| POST | `/ask_all` | Busca semântica em todos os documentos |

### Parâmetros opcionais

**`/upload`** — `chunk_size` (form-data, default: 500 chars)
```bash
curl -X POST https://<url>/upload \
  -F "file=@constituicao.pdf" \
  -F "chunk_size=800"
```

**`/ask`** — `top_k` (default: 3 chunks retornados)
```bash
curl -X POST https://<url>/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "direitos fundamentais", "doc_id": 1, "top_k": 5}'
```

**`/ask_all`** — `top_k` (default: 3)
```bash
curl -X POST https://<url>/ask_all \
  -H "Content-Type: application/json" \
  -d '{"question": "educação", "top_k": 10}'
```

---

## Arquitetura RAG

```
PDF/Texto
    │
    ▼
Extração de texto (PyPDF2)
    │
    ▼
Chunking (500 chars, overlap 50)
    │
    ▼
Embedding (all-MiniLM-L6-v2 → vetor 384 dims)
    │
    ▼
PostgreSQL + pgvector
    │
    ▼
Busca por similaridade coseno (<-> operator)
    │
    ▼
Top-K chunks mais relevantes
```

---

## Pipeline CI/CD — GitHub Actions

O workflow `.github/workflows/deploy.yml` é disparado a cada push na branch `deploy` e executa:

1. **Login** no Azure via Service Principal
2. **Build** da imagem Docker
3. **Push** para o Azure Container Registry (`assistenteia.azurecr.io`)
4. **Cria** o Container Apps Environment (se não existir)
5. **Deploy** no Azure Container Apps com variáveis de ambiente
6. **Imprime** a URL pública no log

```
push → branch deploy
    │
    ▼
GitHub Actions
    ├── az login (Service Principal)
    ├── docker build + push → ACR
    └── az containerapp create/update → URL pública
```

---

## Problemas encontrados e soluções

### 1. `gunicorn: executable file not found`
**Causa:** `gunicorn` não estava no `requirements.txt`  
**Solução:** Adicionar `gunicorn==21.2.0` ao `requirements.txt`

### 2. Worker Timeout no startup
**Causa:** O modelo `SentenceTransformer` demora ~60s para carregar, excedendo o timeout padrão do gunicorn (30s)  
**Solução:** `--timeout 120 --preload` no CMD do Dockerfile  
```dockerfile
CMD ["gunicorn", "main:app", "-w", "2", "-b", "0.0.0.0:8000", "--timeout", "120", "--preload"]
```

### 3. RAG sempre retornava o mesmo chunk (capa do documento)
**Causa:** O upload indexava o documento inteiro como **um único registro** no banco  
**Solução:** Implementar chunking — dividir o texto em pedaços de 500 chars antes de indexar

```python
def split_chunks(text, size=500, overlap=50):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size].strip())
        start += size - overlap
    return [c for c in chunks if c]
```

---

## Conceitos-chave aprendidos

**Embeddings vetoriais**  
Representação numérica do significado semântico de um texto. Textos com significado similar ficam próximos no espaço vetorial.

**pgvector**  
Extensão do PostgreSQL que permite armazenar vetores e fazer buscas por similaridade com o operador `<->` (distância L2).

**Chunking**  
Dividir documentos longos em pedaços menores antes de indexar. Essencial para RAG — sem chunking, o embedding representa o documento inteiro e a busca perde precisão.

**RAG (Retrieval-Augmented Generation)**  
Técnica que combina busca semântica com geração de texto:
1. Indexa documentos em chunks com embeddings
2. Na pergunta, busca os chunks mais relevantes
3. Usa esses chunks como contexto para gerar a resposta

**Azure Container Apps**  
Serviço serverless para rodar containers sem gerenciar infraestrutura. Escala automaticamente de 0 a N réplicas.

---

## Repositório

[https://github.com/arquitetoitamar/aula-2-api](https://github.com/arquitetoitamar/aula-2-api) — branch `deploy`

---

## Para rodar localmente

```bash
git clone https://github.com/arquitetoitamar/aula-2-api
cd aula-2-api/back
cp .env.sample .env
# edite o .env com suas credenciais do banco
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

API disponível em `http://localhost:3000`
