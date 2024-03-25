import re
import anilist
import html, json, traceback
from logging import getLogger
from settings import get_settings
from telegram.constants import ParseMode
from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, CallbackContext, filters, StringCommandHandler


settings = get_settings()
logger = getLogger(__name__)
client = anilist.AsyncClient()


class BotContext(CallbackContext):
    @classmethod
    def from_update( cls, update: object, application: "Application" ) -> "BotContext":
        if isinstance(update, Update):
            return cls(application = application)
        return super().from_update(update, application)


def remove_indents( text: str ) -> str:
    text = "\n".join( [line.strip() for line in text.split("\n")] )
    return text


def get_anime_titles(anime: anilist.types.Anime) -> list[str]:
    romaji = getattr( anime.title, "romaji", "" )
    native = getattr( anime.title, "native", "" )
    english = getattr( anime.title, "english", "" )

    if settings.ANIME_TITLES == "romaji":
        titles = [ romaji, english, native ]
    elif settings.ANIME_TITLES == "japanese":
        titles = [ native, english, romaji ]
    else:
        titles = [ english, romaji, native ]
    return titles


def get_character_names(character: anilist.types.Character) -> list[str]:
    native = getattr( character.name, "native", "" )
    alternative = getattr( character.name, "alternative", "" )

    if settings.ANIME_TITLES == "japanese":
        names = [ native, alternative ]
    else:
        names = [ native, alternative ]
    return names


def get_main_characters(anime: anilist.types.Anime) -> list[anilist.types.Character]:
    characters = []
    for character in anime.characters:
        if character.role == "MAIN":
            characters.append(character)
    return characters



# Bot methods
async def set_bot_commands_menu(application: Application) -> None:
    # Register commands for bot menu
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Get help about this bot"), 
        BotCommand("ping", "Ping the bot"),
        BotCommand("about", "Get information about the bot"),

        BotCommand("latest", "Get information about recently released episodes and anime"),
        BotCommand("anime", "Get information about an anime"),
        BotCommand("character", "Get information about a character"),
        BotCommand("watch", "Watch an episode of an anime"),
        BotCommand("download", "Download episodes of an anime"),
    ]
    await application.bot.set_my_commands(commands)


async def log_in_channels(text: str, context: BotContext, parse_mode = ParseMode.HTML):
    for chat_id in settings.LOG_CHAT_IDS:
        await context.bot.send_message(chat_id = chat_id, text = text, parse_mode = parse_mode)
    

async def send_to_developers(text: str, context: BotContext):
    for chat_id in settings.DEVELOPER_CHAT_IDS:
        await context.bot.send_message(chat_id = chat_id, text = text, parse_mode = ParseMode.HTML)


async def get_help_text( topic: str ):
    return ""



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
    await send_to_developers(text, context)
    

async def handle_message(update: Update, context: BotContext) -> None:
    "Handles messages"
    text = "Use /help to get a list of commands"
    await update.message.reply_text(text)


async def cmd_start(update: Update, context: BotContext) -> None:
    message = update.message
    user = update.effective_user
    text = f"""はじめまして {user.full_name} {user.name}!\n\n
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
    This bot is licensed under the <a href='https://opensource.org/license/mit' title='MIT License'>MIT</a>
    Bot name: {context.bot.username}\nBot handle: {context.bot.name}
    \n<u>Links</u>
    Source code: <a href='https://github.com/Ogoruwa/starter-python-telegram-bot' title='Github repository'>https://github.com/Ogoruwa/starter-python-telegram-bot</a>
    Documentation: Not yet created\n
    Telegram link: <a href='{context.bot.link}' title='Telegram link'>{context.bot.link}</a>"""

    text = remove_indents(text)
    await message.reply_html( text )


async def cmd_ping(update: Update, context: BotContext) -> None:
    message = update.message
    await message.reply_text("pong", reply_to_message_id = message.message_id)


