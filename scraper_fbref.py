import pandas as pd
from pyparsing import col
import soccerdata as sd
import os

# --- Configuration ---
# Create the directory if it doesn't exist
OUTPUT_DIR = 'data/raw'
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'keeper_stats.csv')

# Define the leagues to scrape (expanded beyond Big 5 for maximum volume)
LEAGUE_CODES = ['Big 5 European Leagues Combined',
                'POR-Primeira Liga',    
                'NED-Eredivisie',
                'TUR-Super Lig',
                'USA-MLS',        
                'BRA-Serie A']

# Define the range of seasons to scrape
# Data from Fifa 15 to Fifa 25 (2014/15-2024/25 seasons)
SEASONS = [f"{y}-{y+1}" for y in range(2014, 2025)]

print(f"Targeting {len(LEAGUE_CODES)} leagues over {len(SEASONS)} seasons.")
print(f"Output will be saved to: {OUTPUT_FILE}\n")


# 3a. Initialize the Scraper Object
# enable caching to stabilize the high-volume scrape.
scraper = sd.FBref(leagues=LEAGUE_CODES, seasons=SEASONS, no_cache=False)

# 3b. Execute the Data Retrieval
print("--- Starting Bulk Data Retrieval from FBref. This may take a while. ---")

try:
    df_performance = scraper.read_player_season_stats(
       stat_type='keeper',  # Standard stats (Goals, Assists, etc.)
    )
    # Flatten possible MultiIndex columns into single strings
    df_performance.columns = [
        "_".join(str(c) for c in col if c).strip()
        if isinstance(col, tuple) else str(col)
        for col in df_performance.columns
    ]
    
    # Reset index to make index columns regular columns
    df_performance = df_performance.reset_index()
    
except Exception as e:
    print(f"An error occurred during scraping: {e}")
    print("Scraping failed. Check your internet connection and verify 'soccerdata' installation.")
    df_performance = pd.DataFrame()

print("--- Data Retrieval Complete. ---")


# Verification and Saving
if not df_performance.empty:
    # 4a. Basic Verification Check
    print(f"\nTotal Player-Season Rows Collected: {len(df_performance):,}")
    
    # Debug: Print available columns to understand structure
    print(f"\nAvailable columns: {df_performance.columns.tolist()[:10]}...")
    
    # Find the player column (it might be named differently after flattening)
    player_col = next((col for col in df_performance.columns if 'player' in col.lower()), None)
    if player_col:
        print(f"Number of Unique Players: {df_performance[player_col].nunique():,}")
        df_performance.to_csv(OUTPUT_FILE, index=False)

    # Critical Columns Check for ML Feasibility
    # Note: After flattening, column names might have prefixes
    critical_cols = {
        'min': None,
        'gls': None,
        'ast': None,
        'xg': None,
        'xa': None
    }
    
    for col in df_performance.columns:
        col_lower = col.lower()
        for key in critical_cols:
            if key in col_lower and critical_cols[key] is None:
                critical_cols[key] = col
    
    missing_cols = [key for key, val in critical_cols.items() if val is None]
    
    if not missing_cols:
        print("Success: All critical ML columns (Minutes, Goals, xG, etc.) are present.")
    else:
        print(f"Warning: Could not find columns for: {missing_cols}")

    # 4b. Save the Raw Data
    df_performance.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Raw data saved to '{OUTPUT_FILE}'")

    # Display the first few rows for visual inspection
    print("\nData Head (Preview):")
    # Use the found column names
    display_cols = [col for col in df_performance.columns if any(x in col.lower() for x in ['season', 'comp', 'player', 'pos', 'min', 'gls', 'ast', 'xg', 'xa'])][:9]
    if display_cols:
        print(df_performance[display_cols].head())
    else:
        print(df_performance.head())
else:
    print("\nNo data was collected. Cannot proceed.")