# ml_model.py
import numpy as np
from database import get_team_stats, get_all_finished_matches
from sklearn.linear_model import LinearRegression
import pickle
import os

MODEL_PATH = "odds_model.pkl"

class OddsPredictor:
    """Modelo para prever odds de jogos"""
    
    def __init__(self):
        self.model = None
        self.load_model()
    
    def train_model(self):
        """Treina o modelo com dados históricos"""
        
        matches = get_all_finished_matches()
        
        if len(matches) < 5:
            print("⚠️ Poucos dados para treinar. Usando previsões simples.")
            return False
        
        X = []  # Features (características)
        y = []  # Target (resultado)
        
        for match in matches:
            # match tem: (id, match_id, home_team, away_team, home_goals, away_goals, date, competition, status, created_at)
            match_id = match[1]
            home_team = match[2]
            away_team = match[3]
            home_goals = match[4]
            away_goals = match[5]
            
            home_stats = get_team_stats(home_team)
            away_stats = get_team_stats(away_team)
            
            # Features: média de gols casa, média de gols fora, etc
            if home_stats['home'] and away_stats['away']:
                home_avg_for = home_stats['home'][0] or 0
                home_avg_against = home_stats['home'][1] or 0
                away_avg_for = away_stats['away'][0] or 0
                away_avg_against = away_stats['away'][1] or 0
                
                features = [home_avg_for, home_avg_against, away_avg_for, away_avg_against]
                X.append(features)
                
                # Target: 1 se mandante ganhou, 0 se empatou, -1 se perdeu
                result = 1 if home_goals > away_goals else (0 if home_goals == away_goals else -1)
                y.append(result)
        
        if len(X) < 5:
            print("⚠️ Dados insuficientes após processamento.")
            return False
        
        # Treinar modelo
        self.model = LinearRegression()
        self.model.fit(X, y)
        
        # Salvar modelo
        self.save_model()
        print(f"✅ Modelo treinado com {len(X)} jogos!")
        return True
    
    def predict_odds(self, home_team, away_team):
        """Prevê as odds para um jogo"""
        
        home_stats = get_team_stats(home_team)
        away_stats = get_team_stats(away_team)
        
        # Se não há histórico, retorna odds padrão
        if not home_stats['home'] or not away_stats['away']:
            return self._default_odds()
        
        home_avg_for = home_stats['home'][0] or 0
        home_avg_against = home_stats['home'][1] or 0
        away_avg_for = away_stats['away'][0] or 0
        away_avg_against = away_stats['away'][1] or 0
        
        features = np.array([[home_avg_for, home_avg_against, away_avg_for, away_avg_against]])
        
        if self.model is None:
            # Usar fórmula simples se modelo não foi treinado
            home_strength = (home_avg_for - home_avg_against) * 1.5
            away_strength = (away_avg_for - away_avg_against) * 1.5
        else:
            home_strength = self.model.predict(features)[0]
        
        # Converter força em odds (fórmula simplificada)
        home_prob = self._sigmoid(home_strength)
        draw_prob = 0.25
        away_prob = 1 - home_prob - draw_prob
        
        # Garantir probabilidades válidas
        away_prob = max(0.01, away_prob)
        
        # Converter em odds (1/probabilidade)
        home_win_odds = round(1 / max(0.01, home_prob), 2)
        draw_odds = round(1 / draw_prob, 2)
        away_win_odds = round(1 / max(0.01, away_prob), 2)
        
        return {
            'home_win': home_win_odds,
            'draw': draw_odds,
            'away_win': away_win_odds
        }
    
    def _sigmoid(self, x):
        """Função sigmoid para converter força em probabilidade"""
        return 1 / (1 + np.exp(-x))
    
    def _default_odds(self):
        """Retorna odds padrão quando não há dados"""
        return {
            'home_win': 2.50,
            'draw': 3.00,
            'away_win': 2.70
        }
    
    def save_model(self):
        """Salva o modelo em arquivo"""
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(self.model, f)
    
    def load_model(self):
        """Carrega modelo salvo"""
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, 'rb') as f:
                    self.model = pickle.load(f)
            except:
                self.model = None

# Instância global
predictor = OddsPredictor()