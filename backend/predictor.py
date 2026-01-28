import pickle
import pandas as pd
from sqlmodel import Session
from models import Player
import math
from model_utils import player_to_features
import concurrent.futures
import os

# Get the absolute path to the models directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(os.path.dirname(BASE_DIR), "models")

# LOAD MODELS
with open(os.path.join(MODELS_DIR, "faceStatsBundle.pkl"), "rb") as f:
    MODEL_BUNDLE = pickle.load(f)
paceModel = MODEL_BUNDLE['pace']
shootingModel = MODEL_BUNDLE['shooting']
passingModel = MODEL_BUNDLE['passing']
dribblingModel = MODEL_BUNDLE['dribbling']
defendingModel = MODEL_BUNDLE['defending']
physicModel = MODEL_BUNDLE['physic']
#IRL Stats Models
key90 = pickle.load(open(os.path.join(MODELS_DIR, "key90Model.pkl"), "rb"))
a90Model = pickle.load(open(os.path.join(MODELS_DIR, "a90Model.pkl"), "rb"))
g90Model = pickle.load(open(os.path.join(MODELS_DIR, "g90Model.pkl"), "rb"))
int90Model = pickle.load(open(os.path.join(MODELS_DIR, "int90Model.pkl"), "rb"))
tkl90Model = pickle.load(open(os.path.join(MODELS_DIR, "tkl90Model.pkl"), "rb"))
minModel = pickle.load(open(os.path.join(MODELS_DIR, "minutesModel.pkl"), "rb"))
# Extra Fifa
potModel = pickle.load(open(os.path.join(MODELS_DIR, "potModel.pkl"), "rb"))
ratingChange = pickle.load(open(os.path.join(MODELS_DIR, "changeModel.pkl"), "rb"))
overallModel = pickle.load(open(os.path.join(MODELS_DIR, "ovrModel.pkl"), "rb"))
valModel = pickle.load(open(os.path.join(MODELS_DIR, "valModel.pkl"), "rb"))




# 'Mini' Functions for quick predictions
# Face Stats Predictions
def predictPace(df_features) -> float:
    """Predict Pace"""
    try:
        return float(paceModel.predict(df_features)[0])
    except Exception as e:
        # Fallback: try with values only
        return float(paceModel.predict(df_features.values)[0])
        
def predictShooting(df_features) -> float:
    """Predict Shooting"""
    try:
        return float(shootingModel.predict(df_features)[0])
    except Exception as e:
        return float(shootingModel.predict(df_features.values)[0])
        
def predictDefending(df_features) -> float:
    """Predict Defending"""
    try:
        return float(defendingModel.predict(df_features)[0])
    except Exception as e:
        return float(defendingModel.predict(df_features.values)[0])
        
def predictPassing(df_features) -> float:
    """Predict Passing"""
    try:
        return float(passingModel.predict(df_features)[0])
    except Exception as e:
        return float(passingModel.predict(df_features.values)[0])
        
def predictDribbling(df_features) -> float:
    """Predict Dribbling"""
    try:
        return float(dribblingModel.predict(df_features)[0])
    except Exception as e:
        return float(dribblingModel.predict(df_features.values)[0])
        
def predictPhysic(df_features) -> float:
    """Predict Physic"""
    try:
        return float(physicModel.predict(df_features)[0])
    except Exception as e:
        return float(physicModel.predict(df_features.values)[0])
        
# Core FIFA
def predictRatingChange(df_features) -> float:
    """Predict Overall Rating Change"""
    try:
        return float(ratingChange.predict(df_features)[0])
    except Exception as e:
        return float(ratingChange.predict(df_features.values)[0])
        
def predictOverall(df_features) -> float:
    """Predict Overall Rating"""
    try:
        return float(overallModel.predict(df_features)[0])
    except Exception as e:
        return float(overallModel.predict(df_features.values)[0])
        
def predictValue(df_features) -> float:
    """Predict Market Value EUR"""
    try:
        return float(valModel.predict(df_features)[0])
    except Exception as e:
        return float(valModel.predict(df_features.values)[0])
        
def predictPotential(df_features) -> float:
    """Predict Potential"""
    try:
        return float(potModel.predict(df_features)[0])
    except Exception as e:
        return float(potModel.predict(df_features.values)[0])
        
