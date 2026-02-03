from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from typing import List
from predictor import predictNineYears, predictStats
from model_utils import get_players_by_name, get_player_by_id, player_to_features, get_players_by_name

from database import create_db_and_tables, get_session
from models import Player, PlayerRead, PlayerPrediction

# Mangum for AWS Lambda
from mangum import Mangum

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database and tables...")
    create_db_and_tables()
    print("Database ready.")
    yield

app = FastAPI(
    title="FUT Prediction API",
    version="0.1.0",
    description="API for player rating and market value predictions.",
    lifespan=lifespan  # attach lifespan so tables get created at startup
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FUT Prediction API!"}

@app.get("/searchPlayers", response_model=List[PlayerRead])
def searchPlayers(name: str, session: Session = Depends(get_session)):
    """
    Search for players by name (partial match) and return a list of PlayerRead objects.
    """
    players = get_players_by_name(session, name)
    return players

@app.get("/predictPlayer/{playerID}")
def predictPlayer(playerID: int, session: Session = Depends(get_session)):
    """
    Get pre-computed predictions for a player from database (instant).
    """
    try:
        # Get cached prediction
        cached = session.exec(
            select(PlayerPrediction).where(PlayerPrediction.player_id == playerID)
        ).first()
        
        if not cached:
            return {"error": f"Predictions not found for player ID {playerID}"}
        
        # Get player info
        player = get_player_by_id(session, playerID)
        
        return {
            "player": player,
            "statsLibrary": cached.stats_library
        }
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}
        return {"error": f"Prediction failed: {str(e)}"}

# Lambda handler
handler = Mangum(app, lifespan="off")

@app.get("/health")
def health_check():
    return {"status": "ok"}