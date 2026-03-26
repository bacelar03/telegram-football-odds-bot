# main.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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

def main():
    """Iniciar o bot"""
    application = Application.builder().token(TOKEN).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Iniciar polling (escuta mensagens)
    print("✅ Bot iniciado! Pressiona Ctrl+C para parar.")
    application.run_polling()

if __name__ == "__main__":
    main()