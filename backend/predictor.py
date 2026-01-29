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

    # Handle value adjustments based on rating change
    try:
        # Rating increased significantly: value should increase
        if ratingChange >= 1:
            safe_rating_change = ratingChange if ratingChange >= 0 else 0
            
            # Diminishing returns based on current value
            # Higher values grow slower (percentage-wise)
            if valueEur > 150_000_000:  # Over €150M
                growth_multiplier = 0.06
            elif valueEur > 100_000_000:  # €100M - €150M
                growth_multiplier = 0.08
            elif valueEur > 50_000_000:  # €50M - €100M
                growth_multiplier = 0.10
            else:  # Under €50M
                growth_multiplier = 0.12
            
            predictedVal = valueEur + (math.sqrt(safe_rating_change) * (growth_multiplier * valueEur))
        # Rating decreased: apply gentle penalty
        elif ratingChange <= -1:
            safe_rating_change = abs(ratingChange)
            # Elite players (>€80M) lose value slower (3%), others lose 5%
            decline_rate = 0.03 if valueEur > 80_000_000 else 0.05
            predictedVal = valueEur - (math.sqrt(safe_rating_change) * (decline_rate * valueEur))
        # Minor rating changes: use model prediction with smoothing
        elif -1 < ratingChange < 1:
            # Blend 70% model, 30% current value for stability
            predictedVal = (predictedVal * 0.7) + (valueEur * 0.3)
    except Exception as e:
        print(f"FixValue math error: {e}")
        predictedVal = valueEur

    # Age fixing | aggressive depreciation for older high-value players
    if age >= 33 and predictedVal > 20_000_000:
        # 33+: aggressive decay for expensive players (12% per year)
        years_past_33 = age - 33
        age_factor = math.pow(0.91, years_past_33)
        predictedVal = predictedVal * age_factor
    elif age >= 30 and predictedVal > 10_000_000:
        # 30-32: moderate decay for valuable players (5% per year)
        years_past_30 = age - 30
        age_factor = math.pow(0.92, years_past_30)
        predictedVal = predictedVal * age_factor
    
    # Absolute floor: no player below €500k
    predictedVal = max(predictedVal, 500_000)
    
    return predictedVal

def FixAttributes(results, position):
    """
    Adjusts FIFA face stats to ensure at least 2 are close to overall rating.
    - If 0 stats at/above OVR: boosts 2 closest stats with exponential scaling
    - If 1 stat at/above OVR: distributes gap from next closest to ALL stats (2x priority to closest)
    - If 2+ stats at/above OVR: no adjustment needed
    """
    stats = ['physic', 'defending', 'dribbling', 'passing', 'shooting', 'pace']
    
    try:
        ovr = results.get('predictOverall')
        if ovr is None or not isinstance(ovr, (int, float)):
            print(f"FixAttributes: Invalid predictOverall: {ovr}")
            return results
        
        ovr = float(ovr)
        
        # Collect current stat values and count how many are at/above OVR
        stat_values = {}
        at_or_above_count = 0
        for s in stats:
            val = results.get(f'predict{s.capitalize()}')
            if val is not None and isinstance(val, (int, float)):
                stat_values[s] = float(val)
                if val >= ovr:
                    at_or_above_count += 1
            else:
                stat_values[s] = ovr
        
        # Exit early if 2+ stats already at/above OVR
        if at_or_above_count >= 2:
            return results
        
        # Calculate gaps for stats below OVR
        gaps = {s: max(0, ovr - stat_values[s]) for s in stats}
        stats_with_gaps = [(s, gaps[s]) for s in stats if gaps[s] > 0]
        stats_with_gaps.sort(key=lambda x: x[1])  # Sort by gap (smallest first)
        
        if not stats_with_gaps:
            return results
        
        # Calculate points to distribute based on scenario
        if at_or_above_count == 1:
            # 1 stat already at OVR: distribute gap from next closest to ALL stats
            # Priority given to the next closest stat
            top_stats = [stats_with_gaps[0][0]]
            total_points = math.ceil(gaps[top_stats[0]])
        else:
            # 0 stats at OVR: boost 2 closest with exponential scaling
            if len(stats_with_gaps) < 2:
                return results
            
            top_stats = [s[0] for s in stats_with_gaps[:2]]
            gap_sum = gaps[top_stats[0]] + gaps[top_stats[1]]
            
            # Apply exponential boost when average gap is large
            avg_gap = sum(gaps.values()) / len([g for g in gaps.values() if g > 0])
            boost_factor = 1 + (math.pow(avg_gap / 8, 1.3) * 0.2)
            
            total_points = math.ceil(gap_sum * 0.7 * boost_factor)
        
        # Distribute points: priority stats get 2pts/iteration, others get 1pt
        remaining_points = total_points
        priority_stats = list(top_stats)
        other_stats = [s for s in stats if s not in top_stats]
        
        while remaining_points > 0:
            points_distributed = 0
            
            # Priority stats get 2 points (lose priority once they reach OVR)
            for stat in priority_stats[:]:
                if remaining_points > 0:
                    points_added = min(2, remaining_points)
                    stat_values[stat] += points_added
                    remaining_points -= points_added
                    points_distributed += points_added
                    
                    # Remove from priority if it reached OVR
                    if stat_values[stat] >= ovr:
                        priority_stats.remove(stat)
                        if stat not in other_stats:
                            other_stats.append(stat)
            
            # Other stats get 1 point
            for stat in other_stats:
                if remaining_points > 0:
                    points_added = min(1, remaining_points)
                    stat_values[stat] += points_added
                    remaining_points -= points_added
                    points_distributed += points_added
            
            if points_distributed == 0:
                break
        
        # Update results with rounded values
        for s in stats:
            results[f'predict{s.capitalize()}'] = round(stat_values[s])
        
        return results
        
    except Exception as e:
        print(f"FixAttributes error: {e}")
        return results

