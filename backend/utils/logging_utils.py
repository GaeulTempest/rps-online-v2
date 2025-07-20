import json
import logging
from datetime import datetime
from typing import Optional

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('rps_game.log'),
            logging.StreamHandler()
        ]
    )

def log_gesture_detection(player_id: str, detected_gesture: str, confidence: float, processing_time_ms: float):
    """Log gesture detection event as per BAB III format"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "player_id": player_id,
        "detected_gesture": detected_gesture,
        "confidence": confidence,
        "processing_time_ms": processing_time_ms
    }
    
    logger = logging.getLogger("gesture_detection")
    logger.info(f"GESTURE_DETECTION: {json.dumps(log_data)}")

def log_communication(event_type: str, game_id: str, latency_ms: float, payload_size_bytes: int):
    """Log communication event as per BAB III format"""
    log_data = {
        "event_type": event_type,
        "game_id": game_id,
        "latency_ms": latency_ms,
        "payload_size_bytes": payload_size_bytes,
        "timestamp": datetime.now().isoformat()
    }
    
    logger = logging.getLogger("communication")
    logger.info(f"COMMUNICATION: {json.dumps(log_data)}")

def log_game_result(game_id: str, player1_move: str, player2_move: str, winner: Optional[str], round_duration_ms: float):
    """Log game result event as per BAB III format"""
    log_data = {
        "game_id": game_id,
        "player1_move": player1_move,
        "player2_move": player2_move,
        "winner": winner,
        "round_duration_ms": round_duration_ms,
        "timestamp": datetime.now().isoformat()
    }
    
    logger = logging.getLogger("game_result")
    logger.info(f"GAME_RESULT: {json.dumps(log_data)}")

def log_system_performance(cpu_usage: float, memory_usage: float, frame_rate: float):
    """Log system performance metrics"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "cpu_usage_percent": cpu_usage,
        "memory_usage_mb": memory_usage,
        "frame_rate_fps": frame_rate
    }
    
    logger = logging.getLogger("system_performance")
    logger.info(f"SYSTEM_PERFORMANCE: {json.dumps(log_data)}")

def log_connection_event(event_type: str, player_id: str, room_id: str, success: bool = True):
    """Log connection related events"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,  # connect, disconnect, reconnect
        "player_id": player_id,
        "room_id": room_id,
        "success": success
    }
    
    logger = logging.getLogger("connection")
    logger.info(f"CONNECTION: {json.dumps(log_data)}")