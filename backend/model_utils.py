"""
Utilities for preparing database data for model predictions.
"""
import pandas as pd
import pickle
from typing import List, Dict
from sqlmodel import Session, select
from models import Player

# Feature columns in the exact order expected by the trained models
# This should match X_outfield.csv column order
MODEL_FEATURES = [
    'age_fifa', 'overall', 'potential', 'pace', 'shooting', 'passing',
    'dribbling', 'defending', 'physic', 'Playing Time_Min',
    'Playing Time_90s', 'Per 90 Minutes_Gls', 'Per 90 Minutes_Ast',
    'Per 90 Minutes_G+A', 'Per 90 Minutes_G-PK', 'Per 90 Minutes_xG',
    'Per 90 Minutes_xAG', 'Standard_Sh/90', 'Standard_SoT%', 'Total_Cmp%',
    'Per 90 Minutes_KP', 'Per 90 Minutes_PrgP',
    'Per 90 Minutes_Tackles_Tkl', 'Per 90 Minutes_Int', 'SCA_SCA90',
    'age_squared', 'is_youth', 'is_prime', 'is_veteran', 'is_elite',
    'is_good', 'is_average', 'wage_zscore', 'wage_percentile',
    'value_zscore', 'goals_vs_xG', 'is_forward', 'is_midfield',
    'is_defense', 'overall_lag1', 'age_lag1', 'Playing Time_Min_lag1',
    'Per 90 Minutes_Gls_lag1', 'Per 90 Minutes_Ast_lag1',
    'Per 90 Minutes_G+A_lag1', 'Per 90 Minutes_xG_lag1', 'value_eur_lag1',
    'has_prior_season', 'rating_momentum', 'goals_trend', 'minutes_trend'
]

# Mapping from database column names to model feature names
DB_TO_MODEL_MAPPING = {
    'value_eur': 'value_eur',
    'age_fifa': 'age_fifa',
    'overall': 'overall',
    'potential': 'potential',
    'pace': 'pace',
    'shooting': 'shooting',
    'passing': 'passing',
    'dribbling': 'dribbling',
    'defending': 'defending',
    'physic': 'physic',
    'playing_time_min': 'Playing Time_Min',
    'playing_time_90s': 'Playing Time_90s',
    'gls_per90': 'Per 90 Minutes_Gls',
    'ast_per90': 'Per 90 Minutes_Ast',
    'g_plus_a_per90': 'Per 90 Minutes_G+A',
    'g_minus_pk_per90': 'Per 90 Minutes_G-PK',
    'xg_per90': 'Per 90 Minutes_xG',
    'xag_per90': 'Per 90 Minutes_xAG',
    'sh_per90': 'Standard_Sh/90',
    'sot_percent': 'Standard_SoT%',
    'total_cmp_percent': 'Total_Cmp%',
    'kp_per90': 'Per 90 Minutes_KP',
    'prgp_per90': 'Per 90 Minutes_PrgP',
    'tkl_per90': 'Per 90 Minutes_Tackles_Tkl',
    'int_per90': 'Per 90 Minutes_Int',
    'sca_per90': 'SCA_SCA90',
    'age_squared': 'age_squared',
    'is_youth': 'is_youth',
    'is_prime': 'is_prime',
    'is_veteran': 'is_veteran',
    'is_elite': 'is_elite',
    'is_good': 'is_good',
    'is_average': 'is_average',
    'wage_zscore': 'wage_zscore',
    'wage_percentile': 'wage_percentile',
    'value_zscore': 'value_zscore',
    'goals_vs_xg': 'goals_vs_xG',
    'is_forward': 'is_forward',
    'is_midfield': 'is_midfield',
    'is_defense': 'is_defense',
    'overall_lag1': 'overall_lag1',
    'age_lag1': 'age_lag1',
    'playing_time_min_lag1': 'Playing Time_Min_lag1',
    'gls_per90_lag1': 'Per 90 Minutes_Gls_lag1',
    'ast_per90_lag1': 'Per 90 Minutes_Ast_lag1',
    'g_plus_a_per90_lag1': 'Per 90 Minutes_G+A_lag1',
    'xg_per90_lag1': 'Per 90 Minutes_xG_lag1',
    'value_eur_lag1': 'value_eur_lag1',
    'has_prior_season': 'has_prior_season',
    'rating_momentum': 'rating_momentum',
    'goals_trend': 'goals_trend',
    'minutes_trend': 'minutes_trend',
}


def player_to_features(player: Player) -> pd.DataFrame:
    """
    Convert a Player database object to a feature DataFrame ready for model prediction.
    Returns a single-row DataFrame with columns in the correct order for the model.
    """
    # Create dictionary with model feature names
    features = {}
    
    for db_col, model_col in DB_TO_MODEL_MAPPING.items():
        value = getattr(player, db_col, None)
        # Replace None with 0 for model compatibility
        features[model_col] = value if value is not None else 0.0
    
    # Create DataFrame with features in correct order
    df = pd.DataFrame([features])
    df = df[MODEL_FEATURES]  # Ensure correct column order
    return df

def get_players_by_name(session: Session, name: str) -> List[Player]:
    """
    Retrieve a LIST of players for the frontend dropdown.
    """
    statement = select(Player).where(
        (Player.name.ilike(f"%{name}%")) | 
        (Player.long_name.ilike(f"%{name}%"))
    ).limit(10) # Don't overwhelm the frontend
    
    results = session.exec(statement).all() # Returns a list of Player objects
    return results

def get_player_by_id(session: Session, player_id: int) -> Player:
    """
    Retrieve a single player by their database ID.
    """
    statement = select(Player).where(Player.id == player_id)
    result = session.exec(statement).first() # Returns a single Player object or None
    return result