def resultsToNextSeasonDf(currentDf, results):
    """
    Converts prediction results into a dataframe for the next season.
    Updates all features needed for recursive predictions.
    """
    nextDf = currentDf.copy()
    
    # 1. Update lag features (shift current values to lag)
    nextDf['overall_lag1'] = currentDf['overall']
    nextDf['age_lag1'] = currentDf['age_fifa']
    nextDf['Playing Time_Min_lag1'] = currentDf['Playing Time_Min']
    nextDf['Per 90 Minutes_Gls_lag1'] = currentDf['Per 90 Minutes_Gls']
    nextDf['Per 90 Minutes_Ast_lag1'] = currentDf['Per 90 Minutes_Ast']
    nextDf['Per 90 Minutes_G+A_lag1'] = currentDf['Per 90 Minutes_G+A']
    nextDf['Per 90 Minutes_xG_lag1'] = currentDf['Per 90 Minutes_xG']
    nextDf['value_eur_lag1'] = currentDf['value_eur'] if 'value_eur' in currentDf.columns else results.get('predictValue', 0)
    
    # 2. Map predictions to input columns
    nextDf['pace'] = results.get('predictPace', currentDf['pace'].iloc[0])
    nextDf['shooting'] = results.get('predictShooting', currentDf['shooting'].iloc[0])
    nextDf['passing'] = results.get('predictPassing', currentDf['passing'].iloc[0])
    nextDf['dribbling'] = results.get('predictDribbling', currentDf['dribbling'].iloc[0])
    nextDf['defending'] = results.get('predictDefending', currentDf['defending'].iloc[0])
    nextDf['physic'] = results.get('predictPhysic', currentDf['physic'].iloc[0])
    nextDf['overall'] = results.get('predictOverall', currentDf['overall'].iloc[0])
    
    # For young players below their original potential, maintain it; otherwise use predicted
    age = currentDf['age_fifa'].iloc[0]
    current_overall = results.get('predictOverall', currentDf['overall'].iloc[0])
    original_potential = currentDf.get('original_potential', currentDf['potential'].iloc[0])
    if isinstance(original_potential, pd.Series):
        original_potential = original_potential.iloc[0]
    
    if age <= 25 and current_overall < original_potential:
        nextDf['potential'] = original_potential
    else:
        # Use max of predicted and current overall to prevent potential dropping below overall
        predicted_pot = results.get('predictedPotential', currentDf['potential'].iloc[0])
        nextDf['potential'] = max(predicted_pot, current_overall)
    
    # Preserve original_potential for next iteration
    nextDf['original_potential'] = original_potential
    
    nextDf['value_eur'] = results.get('predictValue', currentDf['value_eur'].iloc[0] if 'value_eur' in currentDf.columns else 0)
    
    # 3. Keep database minutes constant across all predictions (don't use predicted minutes)
    databaseMinutes = currentDf['Playing Time_Min'].iloc[0]
    nextDf['Playing Time_Min'] = databaseMinutes
    nextDf['Playing Time_90s'] = databaseMinutes / 90 if databaseMinutes > 0 else 0
    
    # Use database minutes to calculate per-90 stats from predicted totals
    if databaseMinutes > 0:
        nextDf['Per 90 Minutes_Gls'] = (results.get('predictedGoals', 0) / databaseMinutes) * 90
        nextDf['Per 90 Minutes_Ast'] = (results.get('predictedAssists', 0) / databaseMinutes) * 90
        nextDf['Per 90 Minutes_G+A'] = nextDf['Per 90 Minutes_Gls'] + nextDf['Per 90 Minutes_Ast']
        nextDf['Per 90 Minutes_Tackles_Tkl'] = (results.get('predictedTackles', 0) / databaseMinutes) * 90
        nextDf['Per 90 Minutes_Int'] = (results.get('predictedInterceptions', 0) / databaseMinutes) * 90
        nextDf['Per 90 Minutes_KP'] = (results.get('predictedKeyPasses', 0) / databaseMinutes) * 90
    else:
        nextDf['Per 90 Minutes_Gls'] = 0
        nextDf['Per 90 Minutes_Ast'] = 0
        nextDf['Per 90 Minutes_G+A'] = 0
        nextDf['Per 90 Minutes_Tackles_Tkl'] = 0
        nextDf['Per 90 Minutes_Int'] = 0
        nextDf['Per 90 Minutes_KP'] = 0
    
    # 4. Increment age
    nextDf['age_fifa'] = currentDf['age_fifa'].iloc[0] + 1
    
    # 5. Recalculate derived features
    age = nextDf['age_fifa'].iloc[0]
    nextDf['age_squared'] = age ** 2
    nextDf['is_youth'] = 1 if age < 23 else 0
    nextDf['is_prime'] = 1 if 23 <= age <= 29 else 0
    nextDf['is_veteran'] = 1 if age > 29 else 0
    
    ovr = nextDf['overall'].iloc[0]
    nextDf['is_elite'] = 1 if ovr >= 85 else 0
    nextDf['is_good'] = 1 if 75 <= ovr < 85 else 0
    nextDf['is_average'] = 1 if ovr < 75 else 0
    
    # 6. Calculate momentum and trends
    ratingChange = results.get('predictRatingChange', 0)
    # Accumulate momentum with decay
    currentMomentum = currentDf['rating_momentum'].iloc[0] if 'rating_momentum' in currentDf.columns else 0
    # Apply 0.7 decay (30% fade per year)
    decayedMomentum = currentMomentum * 0.7
    newMomentum = decayedMomentum + ratingChange
    # Light cap between -10 and +10
    nextDf['rating_momentum'] = max(-10, min(10, newMomentum))
    
    # Goals trend: difference between current and lag
    nextDf['goals_trend'] = nextDf['Per 90 Minutes_Gls'].iloc[0] - nextDf['Per 90 Minutes_Gls_lag1'].iloc[0]
    
    # Minutes trend: difference between current and lag
    nextDf['minutes_trend'] = nextDf['Playing Time_Min'].iloc[0] - nextDf['Playing Time_Min_lag1'].iloc[0]
    
    # goals vs xG
    if 'Per 90 Minutes_xG' in nextDf.columns:
        nextDf['goals_vs_xG'] = nextDf['Per 90 Minutes_Gls'] - nextDf['Per 90 Minutes_xG']
    else:
        nextDf['goals_vs_xG'] = 0
    
    # Has prior season is now always True
    nextDf['has_prior_season'] = 1
    
    # Keep wage/value zscore and percentile (or recalculate if you have the logic)
    # For now, maintain existing values as they require full dataset context
    
    return nextDf

