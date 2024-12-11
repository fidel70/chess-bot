import chess
from typing import Tuple, Optional

class MaterialEvaluator:
    def __init__(self):
        # Valores estándar de las piezas
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
        
        # Evaluamos desde la perspectiva de quien mueve
        perspective = 1 if board.turn == chess.WHITE else -1
        
        for piece_type in chess.PIECE_TYPES:
            # Piezas blancas
            score += len(board.pieces(piece_type, chess.WHITE)) * self.piece_values[piece_type]
            # Piezas negras
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.piece_values[piece_type]
            
        # Multiplicamos por la perspectiva del jugador actual
        return score * perspective

class MinimaxEngine:
    def __init__(self, evaluator, depth):
        self.evaluator = evaluator
        self.max_depth = depth

    def search(self, board: chess.Board) -> Tuple[Optional[chess.Move], float]:
        best_value = float('-inf')
        best_move = None

        for move in board.legal_moves:
            board.push(move)
            value = -self._minimax(board, self.max_depth - 1)
            board.pop()

            # Para debug
            print(f"Movimiento {board.san(move)}, valor: {value}")

            if value > best_value:
                best_value = value
                best_move = move

        return best_move, best_value

    def _minimax(self, board: chess.Board, depth: int) -> float:
        if depth == 0 or board.is_game_over():
            return self.evaluator.evaluate(board)

        max_value = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            value = -self._minimax(board, depth - 1)
            board.pop()
            max_value = max(max_value, value)
            
        return max_value