# IRL Stats
def predictG90(df_features) -> float:
    """Predict Goals per 90"""
    try:
        return float(g90Model.predict(df_features)[0])
    except Exception as e:
        return float(g90Model.predict(df_features.values)[0])
        
def predictA90(df_features) -> float:
    """Predict Assists per 90"""
    try:
        return float(a90Model.predict(df_features)[0])
    except Exception as e:
        return float(a90Model.predict(df_features.values)[0])
        
def predictInt90(df_features) -> float:
    """Predict Interceptions per 90"""
    try:
        return float(int90Model.predict(df_features)[0])
    except Exception as e:
        return float(int90Model.predict(df_features.values)[0])
        
def predictTkl90(df_features) -> float:
    """Predict Tackles per 90"""
    try:
        return float(tkl90Model.predict(df_features)[0])
    except Exception as e:
        return float(tkl90Model.predict(df_features.values)[0])
        
def predictMin(df_features) -> float:
    """Predict Minutes Played"""
    try:
        return float(minModel.predict(df_features)[0])
    except Exception as e:
        return float(minModel.predict(df_features.values)[0])
        
def predictKey90(df_features) -> float:
    """Predict Key Passes per 90"""
    try:
        return float(key90.predict(df_features)[0])
    except Exception as e:
        return float(key90.predict(df_features.values)[0])


# Adjustment functions
# Overall and change fix | rounding/matching
def FixOverall(current, change):
    if 0 < change < 1:
        predictOverall = float(current + 1)
        predictChange = 1.0
    elif -1 < change < 0:
        predictOverall = float(current - 1)
        predictChange = -1.0
    else:
        predictOverall = float(current + round(float(change), 0))
        predictChange = round(float(change),0)
    
    return predictOverall, predictChange

def FixMomentum(momentum, ratingChange, ovr):

    if ratingChange < 0:
        predictChange = round((momentum) * .05)
    else :
        predictChange = ratingChange
    # Fix predicted overall based off new rating change
    predictOverall = float(math.ceil(ovr + predictChange))

    return predictChange, predictOverall

def FixValue(age, valueEur, ratingChange, predictedVal):
    valDif = predictedVal - valueEur

    # handle improper increase/decrease
    try:
        if (ratingChange <= 1 and valDif > 0):
            safe_rating_change = abs(ratingChange)
            predictedVal = valueEur - (math.sqrt(safe_rating_change) * (.11 * valueEur))
        elif (ratingChange >= 1 and valDif):
            safe_rating_change = ratingChange if ratingChange >= 0 else 0
            predictedVal = valueEur + (math.sqrt(safe_rating_change) * (.11 * valueEur))
    except Exception as e:
        print(f"FixValue math error: {e}")
        predictedVal = valueEur

    # Age fixing | start decreasing mv 29/30
    age_threshold = 30
    k = 0.05  # gentler exponential decay
    min_factor = 0.7  # don't let value drop below 50%
    if age >= age_threshold:
        age_factor = math.exp(-k * (age - age_threshold))
        age_factor = max(age_factor, min_factor)
        predictedVal = predictedVal * age_factor
    
    return predictedVal

def FixAttributes(results, position):
    # Needs to look more natural
    """
    Adjusts FIFA face stats in the results dict so at least 2 are close to overall.
    Prioritizes relevant attributes for the player's main position (FW, MF, DF).
    Expects: results (dict), position (str)
    Returns updated results dict.
    """
    stats = ['physic', 'defending', 'dribbling', 'passing', 'shooting', 'pace']
    try:
        ovr = results.get('predictOverall')
        if ovr is None or not isinstance(ovr, (int, float)):
            print(f"FixAttributes: Missing or invalid predictOverall in results: {ovr}")
            return results
        pos = str(position).split(',')[0].strip().upper() if position else ''
        if pos == 'FW':
            priorities = ['shooting', 'pace', 'dribbling']
        elif pos == 'MF':
            priorities = ['passing', 'dribbling', 'defending']
        elif pos == 'DF':
            priorities = ['defending', 'physic', 'pace']
        else:
            priorities = stats
        # Find which stats are within 2 of ovr
        close_stats = []
        for s in stats:
            val = results.get(f'predict{s.capitalize()}')
            try:
                if val is not None and isinstance(val, (int, float)) and abs(val - ovr) <= 2:
                    close_stats.append(s)
            except Exception as e:
                print(f"FixAttributes: Error comparing {s}: {e}")
        # Always update at least 2 stats if needed
        stats_to_update = []
        for s in priorities:
            val = results.get(f'predict{s.capitalize()}')
            try:
                if val is None or not isinstance(val, (int, float)) or abs(val - ovr) > 2:
                    stats_to_update.append(s)
            except Exception as e:
                print(f"FixAttributes: Error checking update for {s}: {e}")
        updated = 0
        for stat in stats_to_update:
            try:
                if updated < 2:
                    results[f'predict{stat.capitalize()}'] = ovr
                    updated += 1
            except Exception as e:
                print(f"FixAttributes: Error updating {stat}: {e}")
        return results
    except Exception as e:
        print(f"FixAttributes: Unexpected error: {e}")
        return results

