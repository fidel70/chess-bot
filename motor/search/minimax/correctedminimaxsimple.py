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
        if board.turn == chess.WHITE:
            best_value = float('-inf')
            # Para las blancas, buscamos el máximo
            for move in board.legal_moves:
                board.push(move)
                value = self._minimax(board, self.max_depth - 1, float('-inf'), float('inf'), False)
                print(f"Evaluando {board.san(move)}, Valor: {value}")
                board.pop()
                
                if value > best_value:
                    best_value = value
                    best_move = move
        else:
            best_value = float('inf')
            # Para las negras, buscamos el mínimo
            for move in board.legal_moves:
                board.push(move)
                value = self._minimax(board, self.max_depth - 1, float('-inf'), float('inf'), True)
                print(f"Evaluando {board.san(move)}, Valor: {value}")
                board.pop()
                
                if value < best_value:
                    best_value = value
                    best_move = move
        
        self.search_info.time_spent = time.time() - start_time
        return best_move, best_value

    def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """Algoritmo minimax con poda alfa-beta."""
        self.search_info.nodes_searched += 1
        
        if depth == 0 or board.is_game_over():
            self.search_info.positions_evaluated += 1
            return self.evaluator.evaluate(board)
        
        if maximizing:
            value = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                value = max(value, self._minimax(board, depth - 1, alpha, beta, False))
                board.pop()
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = float('inf')
            for move in board.legal_moves:
                board.push(move)
                value = min(value, self._minimax(board, depth - 1, alpha, beta, True))
                board.pop()
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def _order_moves(self, board: chess.Board) -> List[chess.Move]:
        """Ordenamiento simple de movimientos."""
        moves = []
        for move in board.legal_moves:
            score = 0
            # Priorizar capturas
            if board.is_capture(move):
                score += 1000  # Aumentado para priorizar capturas
            # Priorizar promociones
            if move.promotion:
                score += 900
            # Priorizar jaques
            if board.gives_check(move):
                score += 500
            moves.append((move, score))
        
        moves.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in moves]
