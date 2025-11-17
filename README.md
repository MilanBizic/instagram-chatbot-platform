# Instagram Chatbot Platform 🤖

Profesionalna SaaS platforma za kreiranje i upravljanje Instagram chatbotovima sa keyword-based automatskim odgovorima.

## 🎯 Funkcionalnosti

- ✅ **Admin autentifikacija** - Secure login/register sistem
- ✅ **Multi-bot management** - Kreiraj neograničen broj botova za različite Instagram naloge
- ✅ **Keyword-based odgovori** - Dodaj i edituj keyword trigere i automatske odgovore
- ✅ **Real-time Instagram integracija** - Webhook sistem za instant odgovore na poruke
- ✅ **Bot aktivacija/deaktivacija** - Kontroliši kada bot radi
- ✅ **Clean dashboard** - Intuitivni UI za upravljanje svim botovima

## 🏗️ Tehnički Stack

### Backend
- **Python 3.10+**
- **FastAPI** - Modern web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM
- **JWT** - Autentifikacija
- **Instagram Messaging API** - Meta Graph API

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client

## 📁 Struktura Projekta

```
instagram-chatbot-platform/
├── backend/
│   ├── main.py                 # FastAPI aplikacija
│   ├── models.py              # Database modeli
│   ├── schemas.py             # Pydantic schemas
│   ├── database.py            # DB konfiguracija
│   ├── auth.py                # JWT autentifikacija
│   ├── instagram_service.py  # Instagram API logika
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment template
│
└── frontend/
    ├── src/
    │   ├── pages/             # React komponente (Login, Dashboard, etc.)
    │   ├── context/           # Auth Context
    │   ├── services/          # API service
    │   └── App.jsx            # Main app
    ├── package.json
    └── .env.example
```

## 🚀 Instalacija i Pokretanje

### 1️⃣ Backend Setup

```bash
cd backend

# Kreiraj virtual environment
python -m venv venv
source venv/bin/activate  # Na Windows: venv\Scripts\activate

# Instaliraj dependencies
pip install -r requirements.txt

# Setup PostgreSQL bazu
# Kreiraj bazu "instagram_chatbot"
createdb instagram_chatbot

# Konfiguriši environment varijable
cp .env.example .env
# Edituj .env sa tvojim podacima:
# - DATABASE_URL
# - SECRET_KEY
# - WEBHOOK_VERIFY_TOKEN

# Pokreni server
python main.py
```

Backend će biti dostupan na: `http://localhost:8000`

API dokumentacija: `http://localhost:8000/docs`

### 2️⃣ Frontend Setup

```bash
cd frontend

# Instaliraj dependencies
npm install

# Konfiguriši environment
cp .env.example .env
# VITE_API_URL=http://localhost:8000/api

# Pokreni development server
npm run dev
```

Frontend će biti dostupan na: `http://localhost:5173`

## 📱 Instagram Setup

### Preduslovi
1. **Facebook Business Account** - Potreban je verifikovan business account
2. **Instagram Business/Creator Account** - Mora biti povezan sa Facebook stranicom
3. **Meta Developer App** - Kreiraj app na developers.facebook.com

### Koraci za Instagram API Setup

