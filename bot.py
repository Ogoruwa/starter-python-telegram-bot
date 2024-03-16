from environs import Env
from telegram.constants import ParseMode
from telegram import BotCommand, ForceReply, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, CallbackContext

env = Env()
env.read_env()
DEVELOPER_CHAT_IDS = env.list("DEVELOPER_CHAT_IDS")


class BotContext(CallbackContext):
    """ Custom CallbackContext class that makes `user_data` available for updates of type `WebhookUpdate` """

    @classmethod
    def from_update( cls, update: object, application: "Application" ) -> "BotContext":
        if isinstance(update, WebhookUpdate):
            return cls(application = application, user_id = update.user_id)
        return super().from_update(update, application)


# Bot methods
async def set_bot_commands_menu(application: Application) -> None:
    # Register commands for bot menu
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
    context_types = ContextTypes(context = BotContext )

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

async def handle_error(update: Update, context: BotContext) -> None:
    """Log the error and send a message to notify the developer."""
    # Log the error first so it can be seen even if something breaks.
    print("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # TODO: Add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    for chat_id in DEVELOPER_CHAT_IDS:
        await context.bot.send_message( chat_id = chat_id, text=message, parse_mode = ParseMode.HTML )
    

async def handle_message(update: Update, context: BotContext) -> None:
    "Handles messages"
    message = "I'm not in mood to chat"
    await update.reply_text(message)


async def cmd_start(update: Update, context: BotContext) -> None:
    user = update.effective_user
    message = f"""<p>Hi {user.mention_html()}!</p>\n
        <p>I am ARIES, Ogo's botler 😄</p>\n
        <p>It is a pleasure to make your acquaintance.</p>\n
        <p>Type /help to get a list of commands</p>"""
    await update.message.reply_html( message, reply_markup = ForceReply(selective=True) )


async def cmd_help(update: Update, context: BotContext) -> None:
    await update.message.answer(f"Your ID: {update.from_user.id}")


async def cmd_tag(update: Update, context: BotContext) -> None:
    try:
        await update.send_copy(chat_id=update.chat.id)
    except Exception as e:
        print(f"Can't send message - {e}")
        await update.message.answer("Nice try!")


async def cmd_ping(update: Update, context: BotContext) -> None:
    try:
        await update.message.answer("pong")
    except Exception as e:
        print(f"Can't send message - {e}")
        await update.message.answer("failed")

