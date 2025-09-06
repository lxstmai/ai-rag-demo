"""
RAG system configuration
"""
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# API keys
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# model settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# ChromaDB settings
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "demo_collection")

# RAG settings
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "300"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# server settings
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# check required parameters
if not DEEPSEEK_API_KEY and not OPENAI_API_KEY:
    print("⚠️  Warning: No API key set for LLM")
    print("   Set DEEPSEEK_API_KEY or OPENAI_API_KEY in .env file")
