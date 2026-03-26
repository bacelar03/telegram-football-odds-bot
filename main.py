# main.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from data_fetcher import get_tomorrow_matches, format_matches_for_telegram

# Carregar variáveis de .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    await update.message.reply_text(
        "🤖 Olá! Sou o Football Odds Bot!\n"
        "Estou em desenvolvimento...\n"
        "/help - Ver comandos disponíveis"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    await update.message.reply_text(
        "📋 Comandos disponíveis:\n"
        "/start - Iniciar\n"
        "/tomorrow - Jogos de amanhã\n"
        "/odds - Melhores odds\n"
    )

async def tomorrow_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /tomorrow - Mostra jogos de amanhã"""
    matches = get_tomorrow_matches()
    message = format_matches_for_telegram(matches)
    await update.message.reply_text(message, parse_mode="Markdown")

def main():
    """Iniciar o bot"""
    application = Application.builder().token(TOKEN).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tomorrow", tomorrow_matches))
    
    # Iniciar polling (escuta mensagens)
    print("✅ Bot iniciado! Pressiona Ctrl+C para parar.")
    application.run_polling()

if __name__ == "__main__":
    main()