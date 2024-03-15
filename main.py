from environs import Env
from routes import router
from telegram import Update
from contextlib import asynccontextmanager
from bot import create_bot_application, WebhookUpdate
from fastapi import Depends, FastAPI, Header, HTTPException, Response


env = Env()
env.read_env()

bot_token = env.str("BOT_TOKEN")
bot_web_url = env.str("BOT_WEB_URL")
secret_token = env.str("SECRET_TOKEN")


def auth_bot_token(x_telegram_bot_api_secret_token: str = Header(None)) -> str:
    if x_telegram_bot_api_secret_token != secret_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return x_telegram_bot_api_secret_token


@router.post("/webhook/")
async def webhook(update: WebhookUpdate, token: str = Depends(auth_bot_token)) -> Response:
    """Handle incoming Telegram updates by putting them into the `update_queue`"""
    update = Update.de_json( update, update.bot ) 
    await application.update_queue.put(update)
    return Response()



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with application:
        # Runs when app starts
        print("\n🚀 Bot starting up ...\n")
        await application.start()
        
        yield
        
        # Runs after app shuts down
        print("\n⛔ Bot shutting down ...\n")
        await application.stop()


application = create_bot_application( bot_token, secret_token, bot_web_url )
app = FastAPI( title = "BotFastAPI", description = "An API for a telegram bot", lifespan = lifespan )
app.include_router(router)
