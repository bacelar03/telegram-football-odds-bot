# data_fetcher.py
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
API_BASE_URL = "https://api.football-data.org/v4"

def get_tomorrow_matches():
    """Busca os jogos dos próximos 10 dias"""
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    next_10_days = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    
    url = f"{API_BASE_URL}/matches"
    
    params = {
        "dateFrom": tomorrow,
        "dateTo": next_10_days,
        "status": "SCHEDULED"
    }
    
    headers = {
        'X-Auth-Token': FOOTBALL_DATA_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if 'matches' in data and data['matches']:
            return data['matches']
        else:
            return []
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao buscar dados: {e}")
        return []

def format_matches_for_telegram(matches):
    """Formata os jogos para enviar no Telegram"""
    
    if not matches:
        return "❌ Nenhum jogo disponível nos próximos 10 dias."
    
    message = "⚽ **JOGOS DOS PRÓXIMOS 10 DIAS:**\n\n"
    
    for match in matches[:20]:  # Mostra os primeiros 20
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        
        # Formata a data e hora
        utc_datetime = match['utcDate']
        date_str = utc_datetime.split('T')[0]
        time_str = utc_datetime.split('T')[1][:5]
        
        # Nome da competição
        competition = match['competition']['name']
        
        message += f"📅 {date_str} ⏰ {time_str} - {competition}\n"
        message += f"🏠 {home_team} vs {away_team} 🏃\n\n"
    
    return message

# Teste
if __name__ == "__main__":
    matches = get_tomorrow_matches()
    print(format_matches_for_telegram(matches))