import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_APROVACAO_STR = os.getenv("CHAT_APROVACAO")
GECKO_API_KEY = os.getenv("GECKO_API_KEY")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN não definida no .env")

if not CHAT_APROVACAO_STR:
    raise ValueError("CHAT_APROVACAO não definida no .env")

if not GECKO_API_KEY:
    raise ValueError("GECKO_API_KEY não definida no .env")

try:
    CHAT_APROVACAO = int(CHAT_APROVACAO_STR)
except (ValueError, TypeError):
    raise ValueError(f"CHAT_APROVACAO deve ser um número inteiro, recebeu: {CHAT_APROVACAO_STR}")