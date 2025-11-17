from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

from database import get_db, engine
from models import Base, User, Chatbot, Keyword, Message
from schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    ChatbotCreate, ChatbotUpdate, ChatbotResponse,
    KeywordCreate, KeywordUpdate, KeywordResponse,
    MessageResponse
)
from auth import (
    get_password_hash, verify_password, create_access_token, get_current_user
)
from instagram_service import process_incoming_message, verify_webhook

# Kreiranje tabela
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Instagram Chatbot Platform API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "your-verify-token-123")


# ==================== AUTH ROUTES ====================

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registracija novog admin korisnika"""
    # Provera da li user već postoji
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Kreiranje novog usera
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@app.post("/api/auth/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login i dobijanje JWT tokena"""
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # FIX: Konvertuj user.id u STRING!
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }


# ==================== CHATBOT ROUTES ====================

@app.get("/api/chatbots", response_model=List[ChatbotResponse])
def get_chatbots(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dobijanje svih chatbotova"""
    chatbots = db.query(Chatbot).filter(Chatbot.owner_id == current_user.id).all()
    return [
        {
            "id": bot.id,
            "name": bot.name,
            "instagram_account_id": bot.instagram_account_id,
            "instagram_username": bot.instagram_username,
            "is_active": bot.is_active,
            "created_at": bot.created_at,
            "updated_at": bot.updated_at
        }
        for bot in chatbots
    ]


@app.post("/api/chatbots", response_model=ChatbotResponse, status_code=status.HTTP_201_CREATED)
def create_chatbot(
    chatbot_data: ChatbotCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kreiranje novog chatbota"""
    # Provera da li već postoji bot za taj Instagram account
    existing = db.query(Chatbot).filter(
        Chatbot.instagram_account_id == chatbot_data.instagram_account_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Chatbot for this Instagram account already exists")
    
    new_chatbot = Chatbot(
        name=chatbot_data.name,
        instagram_account_id=chatbot_data.instagram_account_id,
        instagram_username=chatbot_data.instagram_username,
        access_token=chatbot_data.access_token,
        owner_id=current_user.id
    )
    
    db.add(new_chatbot)
    db.commit()
    db.refresh(new_chatbot)
    
    return new_chatbot


@app.get("/api/chatbots/{chatbot_id}", response_model=ChatbotResponse)
def get_chatbot(
    chatbot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dobijanje specifičnog chatbota"""
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.owner_id == current_user.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    return chatbot


@app.put("/api/chatbots/{chatbot_id}", response_model=ChatbotResponse)
def update_chatbot(
    chatbot_id: int,
    chatbot_data: ChatbotUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ažuriranje chatbota"""
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.owner_id == current_user.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    # Update polja
    if chatbot_data.name is not None:
        chatbot.name = chatbot_data.name
    if chatbot_data.instagram_username is not None:
        chatbot.instagram_username = chatbot_data.instagram_username
    if chatbot_data.access_token is not None:
        chatbot.access_token = chatbot_data.access_token
    if chatbot_data.is_active is not None:
        chatbot.is_active = chatbot_data.is_active
    
    db.commit()
    db.refresh(chatbot)
    
    return chatbot


@app.delete("/api/chatbots/{chatbot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chatbot(
    chatbot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Brisanje chatbota"""
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.owner_id == current_user.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    db.delete(chatbot)
    db.commit()
    
    return None


# ==================== KEYWORD ROUTES ====================

@app.get("/api/chatbots/{chatbot_id}/keywords", response_model=List[KeywordResponse])
def get_keywords(
    chatbot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dobijanje svih keyword-ova za chatbot"""
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == chatbot_id,
        Chatbot.owner_id == current_user.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    keywords = db.query(Keyword).filter(Keyword.chatbot_id == chatbot_id).all()
    return keywords


@app.post("/api/keywords", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
def create_keyword(
    keyword_data: KeywordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kreiranje novog keyword-a"""
    # Provera da li chatbot pripada current useru
    chatbot = db.query(Chatbot).filter(
        Chatbot.id == keyword_data.chatbot_id,
        Chatbot.owner_id == current_user.id
    ).first()
    
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    new_keyword = Keyword(
        trigger=keyword_data.trigger,
        response=keyword_data.response,
        chatbot_id=keyword_data.chatbot_id
    )
    
    db.add(new_keyword)
    db.commit()
    db.refresh(new_keyword)
    
    return new_keyword


@app.put("/api/keywords/{keyword_id}", response_model=KeywordResponse)
def update_keyword(
    keyword_id: int,
    keyword_data: KeywordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ažuriranje keyword-a"""
    keyword = db.query(Keyword).join(Chatbot).filter(
        Keyword.id == keyword_id,
        Chatbot.owner_id == current_user.id
    ).first()
    
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    
    if keyword_data.trigger is not None:
        keyword.trigger = keyword_data.trigger
    if keyword_data.response is not None:
        keyword.response = keyword_data.response
    if keyword_data.is_active is not None:
        keyword.is_active = keyword_data.is_active
    
    db.commit()
    db.refresh(keyword)
    
    return keyword


@app.delete("/api/keywords/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword(
    keyword_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Brisanje keyword-a"""
    keyword = db.query(Keyword).join(Chatbot).filter(
        Keyword.id == keyword_id,
        Chatbot.owner_id == current_user.id
    ).first()
    
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    
    db.delete(keyword)
    db.commit()
    
    return None


# ==================== INSTAGRAM WEBHOOK ====================

@app.get("/api/webhook")
def verify_webhook_endpoint(
    request: Request,
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Instagram webhook verification"""
    mode = hub_mode or request.query_params.get("hub.mode")
    token = hub_verify_token or request.query_params.get("hub.verify_token")
    challenge = hub_challenge or request.query_params.get("hub.challenge")
    
    result = verify_webhook(mode, token, challenge, WEBHOOK_VERIFY_TOKEN)
    
    if result:
        return int(result)
    else:
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/api/webhook")
async def webhook_handler(request: Request, db: Session = Depends(get_db)):
    """Primanje Instagram poruka"""
    try:
        body = await request.json()
        
        if body.get("object") != "instagram":
            return {"status": "ignored"}
        
        for entry in body.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                recipient_id = messaging_event["recipient"]["id"]
                
                # Provera da li postoji poruka
                if "message" in messaging_event:
                    message_text = messaging_event["message"].get("text", "")
                    
                    # Pronalaženje chatbota za ovaj Instagram account
                    chatbot = db.query(Chatbot).filter(
                        Chatbot.instagram_account_id == recipient_id,
                        Chatbot.is_active == True
                    ).first()
                    
                    if chatbot:
                        # Procesiranje poruke i slanje odgovora
                        process_incoming_message(sender_id, message_text, chatbot, db)
        
        return {"status": "ok"}
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}


# ==================== HEALTH CHECK ====================

@app.get("/")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Instagram Chatbot Platform API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
