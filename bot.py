from telegram import BotCommand, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes


# Bot methods
async def set_bot_commands_menu(application: Application) -> None:
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


async def create_bot_application(bot_token: str, secret_token: str, bot_web_url: str) -> None:
    """Set up bot application and a web application for handling the incoming requests."""
    context_types = ContextTypes.DEFAULT_TYPES

    # Set updater to None so updates are handled by webhook
    application = Application.builder().token(bot_token).updater(None).context_types(context_types).build()

    # Set webhook: url and secret_key
    await application.bot.set_webhook( url = bot_web_url, secret_token = secret_token )
    await set_bot_commands_menu(application)

    # Add handlers here
    application.add_error_handler(handle_error)
    
    application.add_handler( CommandHandler("start", cmd_start) )
    application.add_handler( CommandHandler("help", cmd_help) )
    application.add_handler( CommandHandler("ping", cmd_ping) )
    
    application.add_handler( MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message) )

    return application



# Create handlers here

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPES) -> None:
    """Handles errors"""
    message = "I have encountered an error"
    print("I have an error")
    await update.message.reply_text(message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPES) -> None:
    "Handles messages"
    message = "I'm not in mood to chat"
    await update.reply_text(message)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPES) -> None:
    user = update.effective_user
    message = f"""<p>Hi {user.mention_html()}!</p>\n
        <p>I am ARIES, Ogo's botler 😄</p>\n
        <p>It is a pleasure to make your acquaintance.</p>\n
        <p>Type /help to get a list of commands</p>"""
    await update.message.reply_html( message, reply_markup = ForceReply(selective=True) )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPES) -> None:
    await update.message.answer(f"Your ID: {update.from_user.id}")


async def cmd_tag(update: Update, context: ContextTypes.DEFAULT_TYPES) -> None:
    try:
        await update.send_copy(chat_id=update.chat.id)
    except Exception as e:
        print(f"Can't send message - {e}")
        await update.message.answer("Nice try!")


async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPES) -> None:
    try:
        await update.message.answer("pong")
    except Exception as e:
        print(f"Can't send message - {e}")
        await update.message.answer("failed")

