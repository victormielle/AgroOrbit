# Trabalho Prático — Deploy de Plataforma Cognitiva na AWS

## Objetivo

Realizar o deploy completo de uma API de **RAG (Retrieval-Augmented Generation)** com LLM local na AWS, utilizando EC2 + RDS PostgreSQL com pgvector.

A aplicação permite:
- Upload de documentos (PDF/texto)
- Busca semântica por similaridade vetorial
- Chat com IA usando RAG (busca contextual + geração com LLM local)

---

## Arquitetura

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────────────┐
│  Frontend   │──────▶│  EC2 t3.medium   │──────▶│  RDS PostgreSQL 15  │
│  (S3 / PC)  │ HTTP  │  Flask API :5000 │  TCP  │  + pgvector         │
└─────────────┘       └──────────────────┘       └─────────────────────┘
                              │
                      ┌───────┴───────┐
                      │ Modelos IA    │
                      │ - Embeddings  │
                      │ - LLM local   │
                      └───────────────┘
```

---

## Passo a Passo

### 1. Criar Security Groups

#### Security Group da EC2 (`aula2-ec2-sg`)

| Porta | Protocolo | Origem | Descrição |
|-------|-----------|--------|-----------|
| 22 | TCP | 0.0.0.0/0 | SSH |
| 80 | TCP | 0.0.0.0/0 | HTTP |
| 5000 | TCP | 0.0.0.0/0 | Flask API |

#### Security Group do RDS (`aula2-rds-sg`)

| Porta | Protocolo | Origem | Descrição |
|-------|-----------|--------|-----------|
| 5432 | TCP | aula2-ec2-sg | PostgreSQL (apenas da EC2) |

---

### 2. Criar RDS PostgreSQL

No console AWS → RDS → Create Database:

| Configuração | Valor |
|-------------|-------|
| Engine | PostgreSQL 15 |
| Template | Free tier / Dev/Test |
| DB Instance Class | db.t3.micro |
| DB Instance Identifier | `aula2-postgres` |
| Master Username | `postgres` |
| Master Password | (escolha uma senha segura) |
| DB Name | `aula2db` |
| Storage | 20 GB gp2 |
| VPC Security Group | `aula2-rds-sg` |
| Public Access | No |

> ⏳ A criação leva ~5-10 minutos. Anote o **Endpoint** quando estiver disponível.

---

### 3. Criar Key Pair

No console AWS → EC2 → Key Pairs → Create Key Pair:

- **Name**: `aula2-key`
- **Type**: RSA
- **Format**: .pem

> ⚠️ Baixe e guarde o arquivo `.pem` — ele não pode ser baixado novamente!

No terminal, ajuste as permissões:
```bash
chmod 400 aula2-key.pem
```

---

### 4. Criar EC2 t3.medium

No console AWS → EC2 → Launch Instance:

| Configuração | Valor |
|-------------|-------|
| Name | `aula2-api-server` |
| AMI | Ubuntu Server 22.04 LTS |
| Instance Type | **t3.medium** (2 vCPU, 4GB RAM) |
| Key Pair | `aula2-key` |
| Security Group | `aula2-ec2-sg` |
| Storage | 30 GB gp3 |

> ⚠️ Usamos t3.medium porque o modelo LLM precisa de ~2GB de RAM para carregar.

---

### 5. Conectar na EC2 via SSH

```bash
ssh -i "aula2-key.pem" ubuntu@<IP_PUBLICO_DA_EC2>
```

---

### 6. Instalar Python 3.11

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y software-properties-common git postgresql-client
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

---

### 7. Clonar o Repositório

```bash
mkdir -p /home/ubuntu/aula2_api
cd /home/ubuntu/aula2_api
git clone https://github.com/arquitetoitamar/aula-2-api.git .
cd back
```

---

### 8. Habilitar pgvector no RDS

```bash
PGPASSWORD='<SENHA_RDS>' psql -h <ENDPOINT_RDS> -U postgres -d aula2db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Exemplo:
```bash
PGPASSWORD='Postgres123!' psql -h aula2-postgres.cjrzofqq7bys.us-east-1.rds.amazonaws.com -U postgres -d aula2db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

---

### 9. Configurar Variáveis de Ambiente

```bash
cat > .env << EOF
DB_HOST=<ENDPOINT_RDS>
DB_PORT=5432
DB_NAME=aula2db
DB_USER=postgres
DB_PASSWORD=<SENHA_RDS>
SQLALCHEMY_TRACK_MODIFICATIONS=False
EOF
```

---

### 10. Criar Ambiente Virtual e Instalar Dependências

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

> ⏳ A instalação do PyTorch e SentenceTransformers pode levar ~5 minutos.

---

### 11. Alterar a Porta para 5000

Edite o arquivo `main.py` e altere a última linha:

```bash
sed -i 's/port=3000/port=5000/' main.py
```

---

### 12. Testar Manualmente

```bash
python main.py
```

Deve aparecer:
```
Carregando LLM: HuggingFaceTB/SmolLM2-360M-Instruct...
LLM carregado!
 * Running on http://0.0.0.0:5000
