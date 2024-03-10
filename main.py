import os
from pydantic import BaseModel
from environs import Env
from telegram import Update, Bot
from fastapi import FastAPI, Header, HTTPException, Depends, Response


# Read the variable from the environment (or .env file)
env = Env()
env.read_env()

bot_token = env.str("BOT_TOKEN")
secret_token = env.str("SECRET_TOKEN")
webhook_base_url = env.str("WEBHOOK_BASE_URL", False)


app = FastAPI()
bot = Bot(token=bot_token)
webhook_info = None


class TelegramUpdate(BaseModel):
    update_id: int
    message: dict

    
def auth_bot_token(x_telegram_bot_api_secret_token: str = Header(None)) -> str:
    print( f"\n\nSecret token: {secret_token}\nBot secret token: {x_telegram_bot_api_secret_token}\n" )
    if x_telegram_bot_api_secret_token != secret_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return x_telegram_bot_api_secret_token


@app.on_event("startup")
async def handle_startup():
    if webhook_base_url:
        webhook_url = webhook_base_url + "/webhook/"
        await bot.set_webhook( url = webhook_url, secret_token = secret_token)


@app.get("/health/")
async def health_check():
    content = "Health is good"
    return Response( content )


@app.post("/webhook/")
async def handle_webhook(update: TelegramUpdate, token: str = Depends(auth_bot_token)):
    if not webhook_info:
        webhook_info = await bot.get_webhook_info()
        print(webhook_info)
    chat_id = update.message["chat"]["id"]
    text = update.message["text"]
    print("Received message:", update.message)

    if text == "/start":
        with open('hello.gif', 'rb') as photo:
            await bot.send_photo(chat_id=chat_id, photo=photo)
        await bot.send_message(chat_id=chat_id, text="Welcome to Cyclic Starter Python Telegram Bot!")
    else:
        await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text="Yo!")

    return {"ok": True}