async def cmd_latest(update: Update, context: BotContext):
    text = ""
    text = remove_indents(text)
    await update.message.reply_text(text, reply_to_message_id = update.message.message_id)


async def cmd_anime(update: Update, context: BotContext):
    context.dhah()
    title = context.args[0]
    if title.isnumeric():
        animes = await client.get_anime(title)
    else:
        animes = await client.search_anime(title, 8, 1)
    
    if animes is None:
        text = "Anime not found"
        await update.message.reply_text( text, reply_to_message_id = update.message.message_id )
        return
    animes, pagination = animes

    if len(animes) > 1:
        text = ""
        for anime in animes:
            titles = "\n".join(get_anime_titles(anime))
            text = f"{text}\n\nID: {anime.id}\n{titles}"
    
    else:
        anime = animes[0]
        titles = "\n".join(get_anime_titles(anime)).replace("\n\n", "\n")
        text = f"""
        ID: {anime.id}
        <b>{titles}</b>\n
        \t<i>{anime.description_short}</i>
        Status: {anime.status}
        Genres: {', '.join(anime.genres)}
        Tags: {', '.join(anime.tags)}\n
        Started: {anime.start_date.year}, Ended: {anime.end_date.year}
        Main characters: {', '.join(get_main_characters(anime))}
        Url: <a href='{anime.url}' title='Anilist url'>{anime.url}</a>
        """
    
    text = remove_indents(text)
    await update.message.reply_html(text, reply_to_message_id = update.message.message_id)


async def cmd_character(update: Update, context: BotContext):
    name = context.args[0]
    if name.isnumeric():
        character = await client.get_character(name)
    else:
        character = await client.search_character(name, 8, 1)

    if characters is None:
        text = "Character not found"
        await update.message.reply_text( text, reply_to_message_id = update.message.message_id )
        return
    characters, pagination = characters

    if len(characters) > 1:
        text = ""
        for character in characters:
            titles = get_character_names(character)
            text = f"{text}\n{' / '.join(titles)}"
    
    else:
        character = characters[0]
        names = "\n".join(get_character_names(character)).replace("\n\n", "\n")
        text = f"""
        ID: {character.id}
        <b>{names}</b>
        \t<i>{character.description}</i>
        Gender: {character.gender}
        Role: {character.role}
        Age: {character.age}
        DOB: {character.birth_date.year}
        Url: <a href='{character.url}' title='Anilist url'>{character.url}</a>
        """
    
    text = remove_indents(text)
    await update.message.reply_html(text, reply_to_message_id = update.message.message_id)


async def cmd_watch(update: Update, context: BotContext):
    text = ""
    await update.message.reply_text(text, reply_to_message_id = update.message.message_id)


async def cmd_download(update: Update, context: BotContext):
    text = ""
    await update.message.reply_text(text, reply_to_message_id = update.message.message_id)


async def handle_new_member(update: Update, context: BotContext):
    chat = update.effective_chat
    for member in update.message.new_chat_members:
        if member == context.bot.get_me():
            await log_in_channels( f"Was added to {chat.type} chat: {chat.title} with id: {chat.id}", context )


async def handle_left_member(update: Update, context: BotContext):
    chat = update.effective_chat
    if update.message.left_chat_member == context.bot.get_me():
        await log_in_channels( f"Left {chat.type} chat: {chat.title} with id: {chat.id}", context )



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
    application.add_handler( CommandHandler("latest", cmd_latest) )

    application.add_handler( StringCommandHandler("anime", cmd_anime) )
    application.add_handler( StringCommandHandler("character", cmd_character) )
    application.add_handler( StringCommandHandler("watch", cmd_watch) )
    application.add_handler( StringCommandHandler("download", cmd_download) )

    
    if settings.DEBUG:
        application.add_handler( CommandHandler("raise", raise_bot_exception) )
    
    application.add_handler( MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member) )
    application.add_handler( MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, handle_left_member) )
    application.add_handler( MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message) )

    application.add_error_handler(handle_error)
    
    return application

                                 
