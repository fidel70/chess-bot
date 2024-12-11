import chess
from typing import Tuple, Optional, List
import time
from dataclasses import dataclass

class MaterialEvaluator:
    def __init__(self):
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
    def evaluate(self, board: chess.Board) -> float:
        """Evaluación material mejorada con perspectiva correcta"""
        if board.is_checkmate():
            return -20000 if board.turn else 20000
            
        score = 0
        perspective = 1 if board.turn == chess.WHITE else -1
        
        for piece_type in chess.PIECE_TYPES:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.piece_values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.piece_values[piece_type]
            
        return score * perspective

@dataclass
class SearchInfo:
    nodes_searched: int = 0
    positions_evaluated: int = 0
    time_spent: float = 0.0
    depth_reached: int = 0

class MinimaxEngine:
    def __init__(self, evaluator, depth=3):
        self.evaluator = evaluator
        self.max_depth = depth
        self.search_info = SearchInfo()
        
    def search(self, board: chess.Board) -> Tuple[Optional[chess.Move], float]:
        """Búsqueda del mejor movimiento usando alpha-beta pruning."""
        self.search_info = SearchInfo()
        start_time = time.time()
        
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        moves = sorted(
            board.legal_moves,
            key=lambda move: board.is_capture(move),
            reverse=True
        )
        
        for move in moves:
            board.push(move)
            self.search_info.nodes_searched += 1
            value = -self._alpha_beta(board, self.max_depth - 1, -beta, -alpha, False)
            board.pop()
            
            if value > best_value:
                best_value = value
                best_move = move
                alpha = value
                
        self.search_info.time_spent = time.time() - start_time
        return best_move, best_value
        
    def _alpha_beta(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        if depth == 0 or board.is_game_over():
            self.search_info.positions_evaluated += 1
            return self.evaluator.evaluate(board)
            
        moves = sorted(
            board.legal_moves,
            key=lambda move: board.is_capture(move),
            reverse=True
        )
        
        if maximizing:
            value = float('-inf')
            for move in moves:
                board.push(move)
                self.search_info.nodes_searched += 1
                value = max(value, -self._alpha_beta(board, depth - 1, -beta, -alpha, False))
                board.pop()
                
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float('inf')
            for move in moves:
                board.push(move)
                self.search_info.nodes_searched += 1
                value = min(value, -self._alpha_beta(board, depth - 1, -beta, -alpha, True))
                board.pop()
                
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value