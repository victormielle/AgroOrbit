# Deployment

Guia para deploy da API Flask em produção na AWS (EC2 Ubuntu + RDS PostgreSQL).

## Pré-requisitos

- Instância EC2 t3.medium (Ubuntu 22.04) com portas 22, 80 e 5000 abertas
- RDS PostgreSQL 15 com extensão pgvector habilitada
- Security Group do RDS permitindo conexão da EC2 na porta 5432

## 1. Preparar o Servidor

```bash
ssh -i "aula2-key.pem" ubuntu@<IP_PUBLICO_EC2>

sudo apt update && sudo apt upgrade -y
sudo apt install -y software-properties-common git
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

## 2. Clonar e Configurar o Projeto

```bash
mkdir -p /home/ubuntu/aula2_api
cd /home/ubuntu/aula2_api
git clone https://github.com/arquitetoitamar/aula-2-api.git .
cd back

python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configurar Variáveis de Ambiente

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

## 4. Habilitar pgvector no RDS

```bash
sudo apt install -y postgresql-client
psql -h <ENDPOINT_RDS> -U postgres -d aula2db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## 5. Criar Serviço Systemd

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

## 6. Verificar

```bash
# Status do serviço
sudo systemctl status aula2api

# Logs
sudo journalctl -u aula2api -f

# Testar API
curl http://localhost:5000/api/data
```

## Acesso Externo

A API estará disponível em:

```
http://<IP_PUBLICO_EC2>:5000
```

## Endpoints Disponíveis

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/data` | Health check |
| POST | `/upload` | Upload e indexação de documento |
| POST | `/ask` | Busca semântica em documento específico |
| POST | `/ask_all` | Busca semântica em todos os documentos |
| GET | `/documents` | Lista documentos indexados |
| POST | `/chat` | Chat com RAG (busca + LLM) |
