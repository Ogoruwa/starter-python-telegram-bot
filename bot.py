from environs import Env
from telegram.constants import ParseMode
from telegram import BotCommand, ForceReply, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, CallbackContext, filters

env = Env()
env.read_env()
DEVELOPER_CHAT_IDS = env.list("DEVELOPER_CHAT_IDS")


class BotContext(CallbackContext):
    """ Custom CallbackContext class that makes `user_data` available for updates of type `WebhookUpdate` """

    @classmethod
    def from_update( cls, update: object, application: "Application" ) -> "BotContext":
        if isinstance(update, Update):
            return cls(application = application)
        return super().from_update(update, application)


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
    print("Exception while handling an update:", exc_info = context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # TODO: Add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    text = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent = 2, ensure_ascii = False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    for chat_id in DEVELOPER_CHAT_IDS:
        await context.bot.send_message(chat_id = chat_id, text = text, parse_mode = ParseMode.HTML)
    

async def handle_message(update: Update, context: BotContext) -> None:
    "Handles messages"
    message = update.message
    text = "Save your messages for later, the now is for anime 🔥"
    await message.reply_text(text)


async def cmd_start(update: Update, context: BotContext) -> None:
    user = update.effective_user
    message = update.message
    text = f"""<pre>こんにちは！ {user.mention_html()} @{message.from_user.id}!</pre>\n
        <pre>わたしはアリエスです, I am ARIES. Hajime mashite</pre>\n
        <pre>Type /help to open the guide</pre>"""
    await message.reply_html(text, reply_markup = ForceReply(selective = True))


async def cmd_help(update: Update, context: BotContext) -> None:
    message = update.message
    text = f"""<pre>I am a bot designed to take care of your anime needs</pre>\n
        <pre>Please, pick a topic to get more information</pre>"""
    await message.reply_html( text )


async def cmd_about(update: Update, context: BotContext) -> None:
    message = update.message
    text = f"""<pre><b>©️ 2024 Ogoruwa</b></pre>\n
    <pre>This bot is licensed under the <a href='https://opensource.org/license/mit'>MIT</a></pre>\n
    <pre> Name: {context.bot.username}, Handle: {context.bot.name}</pre>\n\n
    <pre><i>Links</i></pre>\n
    <pre>Source code: https://github.com/Ogoruwa/starter-python-telegram-bot<\pre>\n
    <pre>Documentation: TODO</pre>\n
    <pre>Telegram link: {context.bot.link}</pre>"""
    message.reply_html( text )


async def cmd_ping(update: Update, context: BotContext) -> None:
    message = update.message
    try:
        await message.reply_text("pong", reply_to_message_id = message.message_id)
    except Exception as e:
        print(f"Can't send message - {e}")
        await message.reply_text("failed", reply_to_message_id = message.message_id)



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
    
    application.add_handler( MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message) )

    application.add_error_handler(handle_error)
    
    return application

                                 
