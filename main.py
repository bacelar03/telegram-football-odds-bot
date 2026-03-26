# main.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from data_fetcher import get_tomorrow_matches, format_matches_for_telegram, sync_matches_to_database
from database import init_database
from ml_model import predictor

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
        "/odds - Previsão de odds\n"
    )

async def tomorrow_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /tomorrow - Mostra jogos de amanhã"""
    matches = get_tomorrow_matches()
    message = format_matches_for_telegram(matches)
    await update.message.reply_text(message, parse_mode="Markdown")

async def predict_odds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /odds - Mostra previsões de odds"""
    matches = get_tomorrow_matches()
    
    if not matches:
        await update.message.reply_text("❌ Nenhum jogo disponível.")
        return
    
    message = "🎯 **PREVISÃO DE ODDS (Próximos 10 dias):**\n\n"
    
    for match in matches[:10]:  # Mostra os primeiros 10
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        
        # Formata a data e hora
        utc_datetime = match['utcDate']
        date_str = utc_datetime.split('T')[0]
        time_str = utc_datetime.split('T')[1][:5]
        
        # Prever odds
        odds = predictor.predict_odds(home_team, away_team)
        
        message += f"📅 {date_str} ⏰ {time_str}\n"
        message += f"🏠 {home_team} vs {away_team} 🏃\n"
        message += f"💰 **Odds:** 1️⃣ {odds['home_win']} | 🤝 {odds['draw']} | 2️⃣ {odds['away_win']}\n\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")

def main():
    """Iniciar o bot"""
    application = Application.builder().token(TOKEN).build()
    
    # Sincronizar dados históricos e treinar modelo
    print("📊 Sincronizando dados históricos...")
    sync_matches_to_database()
    
    print("🤖 Treinando modelo de IA...")
    predictor.train_model()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tomorrow", tomorrow_matches))
    application.add_handler(CommandHandler("odds", predict_odds))
    
    # Iniciar polling (escuta mensagens)
    print("✅ Bot iniciado! Pressiona Ctrl+C para parar.")
    application.run_polling()

if __name__ == "__main__":
    main()