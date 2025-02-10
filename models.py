import os
import logging
from typing import Optional, List, Dict
import google.generativeai as genai

logger = logging.getLogger(__name__)

class BaseModelHandler:
    def generate_response(self, messages: List[Dict[str, str]]) -> Optional[str]:
        raise NotImplementedError

class GeminiModelHandler(BaseModelHandler):
    def __init__(self):
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}", exc_info=True)
            raise

    def generate_response(self, messages: List[Dict[str, str]], retry_count: int = 3) -> Optional[str]:
        for attempt in range(retry_count):
            try:
                response = self.model.generate_content(
                    messages[-1]['content'],
                    generation_config={
                        'temperature': 0.95,
                        'top_p': 0.95,
                        'top_k': 50,
                        'candidate_count': 1,
                    }
                )
                if response.text:
                    return response.text.strip()
                logger.warning(f"Empty response received on attempt {attempt + 1}")
                time.sleep(0.5)  # Shorter pause for faster responses
            except Exception as e:
                logger.error(f"Error generating response (attempt {attempt + 1}): {str(e)}", exc_info=True)
                if attempt < retry_count - 1:
                    time.sleep(1)  # Shorter pause between retries
                continue
                
        return "Something went wrong. Let's try again! 🔄"

def get_model_handler(model_name: str = "gemini") -> BaseModelHandler:
    logger.info(f"Initializing {model_name} model handler")
    try:
        if model_name == "gemini":
            logger.info("Starting Gemini model initialization")
            return GeminiModelHandler()
        else:
            logger.error(f"Unknown model: {model_name}")
            raise ValueError(f"Unknown model: {model_name}")
    except Exception as e:
        logger.error(f"Failed to initialize model handler: {str(e)}", exc_info=True)
        raise