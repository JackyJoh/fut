import pandas as pd
import sys
from pathlib import Path
from sqlmodel import Session

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from database import engine, create_db_and_tables
from models import Player

def ingest_players(csv_path: str):
    """
    Reads current_players_2425.csv and inserts all players into the database.
    """
    # Load CSV
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} players")
    
    # Create tables if they don't exist
    create_db_and_tables()
    
    # Map CSV columns to Player model fields
    players = []
    for idx, row in df.iterrows():
        # Helper function to parse weak_foot and skill_moves (may have ' +1' or ' ★' suffixes)
        def parse_int_with_suffix(value):
            if pd.isna(value):
                return 0
            str_val = str(value).split()[0]  # Take first part before space
            try:
                return int(str_val)
            except ValueError:
                return 0
        
        player = Player(
            # Identity
            name = str(row['player']),
            short_name=str(row['short_name']),
            long_name=str(row['long_name']),
            nationality_name=str(row['nationality_name']),
            age_fifa=int(row['age_fifa']),
            
            # FIFA Attributes
            player_positions=str(row['player_positions']),
            overall=int(row['overall']),
            potential=int(row['potential']),
            value_eur=float(row['value_eur']) if pd.notna(row['value_eur']) else None,
            wage_eur=float(row['wage_eur']) if pd.notna(row['wage_eur']) else None,
            
            # Physical
            height_cm=int(row['height_cm']),
            weight_kg=int(row['weight_kg']),
            preferred_foot=str(row['preferred_foot']),
            weak_foot=parse_int_with_suffix(row['weak_foot']),
            skill_moves=parse_int_with_suffix(row['skill_moves']),
            
            # FIFA Stats
            pace=int(row['pace']),
            shooting=int(row['shooting']),
            passing=int(row['passing']),
            dribbling=int(row['dribbling']),
            defending=int(row['defending']),
            physic=int(row['physic']),
            
            # Club Info
            club_name=str(row['club_name']) if pd.notna(row['club_name']) else None,
            league_name=str(row['league_name']) if pd.notna(row['league_name']) else None,
            club_jersey_number=int(row['club_jersey_number']) if pd.notna(row['club_jersey_number']) else None,
            
            # FBRef Stats (Per 90)
            playing_time_min=float(row['Playing Time_Min']) if pd.notna(row['Playing Time_Min']) else None,
            playing_time_90s=float(row['Playing Time_90s']) if pd.notna(row['Playing Time_90s']) else None,
            gls_per90=float(row['Per 90 Minutes_Gls']) if pd.notna(row['Per 90 Minutes_Gls']) else None,
            ast_per90=float(row['Per 90 Minutes_Ast']) if pd.notna(row['Per 90 Minutes_Ast']) else None,
            g_plus_a_per90=float(row['Per 90 Minutes_G+A']) if pd.notna(row['Per 90 Minutes_G+A']) else None,
            g_minus_pk_per90=float(row['Per 90 Minutes_G-PK']) if pd.notna(row['Per 90 Minutes_G-PK']) else None,
            xg_per90=float(row['Per 90 Minutes_xG']) if pd.notna(row['Per 90 Minutes_xG']) else None,
            xag_per90=float(row['Per 90 Minutes_xAG']) if pd.notna(row['Per 90 Minutes_xAG']) else None,
            tkl_per90=float(row['Per 90 Minutes_Tackles_Tkl']) if pd.notna(row['Per 90 Minutes_Tackles_Tkl']) else None,
            int_per90=float(row['Per 90 Minutes_Int']) if pd.notna(row['Per 90 Minutes_Int']) else None,
            kp_per90=float(row['Per 90 Minutes_KP']) if pd.notna(row['Per 90 Minutes_KP']) else None,
            prgp_per90=float(row['Per 90 Minutes_PrgP']) if pd.notna(row['Per 90 Minutes_PrgP']) else None,
            
            # Standard Stats
            sh_per90=float(row['Standard_Sh/90']) if pd.notna(row['Standard_Sh/90']) else None,
            sot_percent=float(row['Standard_SoT%']) if pd.notna(row['Standard_SoT%']) else None,
            total_cmp_percent=float(row['Total_Cmp%']) if pd.notna(row['Total_Cmp%']) else None,
            sca_per90=float(row['SCA_SCA90']) if pd.notna(row['SCA_SCA90']) else None,
            
            # Engineered Features
            age_squared=int(row['age_squared']) if pd.notna(row['age_squared']) else None,
            is_youth=int(row['is_youth']) if pd.notna(row['is_youth']) else None,
            is_prime=int(row['is_prime']) if pd.notna(row['is_prime']) else None,
            is_veteran=int(row['is_veteran']) if pd.notna(row['is_veteran']) else None,
            is_elite=int(row['is_elite']) if pd.notna(row['is_elite']) else None,
            is_good=int(row['is_good']) if pd.notna(row['is_good']) else None,
            is_average=int(row['is_average']) if pd.notna(row['is_average']) else None,
            
            # Statistical Features
            wage_zscore=float(row['wage_zscore']) if pd.notna(row['wage_zscore']) else None,
            wage_percentile=float(row['wage_percentile']) if pd.notna(row['wage_percentile']) else None,
            value_zscore=float(row['value_zscore']) if pd.notna(row['value_zscore']) else None,
            goals_vs_xg=float(row['goals_vs_xG']) if pd.notna(row['goals_vs_xG']) else None,
            
            # Position Flags
            is_forward=int(row['is_forward']) if pd.notna(row['is_forward']) else None,
            is_midfield=int(row['is_midfield']) if pd.notna(row['is_midfield']) else None,
            is_defense=int(row['is_defense']) if pd.notna(row['is_defense']) else None,
            
            # Lag Features (Previous Season)
            overall_lag1=float(row['overall_lag1']) if pd.notna(row['overall_lag1']) else None,
            age_lag1=float(row['age_lag1']) if pd.notna(row['age_lag1']) else None,
            playing_time_min_lag1=float(row['Playing Time_Min_lag1']) if pd.notna(row['Playing Time_Min_lag1']) else None,
            gls_per90_lag1=float(row['Per 90 Minutes_Gls_lag1']) if pd.notna(row['Per 90 Minutes_Gls_lag1']) else None,
            ast_per90_lag1=float(row['Per 90 Minutes_Ast_lag1']) if pd.notna(row['Per 90 Minutes_Ast_lag1']) else None,
            g_plus_a_per90_lag1=float(row['Per 90 Minutes_G+A_lag1']) if pd.notna(row['Per 90 Minutes_G+A_lag1']) else None,
            xg_per90_lag1=float(row['Per 90 Minutes_xG_lag1']) if pd.notna(row['Per 90 Minutes_xG_lag1']) else None,
            value_eur_lag1=float(row['value_eur_lag1']) if pd.notna(row['value_eur_lag1']) else None,
            
            # Trend Features
            has_prior_season=int(row['has_prior_season']) if pd.notna(row['has_prior_season']) else None,
            rating_momentum=float(row['rating_momentum']) if pd.notna(row['rating_momentum']) else None,
            goals_trend=float(row['goals_trend']) if pd.notna(row['goals_trend']) else None,
            minutes_trend=float(row['minutes_trend']) if pd.notna(row['minutes_trend']) else None,
        )
        players.append(player)
        
        # Batch insert every 1000 players to avoid memory issues
        if len(players) >= 1000:
            with Session(engine) as session:
                session.add_all(players)
                session.commit()
                print(f"Inserted {idx + 1} players...")
            players = []
    
    # Insert remaining players
    if players:
        with Session(engine) as session:
            session.add_all(players)
            session.commit()
            print(f"Inserted final batch. Total: {len(df)} players")
    
    print("✓ Data ingestion complete!")

if __name__ == "__main__":
    csv_path = "../data/clean/current_players_2425.csv"
    ingest_players(csv_path)
