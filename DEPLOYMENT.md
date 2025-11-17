# 🚀 Production Deployment Guide

Ovaj guide pokriva deployment na različite platforme.

## 📋 Pre-Deployment Checklist

- [ ] PostgreSQL baza kreirana
- [ ] Instagram Business Account povezan
- [ ] Meta App kreiran sa Instagram permissions
- [ ] Access Token generisan
- [ ] Webhook verify token generisan

---

## 🐳 Option 1: Docker Deployment (Preporučeno)

### Kreiranje Dockerfile za Backend

```dockerfile
# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose za ceo stack

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: instagram_chatbot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@db:5432/instagram_chatbot
      SECRET_KEY: ${SECRET_KEY}
      WEBHOOK_VERIFY_TOKEN: ${WEBHOOK_VERIFY_TOKEN}
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  postgres_data:
```

### Pokretanje

```bash
# Kreiraj .env fajl sa:
# DB_PASSWORD=your-secure-password
# SECRET_KEY=your-secret-key
# WEBHOOK_VERIFY_TOKEN=your-webhook-token

docker-compose up -d
```

---

## ☁️ Option 2: Railway (Najbrži)

### Backend na Railway

1. **Kreiraj Railway projekat**
   ```
   - Idi na railway.app
   - New Project → Deploy from GitHub
   - Selektuj tvoj repo
   ```

2. **Dodaj PostgreSQL**
   ```
   - New → Database → PostgreSQL
   - Railway će automatski kreirati DATABASE_URL
   ```

3. **Environment Variables**
   ```
   SECRET_KEY=generisi-random-string-ovde
   WEBHOOK_VERIFY_TOKEN=tvoj-verify-token
   ```

4. **Deploy Settings**
   ```
   Root Directory: backend
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

5. **Dobij Public URL**
   ```
   Settings → Generate Domain
   Kopiraj URL (npr. https://your-app.railway.app)
   ```

---

## 🔵 Option 3: DigitalOcean App Platform

### Backend Deployment

1. **Kreiraj App**
   ```
   - Apps → Create App
   - Connect GitHub repo
   ```

2. **Configure App**
   ```
   Name: instagram-bot-backend
   Type: Web Service
   Source: backend/
   Build Command: pip install -r requirements.txt
   Run Command: uvicorn main:app --host 0.0.0.0 --port 8080
   ```

3. **Managed Database**
   ```
   - Create → Database → PostgreSQL
   - Attach to app
   ```

4. **Environment Variables**
   ```bash
   DATABASE_URL=${db.DATABASE_URL}
   SECRET_KEY=your-secret-key
   WEBHOOK_VERIFY_TOKEN=your-token
   ```

---

## ▲ Option 4: Vercel (Frontend Only)

### Frontend na Vercel

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Import u Vercel**
   ```
   - vercel.com → New Project
   - Import GitHub repo
   - Root Directory: frontend
   ```

3. **Environment Variable**
   ```
   VITE_API_URL=https://your-backend-url.com/api
   ```

4. **Build Settings**
   ```
   Framework Preset: Vite
   Build Command: npm run build
   Output Directory: dist
   ```

5. **Deploy**
   ```
   Click Deploy → Done! 🎉
   ```

---

## 🌐 Option 5: VPS (Ubuntu/Debian)

### Backend Setup na VPS

```bash
# 1. Update sistem
sudo apt update && sudo apt upgrade -y

# 2. Install Python & PostgreSQL
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx -y

# 3. Kreiraj bazu
sudo -u postgres psql
CREATE DATABASE instagram_chatbot;
CREATE USER botuser WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE instagram_chatbot TO botuser;
\q

# 4. Clone repo
cd /var/www
git clone https://github.com/yourusername/instagram-chatbot-platform.git
cd instagram-chatbot-platform/backend

# 5. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configure .env
nano .env
# Dodaj DATABASE_URL, SECRET_KEY, WEBHOOK_VERIFY_TOKEN

# 7. Setup systemd service
sudo nano /etc/systemd/system/chatbot-backend.service
```

**chatbot-backend.service:**
```ini
[Unit]
Description=Instagram Chatbot Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/instagram-chatbot-platform/backend
Environment="PATH=/var/www/instagram-chatbot-platform/backend/venv/bin"
ExecStart=/var/www/instagram-chatbot-platform/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl start chatbot-backend
sudo systemctl enable chatbot-backend
```

### Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/chatbot-backend
```

**chatbot-backend:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/chatbot-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL sa Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 📱 Instagram Webhook Configuration

Nakon deployovanja backend-a:

1. **Idi u Meta Developers**
   ```
   Tvoj App → Products → Instagram → Configuration
   ```

2. **Callback URL**
   ```
   https://your-backend-domain.com/api/webhook
   ```

3. **Verify Token**
   ```
   Koristi isti token iz WEBHOOK_VERIFY_TOKEN
   ```

4. **Subscribe to Fields**
   ```
   ✅ messages
   ```

5. **Test Webhook**
   ```bash
   curl "https://your-backend-domain.com/api/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=TEST"
   ```

---

## 🔒 Production Security

### 1. Environment Variables
```bash
# Nikad ne hardcode-uj credentials!
# Koristi environment variables za:
- DATABASE_URL
- SECRET_KEY (minimum 32 karaktera)
- WEBHOOK_VERIFY_TOKEN
- Instagram Access Tokens
```

### 2. CORS Configuration
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Samo production URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. HTTPS Only
```
- Uvek koristi HTTPS u produkciji
- Let's Encrypt za besplatne SSL certifikate
```

### 4. Database Backups
```bash
# Automated daily backups
pg_dump instagram_chatbot > backup_$(date +%Y%m%d).sql
```

---

## 📊 Monitoring & Logs

### Backend Logs
```bash
# Systemd logs
sudo journalctl -u chatbot-backend -f

# Application logs
tail -f /var/www/instagram-chatbot-platform/backend/logs/app.log
```

### Health Check Endpoint
```python
# Backend već ima: GET /
# Returns: {"status": "ok"}
```

---

## 🧪 Testing Production

```bash
# 1. Test health
curl https://your-backend-domain.com/

# 2. Test webhook
curl "https://your-backend-domain.com/api/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=123"

# 3. Test frontend
curl https://your-frontend-domain.com/

# 4. Test full flow
# Pošalji DM na Instagram → proveri odgovor
```

---

## 🆘 Troubleshooting

### Backend ne radi
```bash
# Check service status
sudo systemctl status chatbot-backend

# Check logs
sudo journalctl -u chatbot-backend -n 50

# Restart service
sudo systemctl restart chatbot-backend
```

### Webhook ne prima poruke
```bash
# 1. Proveri URL dostupnost
curl https://your-backend-domain.com/api/webhook

# 2. Proveri Meta App settings
# 3. Proveri access token validnost
# 4. Proveri logs za greške
```

### Database connection error
```bash
# Test connection
psql -h localhost -U botuser -d instagram_chatbot

# Check DATABASE_URL format
# postgresql://username:password@host:port/database
```

---

## 🎉 Gotovo!

Tvoja platforma je sada live i radi! 

**Sledeći koraci:**
1. Test celokupan sistem
2. Kreiraj prvi chatbot preko UI
3. Dodaj keyword-ove
4. Pošalji test poruku

**Monitoring:**
- Redovno proveri logs
- Setup uptime monitoring (UptimeRobot)
- Backup baze dnevno

---

**Need help?** Konsultuj README.md ili otvori GitHub Issue.

🚀 **Happy Deploying!**
