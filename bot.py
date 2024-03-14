from typing import Any
from pydantic import BaseModel
from telegram import BotCommand, ForceReply
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, ContextTypes, ExtBot, JobQueue


class WebhookUpdate(BaseModel):
    update_id: int
    message: dict


class BotContext(CallbackContext[ExtBot, dict, dict, dict]):
    """
    Custom CallbackContext class that makes `user_data` available for updates of type
    `WebhookUpdate`.
    """

    @classmethod
    def from_update(
        cls,
        update: object,
        application: "Application",
    ) -> "BotContext":
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)


# Bot methods
async def set_bot_commands_menu(application: Application[ExtBot[None], Any, Any, Any, Any, JobQueue]) -> None:
    # Register commands for Telegram bot (menu)
    commands = [
        BotCommand( "start", "Start the bot" ),
        BotCommand( "help", "Get help about this bot" ), 
        BotCommand( "ping", "Ping the bot" )
    ]
    try:
        await application.bot.set_my_commands(commands)
    except Exception as e:
        print(f"Can't set commands - {e}")



async def create_bot_application(bot_token: str, secret_token: str, bot_web_url: str):
    """Set up bot application and a web application for handling the incoming requests."""
    context_types = ContextTypes(context=BotContext)

    # Set updater to None so updates are handled by webhook
    application = Application.builder().token(bot_token).updater(None).context_types(context_types).build()

    # Set webhook: url and secret_key
    await application.bot.set_webhook( url = bot_web_url, secret_token = secret_token )

    # Add handlers here
    application.add_handler( CommandHandler("start", cmd_start) )
    application.add_handler( CommandHandler("help", cmd_help) )
    application.add_handler( CommandHandler("ping", cmd_ping) )


    return application



# Create handlers here

async def on_error(update: WebhookUpdate, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles errors"""
    message = "I have encountered an error"
    print("I have an error")
    await update.message.reply_text(message)


async def cmd_start(update: WebhookUpdate, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = f"""<p>Hi {user.mention_html()}!</p>\n
        <p>I am ARIES, Ogo's botler 😄</p>\n
        <p>It is a pleasure to make your acquaintance.</p>\n
        <p>Type /help to get a list of commands</p>"""
    await update.message.reply_html( message, reply_markup = ForceReply(selective=True) )


async def cmd_help(update: WebhookUpdate, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.answer(f"Your ID: {update.from_user.id}")


async def cmd_tag(update: WebhookUpdate, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.send_copy(chat_id=update.chat.id)
    except Exception as e:
        print(f"Can't send message - {e}")
        await update.message.answer("Nice try!")


async def cmd_ping(update: WebhookUpdate, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.answer("pong")
    except Exception as e:
        print(f"Can't send message - {e}")
        await update.message.answer("failed")
