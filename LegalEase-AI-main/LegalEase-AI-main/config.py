import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# API Configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
BACKEND_URL = f"http://{HOST}:{PORT}"

# Asset Paths
IMAGE_DIR = BASE_DIR / "images"
LOGO_PATH = IMAGE_DIR / "logo.png"

# Create images folder if missing
IMAGE_DIR.mkdir(parents=True, exist_ok=True)