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

def sync_matches_to_database():
    """Sincroniza jogos finalizados com o banco de dados"""
    from database import save_match
    
    url = f"{API_BASE_URL}/matches"
    
    headers = {
        'X-Auth-Token': FOOTBALL_DATA_API_KEY
    }
    
    total_synced = 0
    
    # Buscar em períodos de 10 dias
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    current_start = start_date
    
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=10), end_date)
        
        start_str = current_start.strftime("%Y-%m-%d")
        end_str = current_end.strftime("%Y-%m-%d")
        
        params = {
            "dateFrom": start_str,
            "dateTo": end_str,
            "status": "FINISHED"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if 'matches' in data:
                for match in data['matches']:
                    match_data = {
                        'match_id': match['id'],
                        'home_team': match['homeTeam']['name'],
                        'away_team': match['awayTeam']['name'],
                        'home_goals': match['score']['fullTime']['home'],
                        'away_goals': match['score']['fullTime']['away'],
                        'date': match['utcDate'].split('T')[0],
                        'competition': match['competition']['name'],
                        'status': match['status']
                    }
                    if save_match(match_data):
                        total_synced += 1
        
        except Exception as e:
            print(f"⚠️ Erro ao buscar de {start_str} a {end_str}: {e}")
        
        current_start = current_end
    
    if total_synced > 0:
        print(f"✅ {total_synced} novos jogos sincronizados!")
    else:
        print("ℹ️ Sem novos jogos para sincronizar.")
    
    return total_synced

# Teste
if __name__ == "__main__":
    matches = get_tomorrow_matches()
    print(format_matches_for_telegram(matches))
    