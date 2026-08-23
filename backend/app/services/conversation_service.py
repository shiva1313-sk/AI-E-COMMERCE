import uuid
from datetime import datetime
from typing import Dict, List, Optional
import threading

from backend.app.models.chat import ChatMessageRecord, ConversationSession
from backend.app.core.logging import logger


class ConversationService:
    """In-memory session state and context manager for multi-turn conversations."""

    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}
        self._lock = threading.Lock()

    def get_or_create_session(self, conversation_id: Optional[str] = None) -> ConversationSession:
        """Retrieve existing session or create a new session."""
        with self._lock:
            if not conversation_id or conversation_id not in self.sessions:
                cid = conversation_id if conversation_id else str(uuid.uuid4())
                session = ConversationSession(conversation_id=cid)
                self.sessions[cid] = session
                logger.info(f"Created new conversation session: {cid}")
                return session
            
            session = self.sessions[conversation_id]
            session.last_active = datetime.utcnow()
            return session

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        recommended_product_ids: Optional[List[str]] = None
    ):
        """Append message to session history and update last recommended products."""
        with self._lock:
            if conversation_id not in self.sessions:
                self.sessions[conversation_id] = ConversationSession(conversation_id=conversation_id)
            
            session = self.sessions[conversation_id]
            record = ChatMessageRecord(
                role=role,  # type: ignore
                content=content,
                recommended_product_ids=recommended_product_ids
            )
            session.messages.append(record)
            session.last_active = datetime.utcnow()

            if recommended_product_ids:
                session.last_recommended_product_ids = recommended_product_ids

    def get_last_recommended_products(self, conversation_id: str) -> List[str]:
        """Retrieve IDs of products recommended in previous turns."""
        with self._lock:
            session = self.sessions.get(conversation_id)
            if not session:
                return []
            return session.last_recommended_product_ids

    def format_history(self, conversation_id: str, max_turns: int = 4) -> str:
        """Format recent chat history into readable context string."""
        with self._lock:
            session = self.sessions.get(conversation_id)
            if not session or not session.messages:
                return ""
            
            # Take last 2 * max_turns messages
            recent = session.messages[-(max_turns * 2):]
            formatted = []
            for msg in recent:
                prefix = "Customer" if msg.role == "user" else "Assistant"
                formatted.append(f"{prefix}: {msg.content}")
            return "\n".join(formatted)


conversation_service = ConversationService()
