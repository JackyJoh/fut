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
def FixOverall(current, change, age=None, potential=None):
    # Youth/prime players (under 30): Use smart growth logic
    if age is not None and potential is not None and age < 30:
        gap_to_potential = potential - current
        
        # Far below potential (5+) - boost aggressively
        if gap_to_potential >= 5:
            # Use ML prediction but ensure minimum +2 growth
            if change < 2:
                change = max(2, min(4, gap_to_potential * 0.5))
            # Cap max growth at 4
            change = min(change, 4)
        
        # Medium gap (3-4) - strong growth bias
        elif gap_to_potential >= 3:
            # Use ML prediction but ensure minimum +1 growth
            if change < 1:
                change = max(1, min(3, gap_to_potential * 0.6))
            # Cap max growth at 3
            change = min(change, 3)
        
        # Close to potential (1-2 below) - allow ML model with floor
        elif gap_to_potential >= 1:
            # Use ML prediction but prevent decline
            if change < 0:
                change = max(0, min(2, gap_to_potential))
            # Allow natural variance but cap at reaching potential
            change = min(change, gap_to_potential + 1)
        
        # At potential (0) or above - allow natural variance and growth beyond potential
        else:
            # Use ML prediction with light dampening on extremes
            # Prime age players (under 28) - natural variance around potential
            if age < 28:
                # If at exact potential - allow natural ML predictions
                if current == potential:
                    if change <= -2:
                        change = -1  # Dampen extreme drops
                    elif change >= 3:
                        change = 2  # Cap extreme growth
                # If 1 below potential
                elif current == potential - 1:
                    if change <= -2:
                        change = -1  # Dampen big drops
                    elif change >= 3:
                        change = 2  # Cap growth
                # If 2 below potential
                elif current == potential - 2:
                    if change <= -2:
                        change = -1  # Dampen drops
                    elif change >= 3:
                        change = 2  # Cap growth
                # Above potential - allow it but cap extreme growth
                elif current > potential:
                    if change >= 2:
                        change = 1  # Cap growth when already above potential
                    elif change <= -2:
                        change = -1  # Dampen drops
            # Late prime (28-29) - allow more natural variance
            else:
                # More natural variance, less interference
                if change >= 3:
                    change = 2
                elif change <= -3:
                    change = -2
    
    # Veterans (30-34): Natural aging with decline bias
    elif age is not None and 30 <= age < 35:
        # Elite players (85+) can maintain form better
        is_elite_veteran = current >= 85
        
        if is_elite_veteran:
            # Elite veterans: use ML with light bias, allow some improvement
            if change >= 2:
                change = 1  # Allow +1 growth (exceptional season)
            elif change >= 0.5:
                change = 1  # Moderate positive becomes +1
            elif change >= 0.1:
                change = 0  # Small positive becomes stability
            elif change >= -0.2:
                change = -1  # Near-zero biased to decline
            elif change <= -3:
                change = -2  # Cap decline at -2 per year
            # else: use ML prediction (-2 range)
        else:
            # Regular veterans: more decline bias but still allow improvement
            if change >= 2:
                change = 1  # Allow +1 growth (good season)
            elif change >= 0.7:
                change = 1  # Good positive becomes +1
            elif change >= 0.2:
                change = 0  # Small positive becomes stability
            elif change >= -0.2:
                change = -1  # Near-zero biased to decline
            elif change <= -3:
                change = -2  # Cap extreme decline at -2 per year
            # else: use ML prediction (-2 range)
    
    # Very old players (35+): Natural aging with stronger decline bias
    elif age is not None and age >= 35:
        # Elite players (85+) decline more naturally
        is_elite_old = current >= 85
        
        if is_elite_old:
            # Elite old players: use ML with decline bias
            if change >= 2:
                change = 0  # Dampen growth to stability
            elif change > 0:
                change = -1  # Convert gains to decline
            elif change > -0.5:
                change = -1  # Bias near-zero to decline
            elif change <= -4:
                change = -2  # Cap decline at -2 per year
            # else: use ML prediction (-2 to -1 range)
        else:
            # Regular old players: faster decline
            if change >= 1:
                change = -1  # Convert gains to decline
            elif change > -0.5:
                change = -1  # Force decline for near-zero
            elif change <= -4:
                change = -3  # Cap at -3 per year
            # else: use ML prediction (-3 to -1 range)
    
    # Round the change and calculate new overall
    predictChange = round(float(change), 0)
    
    # Diminishing returns for elite players - harder to improve at high ratings
    if current >= 92 and predictChange > 0:
        # 92+: very hard to improve, max +1 and only 50% of the time
        predictChange = min(round(predictChange * 0.4), 1)
    elif current >= 90 and predictChange > 0:
        # 90-91: hard to improve, max +1
        predictChange = min(predictChange, 1)
    elif current >= 88 and predictChange > 0:
        # 88-89: can gain max +2
        predictChange = min(predictChange, 2)
    elif current >= 85 and predictChange > 0:
        # 85-87: can gain max +3
        predictChange = min(predictChange, 3)
    
    predictOverall = float(current + predictChange)
    
    # Soft cap at 93 - only GOAT tier players reach this
    if predictOverall > 93:
        predictOverall = 93.0
        predictChange = predictOverall - current
    
    return predictOverall, predictChange

