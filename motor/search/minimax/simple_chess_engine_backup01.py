from typing import Tuple, Optional, List
import chess
import time
from dataclasses import dataclass

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
        
        # Ordenar movimientos: capturas primero
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
            
            # Para debug
            print(f"Evaluando {board.san(move)}: {value}")
            
            if value > best_value:
                best_value = value
                best_move = move
                alpha = value
                
        self.search_info.time_spent = time.time() - start_time
        return best_move, best_value
        
    def _alpha_beta(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """Implementación recursiva de alpha-beta pruning."""
        if depth == 0 or board.is_game_over():
            self.search_info.positions_evaluated += 1
            return self.evaluator.evaluate(board)
            
        # Ordenar movimientos para mejor poda
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
                    break  # Beta cut-off
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
                    break  # Alpha cut-off
            return value