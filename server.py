import logging
import uvicorn
from main import app
from settings import get_settings

settings = get_settings()
logging.basicConfig( format = "%(asctime)s - %(name)s -%(levelname)s - %(message)s", level = settings.LOG_LEVEL )

if __name__ == "__main__":
    uvicorn.run(app, host = settings.HOST, port = settings.PORT, use_colors = True, log_level = settings.LOG_LEVEL)

