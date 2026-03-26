# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Configurações
DEBUG = True
BOT_NAME = "Football Odds Bot"