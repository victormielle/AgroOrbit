# 🌾 AgroOrbit AI — Assistente IA com RAG na AWS

> Trabalho Final de Semestre — FIAP Global Solution | 1º Semestre 2026 | Prof. Itamar

Um assistente de IA que responde perguntas com base em documentos, usando RAG (Retrieval-Augmented Generation) com infraestrutura completa na AWS.

---

## Demo

Veja o agente em funcionamento — upload de documento e chat com RAG:
Link: https://youtu.be/Z2xl7VjRZSo

## Integrantes

| Nome | RM |
|------|----|
| Luiz Henrique de Paiva Alves Pinto | 572177 |
| Victor Hugo Mielle Bernardes da Silva | 571138 |

---

## Arquitetura

```
Usuário → S3 Frontend → EC2 (Flask + LLM) → RDS PostgreSQL (pgvector)
                                ↑
CSV → S3 incoming/ → Lambda fn-s3-to-pgvector → RDS → CloudWatch
```

### Componentes AWS

| Serviço | Função |
|---------|--------|
| **EC2 (t3.medium)** | API Flask + LLM SmolLM2-360M rodando em CPU |
| **RDS PostgreSQL** | Banco vetorial com extensão pgvector 0.8.1 |
| **S3** | Frontend AgroOrbit AI + ingestão de CSV via incoming/ |
| **Lambda** | fn-s3-to-pgvector — ingestão automatizada de CSV |
| **CloudWatch** | Logs de execução da Lambda |

---

##  Como Rodar

### Pré-requisitos
- Conta AWS com EC2, RDS e S3 configurados
- Python 3.12+
- PostgreSQL com extensão pgvector instalada

### 1. Clonar o repositório
```bash
git clone https://github.com/victormielle/AgroOrbit.git
cd AgroOrbit/GS-Agro-Orbit/back
```

### 2. Criar ambiente virtual e instalar dependências
```bash
python3 -m venv venv
source venv/bin/activate
TMPDIR=~/tmp pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.sample .env
nano .env
```

Preencha com os dados do seu RDS:
```
DB_HOST=seu-endpoint.rds.amazonaws.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=sua_senha
```

### 4. Instalar pgvector no banco
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5. Subir a API
```bash
sudo swapon /swapfile
TMPDIR=~/tmp gunicorn main:app -w 1 -b 0.0.0.0:8000 --timeout 300 --preload
```

### 6. Testar
```bash
curl http://localhost:8000/api/data
# Retorno esperado: {"message": "Hello, World!"}
```

---

##  Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/data` | Health check |
| POST | `/upload` | Upload de PDF/TXT — chunking + embeddings |
| GET | `/documents` | Lista documentos indexados |
| POST | `/ask` | Busca semântica em documento específico |
| POST | `/ask_all` | Busca semântica em todos os documentos |
| POST | `/chat` | **Agente** — RAG + LLM gera resposta |

---

##  Stack Tecnológica

- **Python + Flask** — API web
- **Gunicorn** — WSGI server para produção
- **SmolLM2-360M-Instruct** — LLM local rodando em CPU
- **sentence-transformers (all-MiniLM-L6-v2)** — Embeddings vetoriais 384 dims
- **PostgreSQL + pgvector** — Banco vetorial com busca por similaridade
- **pg8000** — Conexão Python ao PostgreSQL na Lambda
- **AWS EC2, RDS, S3, Lambda, CloudWatch** — Infraestrutura na nuvem

---

##  Problemas Conhecidos e Soluções

| Problema | Causa | Solução |
|----------|-------|---------|
| Worker Timeout no startup | Modelo demora ~60s para carregar | `--timeout 300 --preload` no Gunicorn |
| LLM Killed por falta de memória | RAM insuficiente | Swap de 4GB + instância t3.medium |
| Disco cheio durante instalação | PyTorch é pesado (~192MB) | `TMPDIR=~/tmp pip install` |
| pgvector não encontrado | Extensão não instalada no banco | `CREATE EXTENSION IF NOT EXISTS vector` |

---

##  Estrutura do Projeto

```
AgroOrbit/
├── GS-Agro-Orbit/
│   ├── back/
│   │   ├── main.py          # API Flask + RAG + LLM
│   │   ├── requirements.txt # Dependências Python
│   │   ├── Dockerfile       # Container da API
│   │   └── .env.sample      # Template de variáveis
│   └── front/
│       └── index.html       # Interface AgroOrbit AI
└── README.md
```

---

##  Licença

Projeto acadêmico — FIAP Global Solution 2026.