def predictNineYears(dfStats, player=None):
    """
    Predict 9 years of player progression recursively.
    Returns a list of prediction results, one for each year.
    """
    allPredictions = []
    currentDf = dfStats.copy()
    
    # Store original potential for youth protection
    original_potential = float(dfStats['potential'].iloc[0])
    currentDf['original_potential'] = original_potential
    
    for year in range(9):
        # Predict current season
        results = predictStats(currentDf, player)
        results['year'] = year + 1  # Year 1-9
        allPredictions.append(results)
        
        # Prepare dataframe for next season (unless it's the last year)
        if year < 8:
            currentDf = resultsToNextSeasonDf(currentDf, results)
    
    return allPredictions


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
    # Use value from dataframe (which gets updated each year) instead of player object
    player_value_eur = dfStats['value_eur'].iloc[0] if 'value_eur' in dfStats.columns else (getattr(player, 'value_eur', None) if player else None)
    age_fifa_val = int(dfStats['age_fifa'].iloc[0])
    predictedValueEur = int(results.get('predictValue'))
    results['predictValue'] = FixValue(age_fifa_val, player_value_eur, results['predictRatingChange'], predictedValueEur)

    # Attribute fix | update dfStats with fixed attributes after predictions
    position = dfStats['pos'].iloc[0]
    results = FixAttributes(results, position)
    
    
    return results