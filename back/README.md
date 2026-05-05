# Configuração do Ambiente no Ubuntu

Este guia explica como configurar o ambiente de produção para a aplicação Flask em um servidor Ubuntu (ex: EC2 com Ubuntu AMI).

## 1. Conectar ao Servidor

```bash
ssh -i "sua-chave.pem" ubuntu@seu-ip-servidor
```

## 2. Atualizar o Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

## 3. Instalar Python e Dependências

```bash
# Instalar dependências base
sudo apt install -y software-properties-common

# Adicionar repositório e instalar Python 3.11
sudo add-apt-repository ppa:deadsnakes/python3.11 -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-distutils

# Instalar pip
curl -O https://bootstrap.pypa.io/get-pip.py
python3.11 get-pip.py --user
```

## 4. Configurar o Projeto

```bash
# Criar diretório do projeto
mkdir -p /home/ubuntu/sompo_app
cd /home/ubuntu/sompo_app

# Clonar o repositório
git clone seu-repositorio.git .

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## 5. Configurar Gunicorn

```bash
# Instalar Gunicorn (já está no requirements.txt)
pip install gunicorn

# Testar Gunicorn
gunicorn --bind 0.0.0.0:8000 main:app
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

## 6. Configurar Supervisor (gerenciador de processos)

```bash
# Instalar Supervisor
sudo apt install -y supervisor
sudo systemctl start supervisor
sudo systemctl enable supervisor

# Criar arquivo de configuração
sudo nano /etc/supervisor/conf.d/sompo_app.conf
```

Conteúdo do arquivo `sompo_app.conf`:

```ini
[program:sompo_app]
directory=/home/ubuntu/sompo_app
command=/home/ubuntu/sompo_app/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 main:app
autostart=true
autorestart=true
stderr_logfile=/var/log/sompo_app/sompo_app.err.log
stdout_logfile=/var/log/sompo_app/sompo_app.out.log
user=ubuntu
environment=FLASK_ENV="production",FLASK_APP="main.py"
```

```bash
# Criar diretório para logs
sudo mkdir -p /var/log/sompo_app
sudo chown -R ubuntu:ubuntu /var/log/sompo_app

# Recarregar supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start sompo_app
```

## 7. Configurar Nginx como Proxy Reverso

```bash
# Instalar Nginx
sudo apt install -y nginx

# Configurar Nginx
sudo nano /etc/nginx/sites-available/sompo_app
```

Conteúdo do arquivo `sompo_app`:

```nginx
server {
    listen 80;
    server_name _;  # Substitua pelo seu domínio se houver

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Ativar o site
sudo ln -s /etc/nginx/sites-available/sompo_app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Testar configuração do Nginx
sudo nginx -t

# Iniciar e habilitar Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 8. Configurar o Firewall

```bash
# Habilitar UFW e liberar portas necessárias
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Se estiver usando AWS, configure também o Security Group na console:
1. Abrir porta 80 (HTTP)
2. Abrir porta 443 (HTTPS) se usar SSL
3. Manter porta 22 (SSH) aberta apenas para IPs confiáveis

## 9. Verificar Logs

```bash
# Logs do Supervisor
sudo tail -f /var/log/sompo_app/sompo_app.out.log
sudo tail -f /var/log/sompo_app/sompo_app.err.log

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 10. Comandos Úteis

```bash
# Reiniciar a aplicação
sudo supervisorctl restart sompo_app

# Ver status da aplicação
sudo supervisorctl status

# Reiniciar Nginx
sudo systemctl restart nginx

# Ver logs em tempo real
sudo tail -f /var/log/sompo_app/sompo_app.out.log
```

## 11. SSL/HTTPS (Opcional)

Para configurar HTTPS com Certbot:

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado e configurar Nginx
sudo certbot --nginx -d seu-dominio.com
```

## 12. Monitoramento

Recomendado configurar:
- AWS CloudWatch para métricas do servidor (se EC2)
- AWS CloudWatch Logs para centralizar logs
- Configurar alarmes para CPU, memória e disco

## Troubleshooting

1. Se a aplicação não iniciar:
   - Verificar logs: `sudo tail -f /var/log/sompo_app/sompo_app.err.log`
   - Verificar permissões: `ls -la /home/ubuntu/sompo_app`
   - Verificar variáveis de ambiente

2. Se Nginx retornar 502:
   - Verificar se Gunicorn está rodando: `ps aux | grep gunicorn`
   - Verificar logs do Nginx: `sudo tail -f /var/log/nginx/error.log`

3. Problemas de permissão:
   - Verificar owner dos arquivos: `ls -la /home/ubuntu/sompo_app`
   - Ajustar se necessário: `sudo chown -R ubuntu:ubuntu /home/ubuntu/sompo_app`
