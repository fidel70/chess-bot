from typing import Optional, Tuple
import chess
import time

class MinimalEvaluator:
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
        """
        Evaluación puramente material.
        Retorna un valor positivo si las blancas están mejor, negativo si las negras están mejor.
        """
        if board.is_checkmate():
            return -20000 if board.turn else 20000
            
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
            
        score = 0
        for piece_type in self.piece_values:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.piece_values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.piece_values[piece_type]
        
        return score

class MinimalEngine:
    def __init__(self, evaluator, depth=3):
        self.evaluator = evaluator
        self.max_depth = depth
        
    def search(self, board: chess.Board) -> Tuple[chess.Move, float]:
        """Búsqueda del mejor movimiento."""
        start_time = time.time()
        
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Primero evaluamos capturas
        for move in board.legal_moves:
            if board.is_capture(move):
                board.push(move)
                value = -self._negamax(board, self.max_depth - 1, -beta, -alpha)
                board.pop()
                
                if value > alpha:
                    alpha = value
                    best_move = move
        
        # Si no hay capturas o no encontramos mejora, evaluamos todos los movimientos
        if best_move is None:
            for move in board.legal_moves:
                board.push(move)
                value = -self._negamax(board, self.max_depth - 1, -beta, -alpha)
                board.pop()
                
                if value > alpha:
                    alpha = value
                    best_move = move
        
        print(f"Tiempo de búsqueda: {time.time() - start_time:.2f} segundos")
        return best_move, alpha
    
    def _negamax(self, board: chess.Board, depth: int, alpha: float, beta: float) -> float:
        """Implementación negamax con poda alfa-beta."""
        
        # Verificar fin de juego
        if board.is_game_over():
            return self.evaluator.evaluate(board)
            
        # Si llegamos a la profundidad máxima
        if depth == 0:
            return -self.evaluator.evaluate(board)
        
        # Intentar capturas primero
        value = float('-inf')
        for move in board.legal_moves:
            if board.is_capture(move):
                board.push(move)
                value = max(value, -self._negamax(board, depth - 1, -beta, -alpha))
                board.pop()
                
                alpha = max(alpha, value)
                if alpha >= beta:
                    return alpha
        
        # Si no hay capturas o no encontramos mejora, evaluar todos los movimientos
        if value == float('-inf'):
            for move in board.legal_moves:
                board.push(move)
                value = max(value, -self._negamax(board, depth - 1, -beta, -alpha))
                board.pop()
                
                alpha = max(alpha, value)
                if alpha >= beta:
                    return alpha
        
        return value

def test_engine():
    """Función para probar el motor."""
    board = chess.Board()
    evaluator = MinimalEvaluator()
    engine = MinimalEngine(evaluator, depth=3)
    
    # Probar captura simple
    test_fen = "rnbqkbnr/ppp2ppp/8/3Np3/4P3/8/PPPP1PPP/RNBQKB1R b KQkq - 0 3"
    board.set_fen(test_fen)
    
    move, value = engine.search(board)
    print(f"Posición: {test_fen}")
    print(f"Mejor movimiento encontrado: {move}")
    print(f"Valor: {value}")
    
    return engine

# Crear y probar el motor
if __name__ == "__main__":
    engine = test_engine()
