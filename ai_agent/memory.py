"""
Memory - handles session, conversation, and context management.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .schema import SessionMemory, ConversationTurn


class MemoryManager:
    """
    Manages session memory, conversation history, and context.
    """
    
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self.sessions: Dict[str, SessionMemory] = {}
        self.conversations: Dict[str, List[ConversationTurn]] = {}
    
    def create_session(self, session_id: str, user_id: Optional[str] = None) -> SessionMemory:
        """Create a new session."""
        session = SessionMemory(
            session_id=session_id,
            user_id=user_id,
            ttl_seconds=self.ttl_seconds
        )
        self.sessions[session_id] = session
        self.conversations[session_id] = []
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        """Retrieve session if not expired."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check TTL
        oldest_turn = session.turns[0] if session.turns else None
        if oldest_turn:
            oldest_time = datetime.fromisoformat(oldest_turn["timestamp"])
            if datetime.utcnow() - oldest_time > timedelta(seconds=self.ttl_seconds):
                del self.sessions[session_id]
                return None
        
        return session
    
    def add_conversation_turn(self, session_id: str, turn: ConversationTurn) -> None:
        """Add a turn to conversation history."""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append(turn)
        
        # Also update session memory
        if session_id in self.sessions:
            self.sessions[session_id].turns.append({
                "turn_id": turn.turn_id,
                "intent": turn.intent.value if turn.intent else None,
                "timestamp": turn.timestamp.isoformat()
            })
    
    def get_conversation_history(self, session_id: str) -> List[ConversationTurn]:
        """Retrieve conversation history for a session."""
        return self.conversations.get(session_id, [])
    
    def resolve_entity_from_history(
        self, session_id: str, entity_type: str, fallback: str = None
    ) -> Optional[str]:
        """Resolve an entity from previous turns (e.g., "last quarter" context)."""
        history = self.get_conversation_history(session_id)
        
        # Search recent turns for entity
        for turn in reversed(history[-5:]):  # Last 5 turns
            if entity_type in turn.__dict__:
                return turn.__dict__[entity_type]
        
        return fallback
    
    def cache_result(self, session_id: str, key: str, value: Any, ttl: int = 600) -> None:
        """Cache a result in session memory."""
        if session_id in self.sessions:
            self.sessions[session_id].cache[key] = {
                "value": value,
                "cached_at": datetime.utcnow().isoformat(),
                "ttl": ttl
            }
    
    def get_cached_result(self, session_id: str, key: str) -> Optional[Any]:
        """Retrieve cached result if not expired."""
        if session_id not in self.sessions:
            return None
        
        cache_entry = self.sessions[session_id].cache.get(key)
        if not cache_entry:
            return None
        
        cached_at = datetime.fromisoformat(cache_entry["cached_at"])
        ttl = cache_entry.get("ttl", 600)
        
        if datetime.utcnow() - cached_at > timedelta(seconds=ttl):
            del self.sessions[session_id].cache[key]
            return None
        
        return cache_entry["value"]
    
    def update_entity_resolution(self, session_id: str, entity_name: str, value: str) -> None:
        """Store resolved entity for follow-up reference."""
        if session_id in self.sessions:
            self.sessions[session_id].resolved_entities[entity_name] = value
    
    def get_resolved_entities(self, session_id: str) -> Dict[str, str]:
        """Retrieve all resolved entities for a session."""
        if session_id in self.sessions:
            return self.sessions[session_id].resolved_entities
        return {}
    
    def clear_session(self, session_id: str) -> None:
        """Clear expired or finished session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def cleanup_expired_sessions(self) -> None:
        """Remove all expired sessions."""
        expired = []
        for session_id, session in self.sessions.items():
            if session.turns:
                oldest_time = datetime.fromisoformat(session.turns[0]["timestamp"])
                if datetime.utcnow() - oldest_time > timedelta(seconds=self.ttl_seconds):
                    expired.append(session_id)
        
        for session_id in expired:
            self.clear_session(session_id)
