from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: str = Field(index=True, unique=True)
    username: Optional[str] = None
    total_games: int = Field(default=0)
    total_wins: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)

class PlayerMove(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: str
    player_id: str
    move: str  # rock, paper, scissors
    round_number: int
    timestamp: datetime = Field(default_factory=datetime.now)