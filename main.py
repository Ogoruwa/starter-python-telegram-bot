import os, sys
from routes import router
from telegram import Update
from logging import getLogger
from settings import get_settings
from bot import create_bot_application
from contextlib import asynccontextmanager
from fastapi import Depends, Header, HTTPException, FastAPI, Request


settings = get_settings()
logger = getLogger(__name__)


def auth_bot_token(x_telegram_bot_api_secret_token: str = Header(None)) -> str:
    if x_telegram_bot_api_secret_token != settings.SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return x_telegram_bot_api_secret_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    application = await create_bot_application( settings.BOT_TOKEN, settings.SECRET_TOKEN, settings.BOT_WEB_URL+settings.WEBHOOK_URL )

    @router.post(settings.WEBHOOK_URL, status_code=204)
    async def webhook(request: Request, token: str = Depends(auth_bot_token)) -> None:
        """Handle incoming updates by putting them into the `update_queue`"""
        update_json = await request.json()
        update = Update.de_json( update_json, application.bot )
        await application.update_queue.put(update)

    app.include_router(router)
    async with application:
        # Runs when app starts
        logger.info(f"\n🚀 Bot starting up ...\nDebugging is {'enabled' if settings.DEBUG else 'disabled'}")
        await application.start()
        
        yield
        
        # Runs after app shuts down
        logger.info("\n⛔ Bot shutting down ...\n")
        await application.stop()
        
        if application.bot_data.get("restart", False):
            os.execl(sys.executable, sys.executable, *sys.argv)


app = FastAPI( title = "BotFastAPI", description = "A webhook api for a telegram bot", lifespan = lifespan )
