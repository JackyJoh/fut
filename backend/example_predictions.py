"""
Example: Using model_utils to make predictions on database players
"""
from sqlmodel import Session
from database import engine
from model_utils import (
    get_player_by_name,
    player_to_features,
    predict_player_stats,
    predict_player_bundle
)

# Example 1: Get a single player and make predictions
with Session(engine) as session:
    # Find a player
    player = get_player_by_name(session, "Haaland")
    
    if player:
        print(f"Found: {player.short_name} - {player.overall} OVR")
        
        # Convert to model features
        features = player_to_features(player)
        print(f"Feature shape: {features.shape}")
        print(f"First 5 features:\n{features.iloc[:, :5]}")
        
        # Make a single prediction
        predicted_overall = predict_player_stats(player, '../models/ovrModel.pkl')
        print(f"\nPredicted next overall: {predicted_overall:.1f}")
        
        # Predict face stats bundle
        face_stats = predict_player_bundle(player, '../models/faceStatsBundle.pkl')
        print(f"\nPredicted face stats:")
        for stat, value in face_stats.items():
            print(f"  {stat}: {value:.1f}")
