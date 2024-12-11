from typing import Optional, Tuple, List
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
        
    def search(self, board: chess.Board) -> Tuple[chess.Move, float]:
        """Búsqueda del mejor movimiento."""
        self.search_info = SearchInfo()
        start_time = time.time()
        
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Para cada movimiento en el nivel superior
        for move in list(board.legal_moves):
            board.push(move)
            # El oponente minimiza
            value = -self._minimax(board, self.max_depth - 1, -beta, -alpha)
            board.pop()
            
            if value > best_value:
                best_value = value
                best_move = move
                alpha = value
                
        self.search_info.time_spent = time.time() - start_time
        return best_move, best_value

    def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float) -> float:
        """Algoritmo minimax con poda alfa-beta."""
        self.search_info.nodes_searched += 1
        
        # Verificar fin de juego
        if board.is_game_over():
            if board.is_checkmate():
                return -10000
            return 0
            
        # Si llegamos a la profundidad máxima
        if depth == 0:
            self.search_info.positions_evaluated += 1
            return 
            self.evaluator.evaluate(board)
            
        value = float('-inf')
        
        # Para cada movimiento legal
        for move in board.legal_moves:
            board.push(move)
            value = max(value, self._minimax(board, depth - 1, -beta, -alpha))
            board.pop()
            
            alpha = max(alpha, value)
            if alpha >= beta:
                break
                
        return value

    def _order_moves(self, board: chess.Board) -> List[chess.Move]:
        """Ordenamiento simple de movimientos."""
        moves = []
        for move in board.legal_moves:
            score = 0
            # Priorizar capturas
            if board.is_capture(move):
                score += 100
            # Priorizar promociones
            if move.promotion:
                score += 200
            # Priorizar jaques
            if board.gives_check(move):
                score += 50
            moves.append((move, score))
        
        # Ordenar movimientos por puntuación
        moves.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in moves]
