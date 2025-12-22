from typing import Optional
from sqlmodel import Field, SQLModel

# Player Data - Corresponds to current_players_2425.csv
class PlayerBase(SQLModel):
    # Identity
    name: str
    short_name: str
    long_name: str
    nationality_name: str
    age_fifa: int
    
    # FIFA Attributes
    player_positions: str
    overall: int
    potential: int
    value_eur: Optional[float] = None
    wage_eur: Optional[float] = None
    
    # Physical
    height_cm: int
    weight_kg: int
    preferred_foot: str
    weak_foot: int
    skill_moves: int
    
    # FIFA Stats
    pace: int
    shooting: int
    passing: int
    dribbling: int
    defending: int
    physic: int
    
    # Club Info
    club_name: Optional[str] = None
    league_name: Optional[str] = None
    club_jersey_number: Optional[int] = None
    
    # FBRef Stats (Per 90)
    playing_time_min: Optional[float] = None
    playing_time_90s: Optional[float] = None
    gls_per90: Optional[float] = None
    ast_per90: Optional[float] = None
    g_plus_a_per90: Optional[float] = None
    g_minus_pk_per90: Optional[float] = None
    xg_per90: Optional[float] = None
    xag_per90: Optional[float] = None
    tkl_per90: Optional[float] = None
    int_per90: Optional[float] = None
    kp_per90: Optional[float] = None
    prgp_per90: Optional[float] = None
    
    # Standard Stats
    sh_per90: Optional[float] = None
    sot_percent: Optional[float] = None
    total_cmp_percent: Optional[float] = None
    sca_per90: Optional[float] = None
    
    # Engineered Features
    age_squared: Optional[int] = None
    is_youth: Optional[int] = None
    is_prime: Optional[int] = None
    is_veteran: Optional[int] = None
    is_elite: Optional[int] = None
    is_good: Optional[int] = None
    is_average: Optional[int] = None
    
    # Statistical Features
    wage_zscore: Optional[float] = None
    wage_percentile: Optional[float] = None
    value_zscore: Optional[float] = None
    goals_vs_xg: Optional[float] = None
    
    # Position Flags
    is_forward: Optional[int] = None
    is_midfield: Optional[int] = None
    is_defense: Optional[int] = None
    
    # Lag Features (Previous Season)
    overall_lag1: Optional[float] = None
    age_lag1: Optional[float] = None
    playing_time_min_lag1: Optional[float] = None
    gls_per90_lag1: Optional[float] = None
    ast_per90_lag1: Optional[float] = None
    g_plus_a_per90_lag1: Optional[float] = None
    xg_per90_lag1: Optional[float] = None
    value_eur_lag1: Optional[float] = None
    
    # Trend Features
    has_prior_season: Optional[int] = None
    rating_momentum: Optional[float] = None
    goals_trend: Optional[float] = None
    minutes_trend: Optional[float] = None

class Player(PlayerBase, table=True):
    __tablename__ = "players"
    __table_args__ = {"schema": "fut"}
    id: int | None = Field(default=None, primary_key=True)

class PlayerRead(PlayerBase):
    id: int