# database.py
import sqlite3
import os
from datetime import datetime

DB_PATH = "football_matches.db"

def init_database():
    """Inicializa o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de jogos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER UNIQUE,
            home_team TEXT,
            away_team TEXT,
            home_goals INTEGER,
            away_goals INTEGER,
            date TEXT,
            competition TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de previsões
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            home_win_odds REAL,
            draw_odds REAL,
            away_win_odds REAL,
            predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(match_id) REFERENCES matches(match_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database inicializado!")

def save_match(match_data):
    """Salva um jogo no banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO matches 
            (match_id, home_team, away_team, home_goals, away_goals, date, competition, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_data['match_id'],
            match_data['home_team'],
            match_data['away_team'],
            match_data.get('home_goals', None),
            match_data.get('away_goals', None),
            match_data['date'],
            match_data['competition'],
            match_data['status']
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Jogo já existe
        return False
    finally:
        conn.close()

def get_all_finished_matches():
    """Retorna todos os jogos finalizados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM matches WHERE status = 'FINISHED'
    ''')
    
    matches = cursor.fetchall()
    conn.close()
    
    return matches

def get_team_stats(team_name):
    """Retorna estatísticas de um time"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Jogos como mandante
    cursor.execute('''
        SELECT AVG(home_goals) as avg_goals_for, AVG(away_goals) as avg_goals_against
        FROM matches 
        WHERE home_team = ? AND status = 'FINISHED'
    ''', (team_name,))
    
    home_stats = cursor.fetchone()
    
    # Jogos como visitante
    cursor.execute('''
        SELECT AVG(away_goals) as avg_goals_for, AVG(home_goals) as avg_goals_against
        FROM matches 
        WHERE away_team = ? AND status = 'FINISHED'
    ''', (team_name,))
    
    away_stats = cursor.fetchone()
    conn.close()
    
    return {
        'home': home_stats,
        'away': away_stats
    }

def save_prediction(match_id, odds):
    """Salva uma previsão"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO predictions 
        (match_id, home_win_odds, draw_odds, away_win_odds)
        VALUES (?, ?, ?, ?)
    ''', (match_id, odds['home_win'], odds['draw'], odds['away_win']))
    
    conn.commit()
    conn.close()

# Inicializar ao importar
if not os.path.exists(DB_PATH):
    init_database()