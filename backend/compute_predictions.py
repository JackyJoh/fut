"""
Script to pre-compute predictions for all players and store in database.
Run this once to populate the predictions table.
"""
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import Player, PlayerPrediction
from predictor import predictNineYears
from model_utils import player_to_features
from datetime import datetime
import time

def compute_all_predictions():
    """Compute predictions for all players and store in database"""
    
    print("="*60)
    print("STARTING PREDICTION COMPUTATION")
    print("="*60)
    
    # Ensure tables exist
    print("\n[1/5] Creating database tables...")
    create_db_and_tables()
    print("✓ Tables created/verified")
    
    with Session(engine) as session:
        # Get all players
        print("\n[2/5] Fetching all players from database...")
        players = session.exec(select(Player)).all()
        total = len(players)
        print(f"✓ Found {total} players to process")
        
        print("\n[3/5] Checking for existing predictions...")
        existing_count = session.exec(select(PlayerPrediction)).all()
        print(f"✓ {len(existing_count)} predictions already computed")
        
        print("\n[4/5] Computing predictions...")
        print("-"*60)
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        for idx, player in enumerate(players, 1):
            try:
                # Check if prediction already exists
                existing = session.exec(
                    select(PlayerPrediction).where(PlayerPrediction.player_id == player.id)
                ).first()
                
                if existing:
                    skipped_count += 1
                    if idx % 100 == 0:
                        print(f"[{idx}/{total}] Skipped {player.short_name} (already exists)")
                    continue
                
                print(f"\n[{idx}/{total}] Processing: {player.short_name} ({player.overall} OVR, Age {player.age_fifa})")
                
                # Convert player to features
                print(f"  → Converting player to features...")
                features = player_to_features(player)
                
                # Run predictions
                print(f"  → Running 9-year predictions...")
                stats_library = predictNineYears(features, player)
                print(f"  → Predictions complete!")
                
                # Create prediction record
                prediction = PlayerPrediction(
                    player_id=player.id,
                    stats_library=stats_library,
                    year1_overall=int(stats_library[0].get('predictOverall', 0)),
                    year1_value=int(stats_library[0].get('predictValue', 0)),
                    year1_goals=float(stats_library[0].get('predictedGoals', 0)),
                    year1_assists=float(stats_library[0].get('predictedAssists', 0)),
                    computed_at=datetime.utcnow().isoformat()
                )
                
                print(f"  → Saving to database...")
                session.add(prediction)
                session.commit()
                
                success_count += 1
                print(f"  ✓ SUCCESS - Year 1: {prediction.year1_overall} OVR, €{prediction.year1_value:,}")
                
                # Progress update every 10 players
                if idx % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = idx / elapsed
                    eta = (total - idx) / rate if rate > 0 else 0
                    print(f"\n{'='*60}")
                    print(f"PROGRESS: {idx}/{total} ({idx/total*100:.1f}%)")
                    print(f"Success: {success_count} | Skipped: {skipped_count} | Errors: {error_count}")
                    print(f"Rate: {rate:.1f} players/sec | ETA: {eta/60:.1f} min")
                    print(f"{'='*60}")
                
            except Exception as e:
                error_count += 1
                print(f"\n  ✗ ERROR for {player.short_name}: {str(e)}")
                session.rollback()
                continue
        
        print(f"\n[5/5] Finalizing...")
        print("="*60)
        print("COMPUTATION COMPLETE!")
        print("="*60)
        print(f"Total Players: {total}")
        print(f"✓ Success: {success_count}")
        print(f"⊘ Skipped: {skipped_count}")
        print(f"✗ Errors: {error_count}")
        print("="*60)

if __name__ == "__main__":
    start_time = time.time()
    compute_all_predictions()
    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
