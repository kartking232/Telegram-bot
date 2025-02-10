import logging
import re
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from conversation import ConversationManager
from models import get_model_handler
from gtts import gTTS
import tempfile
import os

# Initialize model handler
model_handler = get_model_handler(Config.AI_MODEL)

# Initialize conversation manager
conversation_manager = ConversationManager()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def error_handler(func):
    """Decorator for handling errors in command handlers."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            await update.message.reply_text(
                "Damn, something went wrong! Try again later? 🤷‍♀️"
            )
    return wrapper

@error_handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /start command."""
    welcome_message = (
        "Hey there! 👋 I'm Ellie, your fun AI buddy! \n\n"
        "I'm here to chat about literally anything - no boring stuff, promise! "
        "Hit me up with whatever's on your mind! 🎭\n\n"
        "Here's what I can do:\n"
        "🌟 /start - Show this message\n"
        "💭 /help - Get help (duh!)\n"
        "🔄 /clear - Fresh start\n"
        "🗣️ /speak [text] - I'll say it out loud!"
    )
    await update.message.reply_text(welcome_message)
    logger.info(f"Start command executed for chat_id: {update.effective_chat.id}")

@error_handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /help command."""
    help_text = (
        "Let's get this party started! 🎉\n\n"
        "I'm Ellie, your AI bestie who's down to chat about anything and everything! "
        "No filters, just pure fun and real talk! 🎭\n\n"
        "Here's the cool stuff we can do:\n"
        "- Chat about literally anything!\n"
        "- Get some wild ideas going\n"
        "- Turn text into speech\n"
        "- Start fresh whenever with /clear\n\n"
        "Commands:\n"
        "🌟 /start - Let's go!\n"
        "💭 /help - You're looking at it\n"
        "🔄 /clear - Clean slate\n"
        "🗣️ /speak [text] - Make me talk!"
    )
    await update.message.reply_text(help_text)
    logger.info(f"Help command executed for chat_id: {update.effective_chat.id}")

@error_handler
async def speak_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /speak command to convert text to speech."""
    if not context.args:
        await update.message.reply_text(
            "Yo! What do you want me to say? Try: /speak Hey, what's up!"
        )
        return

    text = " ".join(context.args)
    logger.info(f"Converting to speech: {text}")

    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            tts = gTTS(text=text, lang='en')
            tts.save(temp_file.name)
            await context.bot.send_voice(
                chat_id=update.effective_chat.id,
                voice=open(temp_file.name, 'rb'),
                caption="🗣️ Here's your voice message!"
            )
            os.unlink(temp_file.name)  # Clean up the temporary file
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Oops, couldn't make that voice message! Try something shorter maybe? 🤔"
        )

@error_handler
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /clear command."""
    chat_id = update.effective_chat.id
    conversation_manager.clear_conversation(chat_id)
    await update.message.reply_text("A fresh canvas awaits our next conversation! ✨🎨")
    logger.info(f"Clear command executed for chat_id: {chat_id}")

@error_handler
async def generate_image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /generate command to create images."""
    chat_id = update.effective_chat.id

    if Config.AI_MODEL != "gemini":
        await update.message.reply_text(
            "I apologize, but image generation is only available when using the Gemini model. "
            "Please contact the administrator to enable this feature. ✨"
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Please provide a description for the image you'd like me to create!\n"
            "Example: /generate a magical forest at sunset with fireflies"
        )
        logger.info(f"Image generation attempted without prompt by chat_id: {chat_id}")
        return

    prompt = " ".join(context.args)
    logger.info(f"Image generation requested by chat_id: {chat_id} with prompt: {prompt}")

    try:
        await update.message.reply_text("🎨 Creating your artistic vision... Please wait...")

        # Enhance prompt for better artistic results
        artistic_prompt = (
            f"Create a visually stunning and artistic image of: {prompt}. "
            "Focus on aesthetic beauty, creative composition, and artistic style. "
            "Make it emotionally evocative and visually captivating."
        )

        image_url = model_handler.generate_image(artistic_prompt)
        if image_url:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=f"✨ Here's your artistic creation: {prompt}\n\nI hope this captures the essence of your vision! Let me know if you'd like to create something else. 🎨"
            )
            logger.info(f"Successfully generated and sent image for chat_id: {chat_id}")
        else:
            await update.message.reply_text(
                "I apologize, but I couldn't create the image you requested. "
                "Could you try describing it differently? Sometimes simpler descriptions work better! ✨🎨"
            )

    except Exception as e:
        logger.error(f"Error generating image for chat_id {chat_id}: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "I encountered an error while creating your image. 🎨\n"
            "Some tips for better results:\n"
            "- Try a simpler description\n"
            "- Be more specific about what you want\n"
            "- Avoid complex or abstract concepts\n\n"
            "Would you like to try again? 💫"
        )

@error_handler
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for regular messages."""
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user_message = update.message.text
    
    # Process text message
    text = update.message.text.lower()
    
    # Example text processing
    if re.search(r'hello|hi|hey', text):
        await update.message.reply_text("Hey there! 👋")
        return

    logger.info(f"Received message from chat_id {chat_id}: {user_message}")

    # Get conversation context
    conversation = conversation_manager.get_conversation(chat_id)
    conversation.add_message("user", user_message)

    try:
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        logger.debug(f"Sending typing indicator to chat_id: {chat_id}")

        try:
            messages = conversation.get_messages()
            logger.debug(f"Sending request to {Config.AI_MODEL} API with messages: {messages}")

            # Get response from the model
            ai_response = model_handler.generate_response(messages)

            if ai_response:
                conversation.add_message("assistant", ai_response)
                logger.info(f"Successfully generated response for chat_id: {chat_id}")
                await update.message.reply_text(ai_response)
            else:
                raise Exception("Failed to generate response")

        except Exception as api_error:
            logger.error(f"API error details: {str(api_error)}", exc_info=True)
            raise

    except Exception as e:
        logger.error(f"Message handling error: {str(e)}", exc_info=True)
        sassy_errors = [
            "Ugh, my brain just broke! 🤪 Give me a sec to fix this mess!",
            "Bruh, what even- 💀 Let me try that again...",
            "Nah fam, that ain't it! Let's try something else? 😩",
            "OMG can't process rn, I'm literally dying! Try again? 😫",
            "That's lowkey not working rn bestie! Hit me up again? 💅"
        ]
        import random
        await update.message.reply_text(random.choice(sassy_errors))