def FixMomentum(momentum, ratingChange, ovr):

    if ratingChange < 0:
        predictChange = round((momentum) * .05)
    else :
        predictChange = ratingChange
    # Fix predicted overall based off new rating change
    predictOverall = float(math.ceil(ovr + predictChange))

    return predictChange, predictOverall

def FixValue(age, valueEur, ratingChange, predictedVal, overall=75):
    valDif = predictedVal - valueEur

    # Handle value adjustments based on rating change
    try:
        # Rating increased significantly: value should increase
        if ratingChange >= 1:
            safe_rating_change = ratingChange if ratingChange >= 0 else 0
            
            # Diminishing returns based on current value
            # Higher values grow slower (percentage-wise)
            if valueEur > 150_000_000:  # Over €150M
                growth_multiplier = 0.04
            elif valueEur > 100_000_000:  # €100M - €150M
                growth_multiplier = 0.06
            elif valueEur > 50_000_000:  # €50M - €100M
                growth_multiplier = 0.08
            elif valueEur > 20_000_000:  # €20M - €50M
                growth_multiplier = 0.18
            elif valueEur > 10_000_000:  # €10M - €20M
                growth_multiplier = 0.30
            else:  # Under €10M - young players making big jumps
                growth_multiplier = 0.50
            
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
            
            # Cap year-over-year decline for elite players (85+) maintaining rating
            # Prevents sharp drops when rating doesn't change
            if overall >= 85 and ratingChange >= 0 and predictedVal < valueEur:
                max_decline = valueEur * 0.15  # Allow max 15% drop per year
                min_value = valueEur - max_decline
                if predictedVal < min_value:
                    predictedVal = min_value
    except Exception as e:
        print(f"FixValue math error: {e}")
        predictedVal = valueEur

    # Calculate expected minimum value based on overall rating
    # This serves as a baseline to prevent undervaluation FOR YOUNG/PRIME PLAYERS ONLY
    # Veterans (30+) are exempt from these floors
    if age < 30:
        expected_value = 0
        if overall >= 90:
            expected_value = 80_000_000
        elif overall >= 88:
            expected_value = 60_000_000
        elif overall >= 85:
            expected_value = 40_000_000
        elif overall >= 82:
            expected_value = 25_000_000
        elif overall >= 80:
            expected_value = 15_000_000
        elif overall >= 78:
            expected_value = 8_000_000
        elif overall >= 75:
            expected_value = 4_000_000
        
        # Enforce minimum value floor based on overall rating (young/prime only)
        if predictedVal < expected_value:
            predictedVal = expected_value
    
    # Age fixing | aggressive depreciation for older high-value players
    # AND value boost ONLY for undervalued young elite players
    if age <= 23 and predictedVal > 5_000_000 and predictedVal < expected_value * 0.7:
        # Only boost if predicted value is less than 70% of expected (undervalued)
        # Young elite players should be worth more due to potential
        youth_premium = 1.0
        if age <= 20:
            youth_premium = 1.25  # 25% premium for 18-20 year olds
        elif age <= 22: 
            youth_premium = 1.18  # 18% premium for 21-22 year olds
        else:  # age 23
            youth_premium = 1.12  # 12% premium for 23 year olds
        predictedVal = predictedVal * youth_premium
    elif age >= 33 and predictedVal > 20_000_000:
        # 33+: decay for expensive players, but slower for elite
        years_past_33 = age - 33
        if overall >= 90:
            age_factor = math.pow(0.94, years_past_33)  # Elite: 6% per year
        else:
            age_factor = math.pow(0.88, years_past_33)  # Regular: 12% per year
        predictedVal = predictedVal * age_factor
    elif age >= 30 and predictedVal > 10_000_000:
        # 30-32: moderate decay, but slower for elite
        years_past_30 = age - 30
        if overall >= 90:
            age_factor = math.pow(0.96, years_past_30)  # Elite: 4% per year
        else:
            age_factor = math.pow(0.92, years_past_30)  # Regular: 8% per year
        predictedVal = predictedVal * age_factor
    
    # Elite player prime years value boost
    # ONLY applies to undervalued elite players (below €150M for 90+ OVR)
    # Prevents runaway compounding for already peak-valued players
    if overall >= 90 and 21 <= age <= 28 and predictedVal < 150_000_000:
        # Graduated boost based on overall
        if overall >= 93:
            elite_boost = 1.20  # 20% boost for 93+ OVR
        elif overall >= 91:
            elite_boost = 1.15  # 15% boost for 91-92 OVR
        else:
            elite_boost = 1.10  # 10% boost for 90 OVR
        predictedVal = predictedVal * elite_boost
    elif overall >= 90 and 29 <= age <= 30 and predictedVal < 150_000_000:
        # Age 29-30: smaller boost
        if overall >= 93:
            elite_boost = 1.10
        elif overall >= 91:
            elite_boost = 1.06
        else:
            elite_boost = 1.03
        predictedVal = predictedVal * elite_boost
    
    # Sanity check: value shouldn't increase when rating drops
    if ratingChange < 0 and predictedVal > valueEur:
        predictedVal = valueEur * 0.97  # Allow max 3% decline when rating drops
    
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
    
    # ALWAYS preserve original potential from year 0
    age = currentDf['age_fifa'].iloc[0]
    current_overall = results.get('predictOverall', currentDf['overall'].iloc[0])
    original_potential = currentDf.get('original_potential', currentDf['potential'].iloc[0])
    if isinstance(original_potential, pd.Series):
        original_potential = original_potential.iloc[0]
    
    # Never update potential - always use original from year 0
    nextDf['potential'] = original_potential
    
    # Preserve original_potential for next iteration
    nextDf['original_potential'] = original_potential
    
    nextDf['value_eur'] = results.get('predictValue', currentDf['value_eur'].iloc[0] if 'value_eur' in currentDf.columns else 0)
    
    # 3. Use predicted minutes for next season if current minutes are low
    databaseMinutes = currentDf['Playing Time_Min'].iloc[0]
    predictedMinutes = results.get('predictedMinutes', databaseMinutes)
    
    # For players with low minutes, transition to predicted minutes over time
    if databaseMinutes < 900:  # Less than 10 full games
        # Use predicted minutes but cap reasonably
        effectiveMinutes = min(float(predictedMinutes), 2500)
    else:
        effectiveMinutes = databaseMinutes
    
    nextDf['Playing Time_Min'] = effectiveMinutes
    nextDf['Playing Time_90s'] = effectiveMinutes / 90 if effectiveMinutes > 0 else 0
    
    # Use effective minutes to calculate per-90 stats from predicted totals
    if effectiveMinutes > 0:
        nextDf['Per 90 Minutes_Gls'] = (results.get('predictedGoals', 0) / effectiveMinutes) * 90
        nextDf['Per 90 Minutes_Ast'] = (results.get('predictedAssists', 0) / effectiveMinutes) * 90
        nextDf['Per 90 Minutes_G+A'] = nextDf['Per 90 Minutes_Gls'] + nextDf['Per 90 Minutes_Ast']
        nextDf['Per 90 Minutes_Tackles_Tkl'] = (results.get('predictedTackles', 0) / effectiveMinutes) * 90
        nextDf['Per 90 Minutes_Int'] = (results.get('predictedInterceptions', 0) / effectiveMinutes) * 90
        nextDf['Per 90 Minutes_KP'] = (results.get('predictedKeyPasses', 0) / effectiveMinutes) * 90
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
    
    # Track last rating change to detect oscillation patterns
    nextDf['last_rating_change'] = ratingChange
    
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
    
    # Get position and rating for minimum G/A enforcement
    position = dfStats['pos'].iloc[0] if 'pos' in dfStats.columns else ''
    player_positions = dfStats['player_positions'].iloc[0] if 'player_positions' in dfStats.columns else ''
    
    # Also check player object for position data (fallback)
    if player is not None and not player_positions:
        player_positions = getattr(player, 'player_positions', '') or ''
    
    current_overall = float(dfStats['overall'].iloc[0])
    
    # Use ML predictions
    g90_ml = float(g90) if g90 is not None else 0.0
    a90_ml = float(a90) if a90 is not None else 0.0
    
    # Determine position type - check both pos and player_positions
    # Priority: CAM/attacking mid > winger > forward > midfielder (for G/A expectations)
    combined_position = f"{position} {player_positions}".upper()
    is_attacking_mid = any(x in combined_position for x in ['CAM', 'AM'])
    is_winger = any(x in combined_position for x in ['LW', 'RW', 'LM', 'RM'])
    is_forward = any(x in combined_position for x in ['FW', 'ST', 'CF']) and not is_attacking_mid
    is_midfielder = any(x in combined_position for x in ['CM', 'CDM']) and not is_attacking_mid and not is_winger
    
    # Calculate expected G/A per 90 based on rating and position
    # This gives us a target to compare against ML predictions
    # Uses tiered rates to prevent mid-tier players from getting elite numbers
    expected_g90 = 0.0
    expected_a90 = 0.0
    
    # Use PREDICTED overall + rating change for expected rates
    # FixOverall() will later adjust the rating, so we need to account for that
    # Use current + predicted change as best estimate of final overall
    predicted_ovr_raw = results.get('predictOverall', current_overall)
    predicted_change_raw = results.get('predictRatingChange', 0)
    predicted_change = float(predicted_change_raw) if predicted_change_raw is not None else 0
    
    # Best estimate: current overall + the predicted change (before FixOverall adjusts it)
    # This better approximates what the final overall will be after FixOverall()
    estimated_final_ovr = current_overall + predicted_change
    current_ovr = float(estimated_final_ovr) if estimated_final_ovr is not None else current_overall
    
    # Linear scaling with overall - each OVR point increases G/A consistently
    # print(f"[NEW CODE v2.0] Calculating expected G/A for {position} {player_positions} at {current_ovr} OVR")
    if is_forward:
        # Forwards: 70 OVR = 0.15/0.08, 95 OVR = 0.70/0.35 (goals-focused)
        expected_g90 = 0.15 + (current_ovr - 70) * 0.022  # +0.022 per OVR
        expected_a90 = 0.08 + (current_ovr - 70) * 0.0108  # +0.0108 per OVR
    elif is_winger:
        # Wingers: 70 OVR = 0.20/0.18, 95 OVR = 0.65/0.60 (balanced)
        expected_g90 = 0.20 + (current_ovr - 70) * 0.018  # +0.018 per OVR
        expected_a90 = 0.18 + (current_ovr - 70) * 0.0168  # +0.0168 per OVR
    elif is_attacking_mid:
        # CAMs: 70 OVR = 0.20/0.24, 95 OVR = 0.60/0.70 (assists-focused)
        expected_g90 = 0.20 + (current_ovr - 70) * 0.016  # +0.016 per OVR
        expected_a90 = 0.24 + (current_ovr - 70) * 0.0184  # +0.0184 per OVR
    elif is_midfielder:
        # CMs: 70 OVR = 0.04/0.08, 95 OVR = 0.30/0.425 (support)
        expected_g90 = 0.04 + (current_ovr - 70) * 0.0104  # +0.0104 per OVR
        expected_a90 = 0.08 + (current_ovr - 70) * 0.0138  # +0.0138 per OVR
    
    # Start with ML predictions
    g90_value = g90_ml
    a90_value = a90_ml
    
    # Age-based G/A adjustments (creates natural career arc)
    # Apply BEFORE floor logic so floors represent minimum at any age
    age = int(dfStats['age_fifa'].iloc[0]) if 'age_fifa' in dfStats.columns else 25
    
    age_multiplier = 1.0
    if is_forward or is_winger or is_attacking_mid or is_midfielder:
        # Career arc multipliers - creates natural peak around 25-26
        if age <= 19:
            age_multiplier = 0.88
        elif age == 20:
            age_multiplier = 0.92
        elif age == 21:
            age_multiplier = 0.95
        elif age == 22:
            age_multiplier = 0.97
        elif age == 23:
            age_multiplier = 0.99
        elif age == 24:
            age_multiplier = 1.01
        elif age in [25, 26]:
            # Peak years
            age_multiplier = 1.04
        elif age == 27:
            age_multiplier = 1.02
        elif age == 28:
            age_multiplier = 1.00
        elif age == 29:
            age_multiplier = 0.97
        elif age == 30:
            age_multiplier = 0.94
        elif age == 31:
            age_multiplier = 0.91
        elif age >= 32 and age <= 34:
            age_multiplier = 0.88 - (age - 32) * 0.03
        else:
            # 35+
            age_multiplier = 0.79 - (age - 35) * 0.04
        
        g90_value *= age_multiplier
        a90_value *= age_multiplier
    
    # Rating change affects G/A - good seasons boost output, bad seasons reduce it
    rating_change_raw = results.get('predictRatingChange', 0)
    rating_multiplier = 1.0
    if rating_change_raw is not None:
        rating_change = float(rating_change_raw)
        # +1 OVR = +5% G/A, -1 OVR = -5% G/A (capped at ±15%)
        rating_multiplier = 1.0 + (rating_change * 0.05)
        rating_multiplier = max(0.85, min(1.15, rating_multiplier))  # Cap between 85% and 115%
        g90_value *= rating_multiplier
        a90_value *= rating_multiplier
    
    # NOW apply floor logic AFTER age multiplier but using age-only adjustment
    # Floors represent talent level at this age, independent of seasonal form (rating change)
    # This prevents floor miscalculation when FixOverall() later adjusts the rating
    if is_forward or is_winger or is_attacking_mid or is_midfielder:
        # Calculate age-adjusted expected rates (base talent scaled by career stage)
        age_adjusted_expected_g90 = expected_g90 * age_multiplier
        age_adjusted_expected_a90 = expected_a90 * age_multiplier
        
        # Apply floors: 85% of expected for goals, 80% for assists
        # Tighter than before to ensure quality players hit closer to expected rates
        g90_floor = age_adjusted_expected_g90 * 0.85
        a90_floor = age_adjusted_expected_a90 * 0.80
        
        # Enforce minimums AFTER rating multiplier applied to ML prediction
        # This allows good form to boost above floor, bad form to drop to floor
        if g90_value < g90_floor:
            g90_value = g90_floor
        if a90_value < a90_floor:
            a90_value = a90_floor
        
        # print(f"DEBUG G/A: pos={combined_position}, start_ovr={current_overall:.0f}, pred_ovr={current_ovr:.0f}, age={age}, g90_ml={g90_ml:.3f}, expected={expected_g90:.3f}, age_mult={age_multiplier:.2f}, rating_mult={rating_multiplier:.2f}, floor={g90_floor:.3f}, final={g90_value:.3f} | a90: expected={expected_a90:.3f}, floor={a90_floor:.3f}, final={a90_value:.3f}")
    
    # Get predicted minutes for total stat calculations
    predicted_minutes = results.get('predictMin', playing_time_min)
    predicted_minutes = float(predicted_minutes) if predicted_minutes is not None else playing_time_min
    
    # For players with very low current minutes, use predicted minutes for total calculations
    # This fixes young players who had limited playing time but are expected to play more
    minutes_for_totals = playing_time_min
    if playing_time_min < 900:  # Less than 10 full games
        # Use predicted minutes but cap at reasonable value to avoid inflation
        minutes_for_totals = min(predicted_minutes, 2500)  # Cap at ~28 full games
    
    results['predictedGoals'] = g90_value * (minutes_for_totals / 90) if minutes_for_totals > 0 else 0.0
    results['predictedAssists'] = a90_value * (minutes_for_totals / 90) if minutes_for_totals > 0 else 0.0
    
    # print(f"FINAL CALC: g90={g90_value:.3f} × ({minutes_for_totals}/90) = {results['predictedGoals']:.2f} goals | a90={a90_value:.3f} × ({minutes_for_totals}/90) = {results['predictedAssists']:.2f} assists")
    results['predictedInterceptions'] = (float(int90) if int90 is not None else 0.0) * (minutes_for_totals / 90) if minutes_for_totals > 0 else 0.0
    results['predictedTackles'] = (float(tkl90) if tkl90 is not None else 0.0) * (minutes_for_totals / 90) if minutes_for_totals > 0 else 0.0
    results['predictedKeyPasses'] = (float(key90) if key90 is not None else 0.0) * (minutes_for_totals / 90) if minutes_for_totals > 0 else 0.0
    results['predictedPotential'] = results.pop('predictPotential', 0.0)
    results['predictedMinutes'] = predicted_minutes

    # POST PREDICTION ADJUSTMENTS

    momentum = float(dfStats['rating_momentum'].iloc[0])
    ratingChange_val = results.get('predictRatingChange')
    ratingChange = float(ratingChange_val) if ratingChange_val is not None else 0.0  # actual predicted
    current_overall = float(math.ceil(float(dfStats['overall'].iloc[0])))        
    
    # Get age and potential for youth player boost
    age_fifa_val = int(dfStats['age_fifa'].iloc[0])
    original_potential = dfStats.get('original_potential', dfStats['potential'].iloc[0])
    if isinstance(original_potential, pd.Series):
        original_potential = original_potential.iloc[0]
    player_potential = float(original_potential)
    
    if momentum > 10:
        # Rating Momentum Fix (if momentum is very high, give revert negatives)
        results['predictRatingChange'], results['predictOverall'] = FixMomentum(momentum, ratingChange, current_overall)
    else:
        # Else fix overall & change (rounding) with youth boost
        predicted_ovr = results.get('predictOverall', current_overall)
        rating_change = (predicted_ovr) - current_overall # calculated using new - old
        results['predictOverall'], results['predictRatingChange'] = FixOverall(current_overall, rating_change, age_fifa_val, player_potential)
    
     # value fix | For old players and improper increase/decrease
    # Use value from dataframe (which gets updated each year) instead of player object
    player_value_eur = dfStats['value_eur'].iloc[0] if 'value_eur' in dfStats.columns else (getattr(player, 'value_eur', None) if player else None)
    age_fifa_val = int(dfStats['age_fifa'].iloc[0])
    current_overall_for_value = float(dfStats['overall'].iloc[0])
    predictedValueEur = int(results.get('predictValue'))
    results['predictValue'] = FixValue(age_fifa_val, player_value_eur, results['predictRatingChange'], predictedValueEur, current_overall_for_value)

    # Attribute fix | update dfStats with fixed attributes after predictions
    position = dfStats['pos'].iloc[0]
    results = FixAttributes(results, position)
    
    
    return results