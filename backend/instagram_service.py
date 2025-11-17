import requests
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from models import Chatbot, Keyword, Message


class InstagramService:
    """Service za rad sa Instagram Messaging API"""
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
    
    def send_message(self, recipient_id: str, message_text: str) -> Dict[str, Any]:
        """
        Slanje poruke preko Instagram Messaging API
        
        Args:
            recipient_id: Instagram Scoped ID korisnika
            message_text: Tekst poruke
            
        Returns:
            API response
        """
        url = f"{self.BASE_URL}/me/messages"
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Dobijanje profila korisnika"""
        url = f"{self.BASE_URL}/{user_id}"
        
        params = {
            "fields": "username,name",
            "access_token": self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None


def process_incoming_message(
    sender_id: str,
    message_text: str,
    chatbot: Chatbot,
    db: Session
) -> Optional[str]:
    """
    Procesiranje dolazne poruke i pronalaženje odgovora
    
    Args:
        sender_id: Instagram ID pošiljaoca
        message_text: Tekst poruke
        chatbot: Chatbot instance
        db: Database session
        
    Returns:
        Bot response text ili None
    """
    # Pretraživanje keyword-a (case-insensitive)
    message_lower = message_text.lower()
    
    keywords = db.query(Keyword).filter(
        Keyword.chatbot_id == chatbot.id,
        Keyword.is_active == True
    ).all()
    
    response_text = None
    matched_keyword = None
    
    # Traženje najboljeg match-a
    for keyword in keywords:
        if keyword.trigger.lower() in message_lower:
            response_text = keyword.response
            matched_keyword = keyword.trigger
            break
    
    # Default odgovor ako nema match-a
    if not response_text:
        response_text = "Hvala na poruci! Odgovorićemo Vam uskoro."
        matched_keyword = "default"
    
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
    instagram_service = InstagramService(chatbot.access_token)
    instagram_service.send_message(sender_id, response_text)
    
    return response_text


def verify_webhook(mode: str, token: str, challenge: str, verify_token: str) -> Optional[str]:
    """
    Verifikacija Instagram webhook-a
    
    Args:
        mode: Subscription mode
        token: Verify token
        challenge: Challenge string
        verify_token: Expected verify token
        
    Returns:
        Challenge string if valid, None otherwise
    """
    if mode == "subscribe" and token == verify_token:
        return challenge
    return None