```

Teste de outro terminal ou navegador: `http://<IP_EC2>:5000/api/data`

Pare com `Ctrl+C` após confirmar que funciona.

---

### 13. Criar Serviço Systemd (rodar permanentemente)

```bash
sudo tee /etc/systemd/system/aula2api.service << EOF
[Unit]
Description=Aula2 Flask API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/aula2_api/back
Environment="PATH=/home/ubuntu/aula2_api/back/venv/bin"
ExecStart=/home/ubuntu/aula2_api/back/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable aula2api
sudo systemctl start aula2api
```

---

### 14. Verificar se está Rodando

```bash
# Status do serviço
sudo systemctl status aula2api

# Logs em tempo real
sudo journalctl -u aula2api -f

# Testar localmente
curl http://localhost:5000/api/data
```

---

## Endpoints da API

| Método | Rota | Descrição | Body |
|--------|------|-----------|------|
| GET | `/api/data` | Health check | — |
| POST | `/upload` | Upload de documento | `file` (multipart) |
| GET | `/documents` | Lista documentos | — |
| POST | `/ask` | Busca em documento específico | `{"question": "...", "doc_id": 1}` |
| POST | `/ask_all` | Busca em todos os documentos | `{"question": "..."}` |
| POST | `/chat` | Chat com RAG + LLM | `{"question": "..."}` |

### Exemplos de uso com curl

```bash
# Health check
curl http://<IP_EC2>:5000/api/data

# Upload de documento
curl -X POST http://<IP_EC2>:5000/upload -F "file=@documento.pdf"

# Listar documentos
curl http://<IP_EC2>:5000/documents

# Busca semântica em todos
curl -X POST http://<IP_EC2>:5000/ask_all \
  -H "Content-Type: application/json" \
  -d '{"question": "o que é inteligência artificial?"}'

# Chat com RAG
curl -X POST http://<IP_EC2>:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "resuma o documento"}'
```

---

## Frontend

O arquivo `front/index.html` é um chat web que se conecta à API. Para usar:

1. Abra o arquivo no navegador
2. No campo **API URL** (canto inferior esquerdo), coloque: `http://<IP_EC2>:5000`
3. Faça upload de um documento
4. Converse com o agente IA

---

## Comandos Úteis

```bash
# Reiniciar API
sudo systemctl restart aula2api

# Ver logs
sudo journalctl -u aula2api -f

# Parar API
sudo systemctl stop aula2api

# Conectar no banco
PGPASSWORD='<SENHA>' psql -h <ENDPOINT_RDS> -U postgres -d aula2db

# Ver documentos no banco
SELECT id, filename FROM documents;

# Ver extensões instaladas
\dx
```

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| `type "vector" does not exist` | Execute `CREATE EXTENSION IF NOT EXISTS vector;` no RDS |
| API não inicia | Verifique `.env` com `cat .env` e logs com `journalctl -u aula2api` |
| Não conecta no RDS | Verifique se o SG do RDS permite a porta 5432 do SG da EC2 |
| Timeout no upload | Documentos grandes demoram para gerar embeddings — aguarde |
| Porta 5000 não acessível | Verifique se o SG da EC2 tem a porta 5000 aberta |
| `ModuleNotFoundError` | Ative o venv: `source /home/ubuntu/aula2_api/back/venv/bin/activate` |
| Memória insuficiente | t3.medium tem 4GB — se travar, reinicie: `sudo systemctl restart aula2api` |

---

## Conceitos-Chave

### RAG (Retrieval-Augmented Generation)
Técnica que combina busca semântica com geração de texto:
1. Documentos são divididos em chunks e convertidos em vetores (embeddings)
2. Na pergunta, busca os chunks mais similares por distância vetorial
3. Usa esses chunks como contexto para o LLM gerar a resposta

### Embeddings
Representação numérica do significado de um texto. Textos similares ficam próximos no espaço vetorial (384 dimensões).

### pgvector
Extensão do PostgreSQL para armazenar e buscar vetores. Operador `<->` calcula distância euclidiana.

### Chunking
Dividir documentos em pedaços menores (500 chars, overlap 50) antes de indexar. Sem chunking, a busca perde precisão.

---

## Entregáveis

1. ✅ EC2 t3.medium rodando a API na porta 5000
2. ✅ RDS PostgreSQL com pgvector habilitado
3. ✅ API respondendo em `http://<IP_EC2>:5000`
4. ✅ Upload de pelo menos 1 documento
5. ✅ Demonstração do chat funcionando com RAG
