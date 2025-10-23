# 🚀 Guida al Deployment

Guida per mettere in produzione Officina AI Assistant.

## 📋 Indice

1. [Opzioni di Deployment](#opzioni-di-deployment)
2. [Streamlit Cloud](#streamlit-cloud)
3. [Docker](#docker)
4. [VPS/Server Dedicato](#vpsserver-dedicato)
5. [AWS/GCP/Azure](#cloud-providers)
6. [Sicurezza](#sicurezza)

---

## Opzioni di Deployment

### 🏆 Raccomandazioni

| Scenario | Soluzione | Costo | Difficoltà |
|----------|-----------|-------|------------|
| **Demo/Test** | Streamlit Cloud | Gratis | ⭐ Facile |
| **Uso interno** | Docker su VPS | $5-20/mese | ⭐⭐ Medio |
| **Produzione** | AWS/GCP | $50-200/mese | ⭐⭐⭐ Avanzato |
| **Enterprise** | Kubernetes | $200+/mese | ⭐⭐⭐⭐ Esperto |

---

## Streamlit Cloud

**Ideale per:** Demo, testing, piccoli team

### Setup

1. **Push su GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/tuousername/officina-ai.git
git push -u origin main
```

2. **Deploy su Streamlit Cloud**
   - Vai su [share.streamlit.io](https://share.streamlit.io)
   - Connetti GitHub
   - Seleziona repository
   - Deploy!

3. **Configura Secrets**

In Streamlit Cloud settings, aggiungi:

```toml
# .streamlit/secrets.toml
ANTHROPIC_API_KEY = "sk-ant-api..."
PINECONE_API_KEY = "..."
PINECONE_ENVIRONMENT = "gcp-starter"
PINECONE_INDEX_NAME = "officina-manuali"
LLM_PROVIDER = "anthropic"
```

### Limitazioni

- ❌ No storage persistente per manuali
- ❌ Timeout 10 minuti
- ✅ Gratis fino a 1GB RAM

**Soluzione:** Indicizza manuali localmente, poi usa solo l'app

---

## Docker

**Ideale per:** Server propri, controllo completo

### Build & Run

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down
```

### Deploy su VPS (DigitalOcean, Linode, etc.)

```bash
# 1. SSH nel server
ssh root@your-server-ip

# 2. Installa Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 3. Clone repository
git clone https://github.com/tuousername/officina-ai.git
cd officina-ai

# 4. Configura .env
nano .env
# ... aggiungi le tue API keys

# 5. Deploy
docker-compose up -d

# 6. Setup SSL (opzionale ma raccomandato)
# Vedi sezione SSL più avanti
```

### Docker Compose Produzione

```yaml
version: '3.8'

services:
  officina-ai:
    build: .
    container_name: officina-ai
    restart: always
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./data/manuali:/app/data/manuali:ro
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    
  officina-ai-api:
    build: .
    container_name: officina-ai-api
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./data/manuali:/app/data/manuali:ro
      - ./logs:/app/logs
    command: uvicorn api:app --host 0.0.0.0 --port 8000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - officina-ai
      - officina-ai-api
```

---

## VPS/Server Dedicato

**Ideale per:** Controllo completo, dati sensibili

### Requisiti Server

- **CPU:** 2+ cores
- **RAM:** 4GB+ (8GB raccomandato)
- **Storage:** 20GB+ SSD
- **OS:** Ubuntu 22.04 LTS

### Setup Completo

```bash
# 1. Update sistema
sudo apt update && sudo apt upgrade -y

# 2. Installa dipendenze
sudo apt install -y python3.11 python3.11-venv python3-pip \
    tesseract-ocr tesseract-ocr-ita poppler-utils nginx

# 3. Setup applicazione
git clone https://github.com/tuousername/officina-ai.git
cd officina-ai

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configura .env
cp .env.example .env
nano .env

# 5. Indicizza manuali (locale o già fatto)
python scripts/index_manuals.py

# 6. Setup systemd service
sudo nano /etc/systemd/system/officina-ai.service
```

**officina-ai.service:**
```ini
[Unit]
Description=Officina AI Assistant
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/officina-ai
Environment="PATH=/home/ubuntu/officina-ai/venv/bin"
ExecStart=/home/ubuntu/officina-ai/venv/bin/streamlit run app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Avvia servizio
sudo systemctl daemon-reload
sudo systemctl enable officina-ai
sudo systemctl start officina-ai
sudo systemctl status officina-ai
```

---

## Nginx Reverse Proxy + SSL

### Nginx Configuration

**`/etc/nginx/sites-available/officina-ai`:**

```nginx
server {
    listen 80;
    server_name officina-ai.tuodominio.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name officina-ai.tuodominio.com;
    
    # SSL Certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/officina-ai.tuodominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/officina-ai.tuodominio.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Streamlit App
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # API Endpoint
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Setup SSL con Let's Encrypt

```bash
# Installa Certbot
sudo apt install certbot python3-certbot-nginx

# Ottieni certificato
sudo certbot --nginx -d officina-ai.tuodominio.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Cloud Providers

### AWS (EC2 + RDS)

```bash
# 1. Launch EC2 instance (t3.medium)
# 2. Setup come VPS sopra
# 3. Opzionale: RDS per database (se espandi)

# 4. Security Groups
# - Inbound: 80, 443, 22
# - Outbound: All

# 5. Elastic IP (IP statico)
```

### Google Cloud Platform

```bash
# Deploy su Cloud Run (serverless)

# 1. Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/officina-ai

# 2. Deploy
gcloud run deploy officina-ai \
  --image gcr.io/PROJECT_ID/officina-ai \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

### Azure

```bash
# Deploy su Azure Container Instances

az container create \
  --resource-group officina-rg \
  --name officina-ai \
  --image officina-ai:latest \
  --dns-name-label officina-ai \
  --ports 8501
```

---

## Sicurezza

### 🔒 Checklist Sicurezza

- [ ] **HTTPS** obbligatorio (Let's Encrypt)
- [ ] **API Key** per endpoint sensibili
- [ ] **Firewall** configurato (ufw)
- [ ] **Rate limiting** su nginx
- [ ] **Backup automatici** manuali e indice
- [ ] **Logging** abilitato
- [ ] **Monitoring** (Uptime Robot, etc.)
- [ ] **Updates** regolari sistema

### Rate Limiting (Nginx)

```nginx
# nginx.conf
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    server {
        location /api {
            limit_req zone=api burst=20 nodelay;
            ...
        }
    }
}
```

### Firewall (UFW)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### Backup Automatico

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/officina-ai"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup manuali
tar -czf $BACKUP_DIR/manuali_$DATE.tar.gz data/manuali/

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# Cleanup vecchi backup (>30 giorni)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Upload su S3 (opzionale)
# aws s3 cp $BACKUP_DIR s3://your-bucket/backups/ --recursive
```

**Cron:**
```bash
crontab -e
# Backup giornaliero alle 2 AM
0 2 * * * /home/ubuntu/backup.sh
```

---

## Monitoring

### Health Checks

```python
# healthcheck.py
import requests
import sys

def check_health():
    try:
        response = requests.get("http://localhost:8501/_stcore/health", timeout=5)
        if response.status_code == 200:
            print("✅ App healthy")
            return 0
        else:
            print(f"❌ App unhealthy: {response.status_code}")
            return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_health())
```

### Uptime Monitoring

Servizi gratuiti:
- [UptimeRobot](https://uptimerobot.com/)
- [Pingdom](https://www.pingdom.com/)
- [StatusCake](https://www.statuscake.com/)

### Application Monitoring

```python
# Integra Sentry per error tracking
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0
)
```

---

## Performance Tuning

### Caching

```python
# Aggiungi cache in config/settings.py
ENABLE_CACHE = True
CACHE_TTL = 3600  # 1 ora

# Usa functools
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(question, marca):
    return chatbot.ask(question, filters={"marca": marca})
```

### Load Balancing

```nginx
# nginx.conf
upstream officina_backend {
    server localhost:8501 weight=3;
    server localhost:8502 weight=2;
    server localhost:8503 weight=1;
}

server {
    location / {
        proxy_pass http://officina_backend;
    }
}
```

---

## 📊 Costi Stimati

### Piccola Scala (10-100 utenti/giorno)

- **VPS:** $10-20/mese (DigitalOcean Droplet)
- **LLM API:** $20-50/mese
- **Pinecone:** Gratis
- **Dominio:** $10-15/anno
- **SSL:** Gratis (Let's Encrypt)

**Totale:** ~$30-70/mese

### Media Scala (100-1000 utenti/giorno)

- **VPS:** $40-80/mese (4GB RAM)
- **LLM API:** $100-300/mese
- **Pinecone:** $70/mese (Standard)
- **CDN:** $20/mese
- **Backup:** $10/mese

**Totale:** ~$240-480/mese

---

## 🆘 Troubleshooting Deployment

### App non si avvia

```bash
# Check logs
sudo journalctl -u officina-ai -f

# Check port
sudo netstat -tlnp | grep 8501

# Check permissions
ls -la /home/ubuntu/officina-ai
```

### Out of Memory

```bash
# Aggiungi swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### SSL Issues

```bash
# Rinnova certificati
sudo certbot renew --force-renewal

# Test configurazione nginx
sudo nginx -t
```

---

## ✅ Checklist Pre-Produzione

- [ ] .env configurato con tutte le key
- [ ] Manuali indicizzati
- [ ] HTTPS configurato
- [ ] Firewall attivo
- [ ] Backup automatici configurati
- [ ] Monitoring attivo
- [ ] Rate limiting configurato
- [ ] Health checks funzionanti
- [ ] Dominio puntato correttamente
- [ ] Test carico eseguiti

---

## 📞 Supporto

Per problemi di deployment:
- Controlla [docs/SETUP.md](./SETUP.md) Troubleshooting
- Apri issue su GitHub
- Contatta supporto provider cloud

**Buon deployment! 🚀**