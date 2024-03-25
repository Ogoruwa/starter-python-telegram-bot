import uvicorn
from main import app

PORT = 8181
HOST = "0.0.0.0"

if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port = 8181, use_colors = True )

