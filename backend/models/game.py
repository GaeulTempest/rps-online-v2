from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class GameState(str, Enum):
    WAITING = "waiting"
    STARTING = "starting"
    PLAYING = "playing"
    FINISHED = "finished"

class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: str = Field(index=True, unique=True)
    state: GameState = Field(default=GameState.WAITING)
    player1_id: Optional[str] = None
    player2_id: Optional[str] = None
    player1_score: int = Field(default=0)
    player2_score: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
class GameLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: str
    event_type: str  # gesture_detection, communication, game_result
    data: str  # JSON string of the log data
    timestamp: datetime = Field(default_factory=datetime.now)