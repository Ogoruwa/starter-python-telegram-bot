import html, json, traceback
from logging import getLogger
from settings import get_settings
from telegram import BotCommand, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, CallbackContext, filters


settings = get_settings()
logger = getLogger(__name__)


class BotContext(CallbackContext):
    @classmethod
    def from_update( cls, update: object, application: "Application" ) -> "BotContext":
        if isinstance(update, Update):
            return cls(application = application)
        return super().from_update(update, application)


def remove_indents( text: str ):
    text = "\n".join( [line.strip() for line in text.split("\n")] )
    return text


# Bot methods
async def set_bot_commands_menu(application: Application) -> None:
    # Register commands for bot menu
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Get help about this bot"), 
        BotCommand("ping", "Ping the bot"),
        BotCommand("about", "Get information about the bot")
    ]
    try:
        await application.bot.set_my_commands(commands)
    except Exception as e:
        print(f"Can't set commands - {e}")


# Create handlers here

async def handle_error(update: Update, context: BotContext) -> None:
    """Log the error and send a message to notify the developer."""
    # Log the error first so it can be seen even if something breaks.
    logger.error("Exception while handling an update:", exc_info = context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # TODO: Add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    text = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent = 2, ensure_ascii = False))}</pre>\n\n"
        f"<pre><u>context.chat_data</u> = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre><u>context.user_data</u> = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    for chat_id in settings.DEVELOPER_CHAT_IDS:
        await context.bot.send_message(chat_id = chat_id, text = text, parse_mode = ParseMode.HTML)
    

async def handle_message(update: Update, context: BotContext) -> None:
    "Handles messages"
    message = update.message
    text = "Save your messages for later, the now is for anime 🔥"
    await message.reply_text(text)


async def cmd_start(update: Update, context: BotContext) -> None:
    message = update.message
    user = update.effective_user
    text = f"""はじめまして {user.full_name} {user.name}!\n
        わたしはアリエスです (I am ARIES).
        Use the help command (/help) to open the guide."""
    
    text = remove_indents(text)
    await message.reply_text(text)


async def cmd_help(update: Update, context: BotContext) -> None:
    message = update.message
    text = f"""I am a bot designed to take care of your anime needs.
        Please, pick a topic to get more information."""
    text = remove_indents(text)
    await message.reply_text( text )


async def cmd_about(update: Update, context: BotContext) -> None:
    message = update.message
    text = f"""<b>Copyright 2024 Ogoruwa</b>
    This bot is licensed under the MIT (https://opensource.org/license/mit)
    Bot name: {context.bot.username}\nBot handle: {context.bot.name}
    \n<i>Links</i>
    Source code: GitHub (https://github.com/Ogoruwa/starter-python-telegram-bot)
    Documentation: Not yet created\n
    Telegram link: {context.bot.link}"""

    text = remove_indents(text)
    message.reply_html( text )


async def cmd_ping(update: Update, context: BotContext) -> None:
    message = update.message
    try:
        await message.reply_text("pong", reply_to_message_id = message.message_id)
    except Exception as e:
        print(f"Can't send message - {e}")
        await message.reply_text("failed", reply_to_message_id = message.message_id)


if settings.DEBUG:
    async def raise_bot_exception(update: Update, context: BotContext):
        context.bot.this_method_does_not_exist()

# Function for creating the bot application 
async def create_bot_application(bot_token: str, secret_token: str, bot_web_url: str) -> None:
    """Set up bot application and a web application for handling the incoming requests."""
    context_types = ContextTypes(context = BotContext )

    # Set updater to None so updates are handled by webhook
    application = Application.builder().token(bot_token).updater(None).context_types(context_types).build()

    # Set webhook: url and secret_key
    await application.bot.set_webhook(url = bot_web_url, secret_token = secret_token)
    await set_bot_commands_menu(application)

    # Add handlers here
    application.add_handler( CommandHandler("start", cmd_start) )
    application.add_handler( CommandHandler("help", cmd_help) )
    application.add_handler( CommandHandler("ping", cmd_ping) )
    application.add_handler( CommandHandler("about", cmd_about) )
    
    if settings.DEBUG:
        application.add_handler( CommandHandler("raise", raise_bot_exception) )
    
    application.add_handler( MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message) )
    application.add_error_handler(handle_error)
    
    return application

                                 
