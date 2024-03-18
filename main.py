import logging
from environs import Env
from routes import router
from telegram import Update
from bot import create_bot_application
from contextlib import asynccontextmanager
from fastapi import Depends, Header, HTTPException, FastAPI, Request


env = Env()
env.read_env()
logger = logging.getLogger(__name__)

DEBUG = env.bool("DEBUG", False)

# Enable logging and set logging level for httpx to set whether all GET and POST requests get loggged
logging.basicConfig( format = "%(asctime)s - %(name)s -%(levelname)s - %(message)s", level = logging.INFO )
logging.getLogger( "httpx" ).setLevel( logging.INFO if DEBUG else logging.WARNING )

bot_token = env.str("BOT_TOKEN")
bot_web_url = env.str("BOT_WEB_URL")
secret_token = env.str("SECRET_TOKEN")
webhook_url = env.str("WEBHOOK_URL", "/webhook/")


def auth_bot_token(x_telegram_bot_api_secret_token: str = Header(None)) -> str:
    if x_telegram_bot_api_secret_token != secret_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return x_telegram_bot_api_secret_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    application = await create_bot_application( bot_token, secret_token, bot_web_url+webhook_url )

    @router.post(webhook_url, status_code=204)
    async def webhook(request: Request, token: str = Depends(auth_bot_token)) -> None:
        """Handle incoming updates by putting them into the `update_queue`"""
        update_json = await request.json()
        update = Update.de_json( update_json, application.bot )
        await application.update_queue.put(update)

    app.include_router(router)
    async with application:
        # Runs when app starts
        logger.info(f"\n🚀 Bot starting up ...\nDebugging is {'enabled' if DEBUG else 'disabled'}")
        await application.start()
        
        yield
        
        # Runs after app shuts down
        logger.info("\n⛔ Bot shutting down ...\n")
        await application.stop()


app = FastAPI( title = "BotFastAPI", description = "A webhook api for a telegram bot", lifespan = lifespan )
