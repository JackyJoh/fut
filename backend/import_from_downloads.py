"""
Quick script to import players/predictions from Downloads CSV to Neon
"""
import pandas as pd
import json
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import Player, PlayerPrediction

def import_players_csv():
    csv_path = r"C:\Users\jacka\Downloads\players_202602022105.csv"
    
    print("="*60)
    print("IMPORTING PLAYERS FROM DOWNLOADED CSV")
    print("="*60)
    
    # Create tables
    print("\n[1/3] Creating database tables...")
    create_db_and_tables()
    print("✓ Tables created")
    
    # Load CSV
    print(f"\n[2/3] Loading CSV from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"✓ Loaded {len(df)} players")
    
    # Import to database
    print("\n[3/3] Importing to Neon database...")
    with Session(engine) as session:
        count = 0
        for idx, row in df.iterrows():
            # Create player from row (adjust column names if needed)
            player_dict = row.to_dict()
            
            # Remove 'id' if it exists (let database generate new IDs)
            if 'id' in player_dict:
                del player_dict['id']
            
            # Convert NaN to None
            for key, value in player_dict.items():
                if pd.isna(value):
                    player_dict[key] = None
            
            try:
                player = Player(**player_dict)
                session.add(player)
                count += 1
                
                if count % 100 == 0:
                    session.commit()
                    print(f"  → Imported {count}/{len(df)} players...")
                    
            except Exception as e:
                print(f"  ✗ Error importing row {idx}: {e}")
                continue
        
        session.commit()
        print(f"\n✓ Successfully imported {count} players!")
    
    print("="*60)
    print("IMPORT COMPLETE!")
    print("="*60)

def import_predictions_csv():
    csv_path = r"C:\Users\jacka\Downloads\player_predictions_202602022131.csv"
    
    print("="*60)
    print("IMPORTING PREDICTIONS FROM DOWNLOADED CSV")
    print("="*60)
    
    # Create tables
    print("\n[1/4] Creating database tables...")
    create_db_and_tables()
    print("✓ Tables created")
    
    # Load CSV
    print(f"\n[2/4] Loading CSV from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"✓ Loaded {len(df)} predictions")
    
    # Detect ID offset
    print("\n[3/4] Detecting player ID offset...")
    with Session(engine) as session:
        # Get first player ID from Neon
        first_neon_player = session.exec(select(Player).order_by(Player.id)).first()
        neon_start_id = first_neon_player.id if first_neon_player else 1
        
        # Get first player ID from AWS CSV
        aws_start_id = int(df['player_id'].min())
        
        # Calculate offset
        id_offset = aws_start_id - neon_start_id
        
        print(f"✓ AWS starts at ID {aws_start_id}, Neon starts at ID {neon_start_id}")
        print(f"✓ Applying offset: -{id_offset} to all player IDs")
    
        print(f"✓ AWS starts at ID {aws_start_id}, Neon starts at ID {neon_start_id}")
        print(f"✓ Applying offset: -{id_offset} to all player IDs")
    
    # Import to database
    print("\n[4/4] Importing to Neon database...")
    with Session(engine) as session:
        count = 0
        skipped = 0
        for idx, row in df.iterrows():
            try:
                # Adjust player_id with offset
                adjusted_player_id = int(row['player_id']) - id_offset
                
                # Check if adjusted player_id exists in Neon
                player_exists = session.exec(
                    select(Player).where(Player.id == adjusted_player_id)
                ).first()
                
                if not player_exists:
                    skipped += 1
                    if skipped <= 5:  # Show first 5 mismatches
                        print(f"  ⊘ Skip: AWS ID {int(row['player_id'])} → Neon ID {adjusted_player_id} (not found)")
                    continue
                
                # Parse stats_library JSON if it's a string
                stats_lib = row['stats_library']
                if isinstance(stats_lib, str):
                    stats_lib = json.loads(stats_lib)
                
                prediction = PlayerPrediction(
                    player_id=adjusted_player_id,
                    stats_library=stats_lib,
                    year1_overall=int(row['year1_overall']),
                    year1_value=int(row['year1_value']),
                    year1_goals=float(row['year1_goals']),
                    year1_assists=float(row['year1_assists']),
                    computed_at=row['computed_at']
                )
                
                session.add(prediction)
                count += 1
                
                if count % 100 == 0:
                    session.commit()
                    print(f"  → Imported {count}/{len(df)} predictions (skipped {skipped})...")
                    
            except Exception as e:
                print(f"  ✗ Error importing row {idx}: {e}")
                session.rollback()
                continue
        
        session.commit()
        print(f"\n✓ Successfully imported {count} predictions!")
        print(f"⊘ Skipped {skipped} predictions (mismatched player IDs)")
    
    print("="*60)
    print("IMPORT COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    # Uncomment the one you want to run:
    # import_players_csv()
    import_predictions_csv()
