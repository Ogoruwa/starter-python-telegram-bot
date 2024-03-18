from environs import Env
from logging import INFO, WARNING

env = Env()
env.read_env()


class Settings:
    PORT = 8181
    HOST = "0.0.0.0"
    DEBUG = env.bool("DEBUG", False)
    LOG_LEVEL = INFO if DEBUG else WARNING

    BOT_TOKEN = env.str("BOT_TOKEN")
    SECRET_TOKEN = env.str("SECRET_TOKEN")
    
    BOT_WEB_URL = env.str("BOT_WEB_URL")
    HEALTH_URL = env.str("HEALTH_URL", "/health/")
    WEBHOOK_URL = env.str("WEBHOOK_URL", "/webhook/")

    LOG_CHANNEL_IDS = [ i.strip() for i in env.list("LOG_CHANNEL_IDS") ]
    DEVELOPER_CHAT_IDS = [ i.strip() for i in env.list("DEVELOPER_CHAT_IDS") ]


def get_settings():
    return Settings()