#### 1. Kreiraj Meta App
1. Idi na [Meta Developers](https://developers.facebook.com/)
2. Klikni **My Apps** → **Create App**
3. Odaberi **Business** app type
4. Popuni detalje i kreiraj app

#### 2. Dodaj Instagram Messaging
1. U Dashboard → **Add Products**
2. Dodaj **Instagram** produkt
3. Omogući **instagram_manage_messages** permission

#### 3. Dobij Access Token
1. Idi na **Tools** → **Access Token Tool**
2. Generiši **Page Access Token** sa sledećim permissions:
   - `instagram_basic`
   - `instagram_manage_messages`
   - `pages_manage_metadata`
3. Kopiraj token (čuvaj ga sigurno!)

#### 4. Dobij Instagram Account ID
1. Idi na Meta Business Suite
2. **Settings** → **Instagram Accounts**
3. Pronađi **Instagram Account ID** (17-cifreni broj)

#### 5. Setup Webhook
1. U Meta App Dashboard → **Instagram** → **Configuration**
2. Dodaj **Webhook Callback URL**: `https://tvoj-backend-url.com/api/webhook`
3. **Verify Token**: Unesi isti token kao u `.env` (`WEBHOOK_VERIFY_TOKEN`)
4. Subscribe to: `messages`

#### 6. Test Webhook
```bash
# Meta će poslati GET request za verifikaciju
# Tvoj backend će automatski odgovoriti sa challenge-om
```

## 🎮 Kako Koristiti Platformu

### 1. Registracija/Login
```
1. Otvori frontend (localhost:5173)
2. Klikni "Register"
3. Kreiraj admin nalog
4. Login sa kredencijalima
```

### 2. Kreiranje Chatbota
```
1. U Dashboard → "Create New Chatbot"
2. Unesi:
   - Bot Name (npr. "Store Bot")
   - Instagram Account ID
   - Instagram Username (opciono)
   - Access Token
3. Klikni "Create Chatbot"
```

### 3. Dodavanje Keyword-ova
```
1. Klikni na bot iz liste
2. "Add Keyword"
3. Unesi:
   - Trigger: "cena" ili "hello"
   - Response: "Naše cene počinju od 1000 RSD!"
4. Sačuvaj
```

### 4. Aktivacija Bota
```
1. Bot je automatski aktivan nakon kreiranja
2. Možeš ga deaktivirati klikom na "Deactivate"
3. Aktiviraj ponovo sa "Activate"
```

### 5. Testiranje
```
1. Pošalji Direct Message na tvoj Instagram nalog
2. Upiši keyword (npr. "cena")
3. Bot će automatski odgovoriti! 🎉
```

## 📊 Database Schema

```
users
├── id (PK)
├── username
├── email
├── hashed_password
└── created_at

chatbots
├── id (PK)
├── name
├── instagram_account_id
├── instagram_username
├── access_token
├── is_active
├── owner_id (FK → users)
├── created_at
└── updated_at

keywords
├── id (PK)
├── trigger
├── response
├── is_active
├── chatbot_id (FK → chatbots)
└── created_at

messages (log)
├── id (PK)
├── sender_id
├── sender_username
├── message_text
├── bot_response
├── matched_keyword
├── chatbot_id (FK → chatbots)
└── timestamp
```

## 🔐 Security Best Practices

1. **JWT Token** - Sve API rute su zaštićene JWT autentifikacijom
2. **Password Hashing** - Bcrypt za sigurno čuvanje passworda
3. **Access Token Encryption** - Instagram access tokeni su sigurno čuvani u bazi
4. **CORS** - Konfiguriši production CORS origins u `main.py`
5. **Environment Variables** - Nikad ne commit-uj `.env` fajlove!

## 🚢 Production Deployment

### Backend (Railway/DigitalOcean/Render)

```bash
# 1. Setup PostgreSQL database
# 2. Set environment variables
# 3. Deploy backend
# 4. Note backend URL za webhook
```

### Frontend (Vercel)

```bash
# 1. Push code to GitHub
# 2. Import projekt u Vercel
# 3. Set VITE_API_URL environment variable
# 4. Deploy
```

### Instagram Webhook Update
```
U Meta App Dashboard → Webhook URL
Promeni sa localhost na production backend URL
```

## 🐛 Troubleshooting

### Bot ne odgovara na poruke
- ✅ Proveri da li je bot **Active** u dashboard-u
- ✅ Verifikuj **Webhook** konfiguraciju u Meta App
- ✅ Proveri **Access Token** validnost
- ✅ Proveri backend logs za greške

### Webhook verification failed
- ✅ Proveri da li je `WEBHOOK_VERIFY_TOKEN` isti u `.env` i Meta App
- ✅ Proveri da li je backend dostupan (public URL)
- ✅ Testuj endpoint: `GET /api/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=123`

### Database connection error
- ✅ Proveri `DATABASE_URL` u `.env`
- ✅ Proveri da li PostgreSQL radi
- ✅ Proveri database credentials

## 📝 API Dokumentacija

FastAPI automatski generiše Swagger dokumentaciju:

```
http://localhost:8000/docs
```

### Glavni Endpoints

#### Auth
- `POST /api/auth/register` - Registracija
- `POST /api/auth/login` - Login (vraća JWT token)
- `GET /api/auth/me` - Get current user

#### Chatbots
- `GET /api/chatbots` - Lista svih botova
- `POST /api/chatbots` - Kreiranje bota
- `GET /api/chatbots/{id}` - Detalji bota
- `PUT /api/chatbots/{id}` - Update bota
- `DELETE /api/chatbots/{id}` - Brisanje bota

#### Keywords
- `GET /api/chatbots/{id}/keywords` - Lista keyword-ova
- `POST /api/keywords` - Dodavanje keyword-a
- `PUT /api/keywords/{id}` - Update keyword-a
- `DELETE /api/keywords/{id}` - Brisanje keyword-a

#### Webhook
- `GET /api/webhook` - Verifikacija webhook-a
- `POST /api/webhook` - Prijem Instagram poruka

## 🎓 Kako Sistem Radi

```
1. User pošalje DM na Instagram
        ↓
2. Instagram šalje webhook na tvoj backend
        ↓
3. Backend proverava koji chatbot je za taj Instagram account
        ↓
4. Backend traži keyword u poruci korisnika
        ↓
5. Nalazi matching keyword → dobija response
        ↓
6. Šalje automatski odgovor preko Instagram API
        ↓
7. Loguje konverzaciju u database
```

## 📈 Buduće Funkcionalnosti (Opciono)

- [ ] Analytics dashboard (broj poruka, conversion rate)
- [ ] AI-powered odgovori (GPT integracija)
- [ ] Scheduled messages
- [ ] Multi-user support (klijenti sa svojim login-ima)
- [ ] Email notifikacije
- [ ] Story replies automation

## 🤝 Contributing

Ovo je MVP verzija. Za dodavanje novih funkcionalnosti:

1. Fork projekat
2. Kreiraj feature branch
3. Commit promene
4. Push na branch
5. Otvori Pull Request

## 📄 License

MIT License - Free to use and modify!

## 💬 Support

Za pitanja i probleme:
- GitHub Issues
- Email: support@yourplatform.com

---

**Napravljen sa ❤️ za automatizaciju Instagram komunikacije**

🚀 **Happy Automating!**
