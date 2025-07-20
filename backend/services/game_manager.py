from typing import Dict, List, Optional
from models.game import Game, GameState
import logging

logger = logging.getLogger(__name__)

class GameManager:
    def __init__(self):
        self.games: Dict[str, Game] = {}
        self.player_moves: Dict[str, Dict[str, str]] = {}  # room_id -> {player_id: move}
        self.player_ready: Dict[str, List[str]] = {}  # room_id -> [ready_player_ids]
        
    def create_game(self, room_id: str) -> Game:
        """Create a new game for the room"""
        game = Game(
            room_id=room_id,
            state=GameState.WAITING
        )
        self.games[room_id] = game
        self.player_moves[room_id] = {}
        self.player_ready[room_id] = []
        logger.info(f"Created game for room {room_id}")
        return game
    
    def get_game(self, room_id: str) -> Optional[Game]:
        """Get game by room ID"""
        return self.games.get(room_id)
    
    def get_game_state(self, room_id: str) -> Optional[GameState]:
        """Get current game state"""
        game = self.get_game(room_id)
        return game.state if game else None
    
    def start_game(self, room_id: str) -> bool:
        """Start the game (when 2 players joined)"""
        game = self.get_game(room_id)
        if game and game.state == GameState.WAITING:
            game.state = GameState.STARTING
            logger.info(f"Game started for room {room_id}")
            return True
        return False
    
    def start_round(self, room_id: str) -> bool:
        """Start a new round"""
        game = self.get_game(room_id)
        if game:
            game.state = GameState.PLAYING
            self.clear_moves(room_id)
            self.player_ready[room_id] = []
            logger.info(f"Round started for room {room_id}")
            return True
        return False
    
    def set_player_ready(self, room_id: str, player_id: str):
        """Mark player as ready"""
        if room_id not in self.player_ready:
            self.player_ready[room_id] = []
        
        if player_id not in self.player_ready[room_id]:
            self.player_ready[room_id].append(player_id)
            logger.info(f"Player {player_id} ready in room {room_id}")
    
    def both_players_ready(self, room_id: str) -> bool:
        """Check if both players are ready"""
        return len(self.player_ready.get(room_id, [])) >= 2
    
    def record_move(self, room_id: str, player_id: str, move: str) -> bool:
        """Record a player's move"""
        game = self.get_game(room_id)
        if not game or game.state != GameState.PLAYING:
            return False
        
        if room_id not in self.player_moves:
            self.player_moves[room_id] = {}
        
        # Only record if player hasn't moved yet this round
        if player_id not in self.player_moves[room_id]:
            self.player_moves[room_id][player_id] = move
            logger.info(f"Player {player_id} moved {move} in room {room_id}")
            return True
        
        return False
    
    def get_moves(self, room_id: str) -> Dict[str, str]:
        """Get all moves for current round"""
        return self.player_moves.get(room_id, {})
    
    def clear_moves(self, room_id: str):
        """Clear moves for next round"""
        if room_id in self.player_moves:
            self.player_moves[room_id] = {}
    
    def evaluate_moves(self, moves: Dict[str, str]) -> Dict:
        """Evaluate the round result"""
        if len(moves) < 2:
            return {"result": "timeout", "winner": None, "moves": moves}
        
        player_ids = list(moves.keys())
        move1 = moves[player_ids[0]]
        move2 = moves[player_ids[1]]
        
        # Game logic
        if move1 == move2:
            return {"result": "draw", "winner": None, "moves": moves}
        
        winning_combinations = {
            ("rock", "scissors"): player_ids[0],
            ("scissors", "paper"): player_ids[0],
            ("paper", "rock"): player_ids[0],
            ("scissors", "rock"): player_ids[1],
            ("paper", "scissors"): player_ids[1],
            ("rock", "paper"): player_ids[1]
        }
        
        winner = winning_combinations.get((move1, move2))
        
        return {
            "result": "win" if winner else "unknown",
            "winner": winner,
            "moves": moves
        }
    
    def update_scores(self, room_id: str, result: Dict):
        """Update game scores"""
        game = self.get_game(room_id)
        if not game or result["result"] != "win":
            return
        
        winner = result["winner"]
        player_ids = list(result["moves"].keys())
        
        if winner == player_ids[0]:
            game.player1_score += 1
        elif winner == player_ids[1]:
            game.player2_score += 1
        
        logger.info(f"Updated scores for room {room_id}: {game.player1_score}-{game.player2_score}")
    
    def get_scores(self, room_id: str) -> Dict[str, int]:
        """Get current scores"""
        game = self.get_game(room_id)
        if not game:
            return {}
        
        moves = self.get_moves(room_id)
        player_ids = list(moves.keys()) if moves else []
        
        if len(player_ids) >= 2:
            return {
                player_ids[0]: game.player1_score,
                player_ids[1]: game.player2_score
            }
        
        return {}
    
    def restart_game(self, room_id: str):
        """Restart game (reset state but keep scores)"""
        game = self.get_game(room_id)
        if game:
            game.state = GameState.STARTING
            self.clear_moves(room_id)
            self.player_ready[room_id] = []
            logger.info(f"Game restarted for room {room_id}")
    
    def end_game(self, room_id: str):
        """End the game"""
        game = self.get_game(room_id)
        if game:
            game.state = GameState.FINISHED
            logger.info(f"Game ended for room {room_id}")
    
    def cleanup_room(self, room_id: str):
        """Clean up room data"""
        if room_id in self.games:
            del self.games[room_id]
        if room_id in self.player_moves:
            del self.player_moves[room_id]
        if room_id in self.player_ready:
            del self.player_ready[room_id]
        logger.info(f"Cleaned up room {room_id}")