# Feature 1 | Predict Current Season Stats
def predictStats(dfStats, player=None):
    """
    Predict key stats for a player (dataframe from front-end) using the face stats models.
    Returns a json/dict of predicted stats.
    """
    # Only pass model features to prediction functions
    # Allows additional features to be used for 'fixing'
    model_features = [
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
    df_model = dfStats[model_features].copy()

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
        futureToTask = {executor.submit(task, df_model): task.__name__ for task in tasks}
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
    try:
        playing_time_min = dfStats['Playing Time_Min'].iloc[0]
        playing_time_min = float(playing_time_min) if playing_time_min is not None else 0.0
    except:
        playing_time_min = 0.0
    
    # Safely pop and convert per-90 stats
    g90 = results.pop('predictG90', None)
    a90 = results.pop('predictA90', None)
    int90 = results.pop('predictInt90', None)
    tkl90 = results.pop('predictTkl90', None)
    key90 = results.pop('predictKey90', None)
    
    results['predictedGoals'] = (float(g90) if g90 is not None else 0.0) * (playing_time_min / 90) if playing_time_min > 0 else 0.0
    results['predictedAssists'] = (float(a90) if a90 is not None else 0.0) * (playing_time_min / 90) if playing_time_min > 0 else 0.0
    results['predictedInterceptions'] = (float(int90) if int90 is not None else 0.0) * (playing_time_min / 90) if playing_time_min > 0 else 0.0
    results['predictedTackles'] = (float(tkl90) if tkl90 is not None else 0.0) * (playing_time_min / 90) if playing_time_min > 0 else 0.0
    results['predictedKeyPasses'] = (float(key90) if key90 is not None else 0.0) * (playing_time_min / 90) if playing_time_min > 0 else 0.0
    results['predictedPotential'] = results.pop('predictPotential', 0.0)
    results['predictedMinutes'] = results.pop('predictMin', 0.0)

    # POST PREDICTION ADJUSTMENTS

    momentum = float(dfStats['rating_momentum'].iloc[0])
    ratingChange_val = results.get('predictRatingChange')
    ratingChange = float(ratingChange_val) if ratingChange_val is not None else 0.0  # actual predicted
    current_overall = float(math.ceil(float(dfStats['overall'].iloc[0])))        
    
    if momentum > 10:
        # Rating Momentum Fix (if momentum is very high, give revert negatives)
        results['predictRatingChange'], results['predictOverall'] = FixMomentum(momentum, ratingChange, current_overall)
    else:
        # Else fix overall & change (rounding)
        predicted_ovr = results.get('predictOverall', current_overall)
        rating_change = (predicted_ovr) - current_overall # calculated using new - old
        results['predictOverall'], results['predictRatingChange'] = FixOverall(current_overall, rating_change)
    
     # value fix | For old players and improper increase/decrease
    player_value_eur = getattr(player, 'value_eur', None) if player else None
    age_fifa_val = int(dfStats['age_fifa'].iloc[0])
    predictedValueEur = int(results.get('predictValue'))
    results['predictValue'] = FixValue(age_fifa_val, player_value_eur, results['predictRatingChange'], predictedValueEur)

    # Attribute fix | update dfStats with fixed attributes after predictions
    # FIX FUNCTION
    position = dfStats['pos'].iloc[0]
    #results = FixAttributes(results, position)
    
    
    return results