import os


class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    PORT = os.getenv("TELEGRAM_BOT_PORT", 5000)
    HOST = os.getenv("WEB_HOOK_HOST")
    TELEGRAM_API = "https://api.telegram.org"
    TELEGRAM_CORE_API_HASH = os.getenv("TELEGRAM_CORE_API_HASH")
    TELEGRAM_CORE_API_ID = os.getenv("TELEGRAM_CORE_API_ID")
