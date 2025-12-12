from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlmodel import Session
from typing import List

from .database import create_db_and_tables, get_session
from . import models
from .models import Player, PlayerRead, PlayerBase

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database and tables...")
    create_db_and_tables()
    print("Database ready.")
    yield
# ...existing code...
app = FastAPI(
    title="FUT Prediction API",
    version="0.1.0",
    description="API for player rating and market value predictions.",
    lifespan=lifespan  # attach lifespan so tables get created at startup
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FUT Prediction API!"}

@app.post("/players/", response_model=PlayerRead)
def create_player(*, session: Session = Depends(get_session), player: PlayerBase):
    """
    Creates a new Player record in the database.
    
    * session: The database session dependency (automatically manages connection).
    * player: The incoming data, validated against the PlayerBase model.
    """
    # 1. Create a full Player object using the validated data
    db_player = Player.model_validate(player)

    # 2. Add to session and commit to the database (RDS)
    session.add(db_player)
    session.commit()
    session.refresh(db_player) # Get the DB-generated ID back

    return db_player

@app.get("/players/", response_model=List[PlayerRead])
def read_players(
    *, 
    session: Session = Depends(get_session), 
    offset: int = 0, 
    limit: int = 10
):
    """Reads a list of players from the database."""
    
    players = session.query(Player).offset(offset).limit(limit).all()
    
    return players