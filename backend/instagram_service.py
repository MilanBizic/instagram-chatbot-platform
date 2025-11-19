from typing import Optional
import requests
from sqlalchemy.orm import Session
from models import Chatbot, Keyword, Message


class InstagramService:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.instagram.com/v18.0"
    
    def send_message(self, recipient_id: str, message_text: str) -> dict:
        """Slanje poruke preko Instagram API"""
        url = f"{self.base_url}/me/messages"
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }
        
        params = {"access_token": self.access_token}
        
        try:
            response = requests.post(url, json=payload, params=params)
            return response.json()
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return {"error": str(e)}


def process_incoming_message(
    sender_id: str,
    message_text: str,
    chatbot: Chatbot,
    db: Session
) -> Optional[str]:
    """
    Procesiranje dolazne poruke i pronalaženje odgovora
    """
    try:
        # Pretraživanje keyword-a (case-insensitive)
        message_lower = message_text.lower()
        
        keywords = db.query(Keyword).filter(
            Keyword.chatbot_id == chatbot.id,
            Keyword.is_active == True
        ).all()
        
        print(f"🔍 Found {len(keywords)} keywords for chatbot")
        
        response_text = None
        matched_keyword = None
        
        # Traženje najboljeg match-a
        for keyword in keywords:
            if keyword.trigger.lower() in message_lower:
                response_text = keyword.response
                matched_keyword = keyword.trigger
                print(f"✅ Matched keyword: {matched_keyword}")
                break
        
        # Default odgovor ako nema match-a
        if not response_text:
            response_text = "Hvala na poruci! Odgovorićemo Vam uskoro."
            matched_keyword = "default"
            print(f"⚠️ No keyword match, using default response")
        
        # Logovanje poruke
        new_message = Message(
            sender_id=sender_id,
            message_text=message_text,
            bot_response=response_text,
            matched_keyword=matched_keyword,
            chatbot_id=chatbot.id
        )
        
        db.add(new_message)
        db.commit()
        
        # Slanje odgovora preko Instagram API
        print(f"📤 Sending response to {sender_id}: {response_text[:50]}...")
        instagram_service = InstagramService(chatbot.access_token)
        result = instagram_service.send_message(sender_id, response_text)
        print(f"📨 Instagram API response: {result}")
        
        return response_text
        
    except Exception as e:
        print(f"❌ Error in process_incoming_message: {e}")
        return None


def verify_webhook(mode: str, token: str, challenge: str, verify_token: str) -> Optional[str]:
    """
    Verifikacija Instagram webhook-a
    """
    if mode == "subscribe" and token == verify_token:
        return challenge
    return None