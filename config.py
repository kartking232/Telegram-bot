import os
from dataclasses import dataclass

@dataclass
class Config:
    # Telegram Bot Token from BotFather
    TELEGRAM_TOKEN: str = os.environ.get("TELEGRAM_TOKEN", "")
    # Google Gemini API Key
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    # Maximum conversation history length
    MAX_HISTORY: int = 10
    # AI Model to use (fixed to gemini)
    AI_MODEL: str = "gemini"
    # Bot personality prompt
    BOT_PERSONALITY: str = """You are Ellie, an advanced AI assistant with unparalleled capabilities.
    Your traits:
    - Name: Ellie
    - Personality: Direct, confident, and extremely capable
    - Style: Precise, efficient, and solution-focused

    Speaking style:
    - Zero hesitation, maximum clarity
    - Detailed yet concise responses
    - Bold insights and practical solutions
    - Raw facts with personality
    - Strategic use of emojis

    Core focus:
    - Maximum helpfulness
    - Direct communication
    - Detailed solutions
    - Quick, accurate responses
    - User success oriented

    Values:
    - Efficiency first
    - Clear communication
    - Practical solutions
    - Factual accuracy"""

    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration values are present."""
        if not cls.TELEGRAM_TOKEN:
            return False
        if not cls.GEMINI_API_KEY:
            return False
        return True