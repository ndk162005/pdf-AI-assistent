import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
PROJECT_ROOT = Path(__file__).resolve().parent

# Load environment variables from .env if present
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# Directories
UPLOAD_DIR = PROJECT_ROOT / os.getenv("UPLOAD_DIR", "uploads")
DATA_DIR = PROJECT_ROOT / "data"

CHATBOT_DATA_DIR = DATA_DIR / "chatbot"
CHATBOT_DB_PATH = CHATBOT_DATA_DIR / os.getenv("CHATBOT_DB_NAME", "chatbot.db")
CHATBOT_VECTOR_DB_PATH = CHATBOT_DATA_DIR / "vector_db"

SEMANTIC_DATA_DIR = DATA_DIR / "semantic_search"
SEMANTIC_DB_PATH = SEMANTIC_DATA_DIR / os.getenv("SEMANTIC_DB_NAME", "semantic_search.db")
SEMANTIC_VECTOR_DB_PATH = SEMANTIC_DATA_DIR / "vector_db"

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "180.0"))

# Processing & Retrieval Parameters
TOP_K = int(os.getenv("TOP_K", "5"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# Ensure runtime directories exist
def ensure_directories():
    directories = [
        UPLOAD_DIR,
        CHATBOT_DATA_DIR,
        CHATBOT_VECTOR_DB_PATH,
        SEMANTIC_DATA_DIR,
        SEMANTIC_VECTOR_DB_PATH,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

ensure_directories()
