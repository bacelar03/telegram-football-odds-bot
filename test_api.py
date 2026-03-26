# test_api.py
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

load_dotenv()

FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
API_BASE_URL = "https://api.football-data.org/v4"

print(f"🔑 API Key: {FOOTBALL_DATA_API_KEY[:10] if FOOTBALL_DATA_API_KEY else 'NÃO ENCONTRADA'}...")

# Testa com data de hoje até 30 dias atrás
start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

print(f"📅 Buscando de {start_date} até {end_date}")

url = f"{API_BASE_URL}/matches"

params = {
    "dateFrom": start_date,
    "dateTo": end_date
}

headers = {
    'X-Auth-Token': FOOTBALL_DATA_API_KEY
}

try:
    response = requests.get(url, params=params, headers=headers)
    print(f"📊 Status: {response.status_code}")
    
    data = response.json()
    
    if 'matches' in data:
        print(f"✅ Total de jogos encontrados: {len(data['matches'])}")
        
        if data['matches']:
            print("\n🎯 Primeiros 5 jogos:")
            for match in data['matches'][:5]:
                date = match['utcDate'].split('T')[0]
                home = match['homeTeam']['name']
                away = match['awayTeam']['name']
                status = match['status']
                print(f"  {date} | {home} vs {away} | Status: {status}")
    else:
        print(f"❌ Resposta inesperada: {data}")
        
except Exception as e:
    print(f"❌ Erro: {e}")