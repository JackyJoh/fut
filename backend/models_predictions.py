from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from typing import Optional

class PlayerPrediction(SQLModel, table=True):
    """Pre-computed predictions stored in database for instant retrieval"""
    __tablename__ = "player_predictions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="players.id", unique=True, index=True)
    
    # Store entire statsLibrary as JSON (9 years of predictions)
    stats_library: dict = Field(sa_column=Column(JSON))
    
    # Cache key stats for quick filtering (from year 1)
    year1_overall: int
    year1_value: int
    year1_goals: float
    year1_assists: float
    
    # Metadata
    computed_at: Optional[str] = None  # Timestamp of when predictions were computed
