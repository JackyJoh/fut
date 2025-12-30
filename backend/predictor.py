import pickle
import pandas as pd
from sqlmodel import Session
from models import Player
import math as Math
from model_utils import player_to_features
import concurrent.futures


# LOAD MODELS
with open("../models/faceStatsBundle.pkl", "rb") as f:
    MODEL_BUNDLE = pickle.load(f)
paceModel = MODEL_BUNDLE['pace']
shootingModel = MODEL_BUNDLE['shooting']
passingModel = MODEL_BUNDLE['passing']
dribblingModel = MODEL_BUNDLE['dribbling']
defendingModel = MODEL_BUNDLE['defending']
physicModel = MODEL_BUNDLE['physic']
#IRL Stats Models
key90 = pickle.load(open("../models/key90Model.pkl", "rb"))
a90Model = pickle.load(open("../models/a90Model.pkl", "rb"))
g90Model = pickle.load(open("../models/g90Model.pkl", "rb"))
int90Model = pickle.load(open("../models/int90Model.pkl", "rb"))
tkl90Model = pickle.load(open("../models/tkl90Model.pkl", "rb"))
minModel = pickle.load(open("../models/minutesModel.pkl", "rb"))
# Extra Fifa
potModel = pickle.load(open("../models/potModel.pkl", "rb"))
ratingChange = pickle.load(open("../models/changeModel.pkl", "rb"))
overallModel = pickle.load(open("../models/ovrModel.pkl", "rb"))
valModel = pickle.load(open("../models/valModel.pkl", "rb"))




# 'Mini' Functions for quick predictions
# Face Stats Predictions
def predictPace(df_features) -> float:
    """Predict Pace"""
    return paceModel.predict(df_features)[0]
def predictShooting(df_features) -> float:
    """Predict Shooting"""
    return shootingModel.predict(df_features)[0]
def predictDefending(df_features) -> float:
    """Predict Defending"""
    return defendingModel.predict(df_features)[0]
def predictPassing(df_features) -> float:
    """Predict Passing"""
    return passingModel.predict(df_features)[0]
def predictDribbling(df_features) -> float:
    """Predict Dribbling"""
    return dribblingModel.predict(df_features)[0]
def predictPhysic(df_features) -> float:
    """Predict Physic"""
    return physicModel.predict(df_features)[0]
# Core FIFA
def predictRatingChange(df_features) -> float:
    """Predict Overall Rating Change"""
    return ratingChange.predict(df_features)[0]
def predictOverall(df_features) -> float:
    """Predict Overall Rating"""
    return overallModel.predict(df_features)[0]
def predictValue(df_features) -> float:
    """Predict Market Value EUR"""
    return valModel.predict(df_features)[0]
def predictPotential(df_features) -> float:
    """Predict Potential"""
    return potModel.predict(df_features)[0]
# IRL Stats
def predictG90(df_features) -> float:
    """Predict Goals per 90"""
    return g90Model.predict(df_features)[0]
def predictA90(df_features) -> float:
    """Predict Assists per 90"""
    return a90Model.predict(df_features)[0]
def predictInt90(df_features) -> float:
    """Predict Interceptions per 90"""
    return int90Model.predict(df_features)[0]
def predictTkl90(df_features) -> float:
    """Predict Tackles per 90"""
    return tkl90Model.predict(df_features)[0]
def predictMin(df_features) -> float:
    """Predict Minutes Played"""
    return minModel.predict(df_features)[0]
def predictKey90(df_features) -> float:
    """Predict Key Passes per 90"""
    return key90.predict(df_features)[0]


# Feature 1 | Predict Current Season Stats
def predictStats(dfStats, player=None):
    """
    Predict key stats for a player (dataframe from front-end) using the face stats models.
    Returns a json/dict of predicted stats.
    """    # Tasks of predictions
    tasks = [
        predictPace,
        predictShooting,
        predictPassing,
        predictDribbling,
        predictPhysic,
        predictDefending,
        predictRatingChange,
        predictOverall,
        predictValue,
        predictPotential,
        predictG90,
        predictA90,
        predictInt90,
        predictTkl90,
        predictMin,
        predictKey90        
    ]

    results = {}
    # Run tasks in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futureToTask = {executor.submit(task, dfStats): task.__name__ for task in tasks}
        for future in concurrent.futures.as_completed(futureToTask):
            task_name = futureToTask[future]
            try:
                result = future.result()
                # Convert numpy types to Python native types for JSON serialization
                results[task_name] = float(result) if result is not None else None
            except Exception as e:
                results[task_name] = None
                print(f"Error in {task_name}: {e}")
    # Change per 90 to normal stats where applicable
    playing_time_min = float(dfStats['Playing Time_Min'].iloc[0])
    results['predictedGoals'] = float(results.pop('predictG90')) * (playing_time_min / 90)
    results['predictedAssists'] = float(results.pop('predictA90')) * (playing_time_min / 90)
    results['predictedInterceptions'] = float(results.pop('predictInt90')) * (playing_time_min / 90)
    results['predictedTackles'] = float(results.pop('predictTkl90')) * (playing_time_min / 90)
    results['predictedKeyPasses'] = float(results.pop('predictKey90')) * (playing_time_min / 90)

   
    # NEED TO CLEAN THIS CODE BELOW

    # Rating Momentum Fix (if momentum is very high, give revert negatives)
    momentum = dfStats['rating_momentum'].iloc[0]
    if momentum > 10:
        if results['predictRatingChange'] < 0:
            results['predictRatingChange'] = round((momentum) * .05)
        # Fix predicted overall based off new rating change
        results['predictOverall'] = float(Math.ceil(float(dfStats['overall'].iloc[0]) + results['predictRatingChange']))
        results['predictedPotential'] = dfStats['potential'].iloc[0]
        return results


    current_overall = Math.ceil(float(dfStats['overall'].iloc[0]))
    rating_change = results['predictOverall'] - current_overall
    if 0 < rating_change < 1:
        results['predictOverall'] = float(current_overall + 1)
        results['predictRatingChange'] = 1.0
    elif -1 < rating_change < 0:
        results['predictOverall'] = float(current_overall - 1)
        results['predictRatingChange'] = -1.0
    else:
        results['predictRatingChange'] = round((float(rating_change)),0)
    
     # value fix | high value players tend to drop crazy value w little rating change and not old
    player_value_eur = getattr(player, 'value_eur', None) if player else None
    if dfStats['age_fifa'].iloc[0] < 30 and player_value_eur > 80000000:
        if results['predictRatingChange'] is not None and results['predictRatingChange'] < 1:
            results['predictValue'] = player_value_eur * (0.95 - (results['predictRatingChange'] * 0.02))
        elif results['predictRatingChange'] is not None and results['predictRatingChange'] >= 1:
            results['predictValue'] = player_value_eur * 1.05
    
    return results