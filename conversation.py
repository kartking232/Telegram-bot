from typing import List, Dict
from dataclasses import dataclass, field
from config import Config

@dataclass
class Conversation:
    chat_id: int
    messages: List[Dict[str, str]] = field(default_factory=list)
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})
        # Keep only the last MAX_HISTORY messages
        if len(self.messages) > Config.MAX_HISTORY:
            self.messages = self.messages[-Config.MAX_HISTORY:]
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get the full conversation context."""
        system_message = {"role": "system", "content": Config.BOT_PERSONALITY}
        return [system_message] + self.messages
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.messages = []

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[int, Conversation] = {}
    
    def get_conversation(self, chat_id: int) -> Conversation:
        """Get or create a conversation for a chat ID."""
        if chat_id not in self.conversations:
            self.conversations[chat_id] = Conversation(chat_id)
        return self.conversations[chat_id]
    
    def clear_conversation(self, chat_id: int) -> None:
        """Clear the conversation history for a chat ID."""
        if chat_id in self.conversations:
            self.conversations[chat_id].clear_history()
