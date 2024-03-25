import logging
import uvicorn
from main import app
from settings import get_settings

settings = get_settings()

# Enable logging and set higher logging level for httpx to avoid all GET and POST requests being loggged
logging.getLogger( "httpx" ).setLevel( logging.WARNING )
logging.basicConfig( format = "%(asctime)s - %(name)s -%(levelname)s - %(message)s", level = settings.LOG_LEVEL )

if __name__ == "__main__":
    uvicorn.run(app, host = settings.HOST, port = settings.PORT, use_colors = True, log_level = settings.LOG_LEVEL)

