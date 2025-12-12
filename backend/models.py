from typing import Optional
from sqlmodel import Field, SQLModel

class PlayerBase(SQLModel):
    full_name: str
    birth_date: str 
    nationality: str
    position_main: str

class Player(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    full_name: str
    birth_date: str
    nationality: str
    position_main: str

class PlayerRead(PlayerBase):
    id: int