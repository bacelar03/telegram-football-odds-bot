# main.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from data_fetcher import get_tomorrow_matches, format_matches_for_telegram, sync_matches_to_database
from database import init_database, get_team_stats, get_all_teams_ranking
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
        "/stats <time> - Estatísticas de um time\n"
        "/best - Melhores odds\n"
        "/ranking - Top 10 times\n"
        "/compare <time1> vs <time2> - Comparar times\n"
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

async def team_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats <time> - Mostra estatísticas de um time"""
    
    if not context.args:
        await update.message.reply_text(
            "❌ Uso: `/stats Nome_do_Time`\n"
            "Exemplo: `/stats Flamengo`",
            parse_mode="Markdown"
        )
        return
    
    team_name = " ".join(context.args)
    stats = get_team_stats(team_name)
    
    if not stats['home'] or not stats['away']:
        await update.message.reply_text(f"❌ Nenhum histórico encontrado para {team_name}")
        return
    
    home_gf, home_ga = stats['home']
    away_gf, away_ga = stats['away']
    
    message = f"📊 **ESTATÍSTICAS - {team_name}**\n\n"
    message += f"🏠 **Em Casa:**\n"
    message += f"  Gols a Favor: {home_gf:.2f}\n"
    message += f"  Gols contra: {home_ga:.2f}\n"
    message += f"  Saldo: {home_gf - home_ga:+.2f}\n\n"
    message += f"🏃 **Fora de Casa:**\n"
    message += f"  Gols a Favor: {away_gf:.2f}\n"
    message += f"  Gols contra: {away_ga:.2f}\n"
    message += f"  Saldo: {away_gf - away_ga:+.2f}\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def best_odds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /best - Mostra as melhores odds do momento"""
    matches = get_tomorrow_matches()
    
    if not matches:
        await update.message.reply_text("❌ Nenhum jogo disponível.")
        return
    
    # Calcular odds para todos os jogos
    odds_list = []
    
    for match in matches:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        odds = predictor.predict_odds(home_team, away_team)
        
        utc_datetime = match['utcDate']
        date_str = utc_datetime.split('T')[0]
        time_str = utc_datetime.split('T')[1][:5]
        
        odds_list.append({
            'home': home_team,
            'away': away_team,
            'odds': odds,
            'date': date_str,
            'time': time_str
        })
    
    # Encontrar as melhores odds (maiores)
    best_home = max(odds_list, key=lambda x: x['odds']['home_win'])
    best_draw = max(odds_list, key=lambda x: x['odds']['draw'])
    best_away = max(odds_list, key=lambda x: x['odds']['away_win'])
    
    message = "🏆 **MELHORES ODDS DO MOMENTO:**\n\n"
    
    message += f"🥇 **Maior Odd - Vitória Mandante:**\n"
    message += f"{best_home['home']} vs {best_home['away']}\n"
    message += f"Odd: {best_home['odds']['home_win']} ({best_home['date']} {best_home['time']})\n\n"
    
    message += f"🥈 **Maior Odd - Empate:**\n"
    message += f"{best_draw['home']} vs {best_draw['away']}\n"
    message += f"Odd: {best_draw['odds']['draw']} ({best_draw['date']} {best_draw['time']})\n\n"
    
    message += f"🥉 **Maior Odd - Vitória Visitante:**\n"
    message += f"{best_away['home']} vs {best_away['away']}\n"
    message += f"Odd: {best_away['odds']['away_win']} ({best_away['date']} {best_away['time']})\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ranking - Mostra o ranking dos 10 times mais fortes"""
    
    teams = get_all_teams_ranking()
    
    if not teams:
        await update.message.reply_text("❌ Sem dados para ranking.")
        return
    
    message = "🏆 **TOP 10 TIMES MAIS FORTES:**\n\n"
    
    for i, team in enumerate(teams[:10], 1):
        message += f"{i}. {team['name']}\n"
        message += f"   Força: {team['strength']:+.2f}\n"
        message += f"   Casa: {team['home_gf']:.1f}GF - {team['home_ga']:.1f}GA\n"
        message += f"   Fora: {team['away_gf']:.1f}GF - {team['away_ga']:.1f}GA\n\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def compare_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /compare <time1> vs <time2> - Compara dois times"""
    
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "❌ Uso: `/compare Time1 vs Time2`\n"
            "Exemplo: `/compare Flamengo vs Botafogo`",
            parse_mode="Markdown"
        )
        return
    
    # Procurar por "vs" (case-insensitive)
    args_lower = [arg.lower() for arg in context.args]
    
    if "vs" not in args_lower:
        await update.message.reply_text(
            "❌ Uso: `/compare Time1 vs Time2`\n"
            "Exemplo: `/compare Flamengo vs Botafogo`",
            parse_mode="Markdown"
        )
        return
    
    # Encontrar índice de "vs"
    vs_index = args_lower.index("vs")
    
    team1_args = context.args[:vs_index]
    team2_args = context.args[vs_index + 1:]
    
    team1 = " ".join(team1_args)
    team2 = " ".join(team2_args)
    
    if not team1 or not team2:
        await update.message.reply_text(
            "❌ Uso: `/compare Time1 vs Time2`\n"
            "Exemplo: `/compare Flamengo vs Botafogo`",
            parse_mode="Markdown"
        )
        return
    
    stats1 = get_team_stats(team1)
    stats2 = get_team_stats(team2)
    
    if not stats1['home'] or not stats2['home']:
        await update.message.reply_text(f"❌ Nenhum histórico encontrado para um dos times.")
        return
    
    h1_gf, h1_ga = stats1['home']
    a1_gf, a1_ga = stats1['away']
    h2_gf, h2_ga = stats2['home']
    a2_gf, a2_ga = stats2['away']
    
    strength1 = ((h1_gf - h1_ga) + (a1_gf - a1_ga)) / 2
    strength2 = ((h2_gf - h2_ga) + (a2_gf - a2_ga)) / 2
    
    message = f"⚔️ **COMPARAÇÃO: {team1} vs {team2}**\n\n"
    
    message += f"📊 **{team1}**\n"
    message += f"  Força Total: {strength1:+.2f}\n"
    message += f"  Média Gols (Casa): {h1_gf:.1f}\n"
    message += f"  Média Gols (Fora): {a1_gf:.1f}\n\n"
    
    message += f"📊 **{team2}**\n"
    message += f"  Força Total: {strength2:+.2f}\n"
    message += f"  Média Gols (Casa): {h2_gf:.1f}\n"
    message += f"  Média Gols (Fora): {a2_gf:.1f}\n\n"
    
    if strength1 > strength2:
        message += f"🏆 **{team1} é mais forte!**"
    elif strength2 > strength1:
        message += f"🏆 **{team2} é mais forte!**"
    else:
        message += f"⚖️ **Equipas equilibradas!**"
    
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
    application.add_handler(CommandHandler("stats", team_stats))
    application.add_handler(CommandHandler("best", best_odds))
    application.add_handler(CommandHandler("ranking", ranking))
    application.add_handler(CommandHandler("compare", compare_teams))
    
    # Iniciar polling (escuta mensagens)
    print("✅ Bot iniciado! Pressiona Ctrl+C para parar.")
    application.run_polling()

if __name__ == "__main__":
    main()