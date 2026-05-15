# scripts/utils.py
import os, re
from unidecode import unidecode
from dotenv import load_dotenv

def slugify(text: str) -> str:
    text = unidecode(text).lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

def load_env() -> str:
    load_dotenv()
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not set in .env")
    return key
