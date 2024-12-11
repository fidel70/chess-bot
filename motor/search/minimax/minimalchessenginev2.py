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
    
    def evaluate(self, board: chess.Board) -> int:
        """Evaluación puramente material."""
        if board.is_checkmate():
            return -20000 if board.turn else 20000
            
        if board.is_stalemate():
            return 0
            
        score = 0
        # Contar material
        for piece_type in self.piece_values:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.piece_values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.piece_values[piece_type]
        
        # Retornamos el score desde la perspectiva del lado que mueve
        return score

class MinimalEngine:
    def __init__(self, depth=3):
        self.evaluator = MinimalEvaluator()
        self.max_depth = depth
        
    def search(self, board: chess.Board) -> Tuple[Optional[chess.Move], float]:
        self.nodes = 0  # Para debug
        
        # Buscar capturas primero
        best_move = None
        best_value = float('-inf')
        
        # Ordenar movimientos - capturas primero
        moves = list(board.legal_moves)
        moves.sort(key=lambda move: 10000 if board.is_capture(move) else 0, reverse=True)
        
        for move in moves:
            board.push(move)
            value = -self._minimax(board, self.max_depth - 1, float('-inf'), float('inf'), not board.turn)
            board.pop()
            
            print(f"Evaluando {move}: {value}")  # Debug
            
            if value > best_value:
                best_value = value
                best_move = move
        
        print(f"Nodos explorados: {self.nodes}")  # Debug
        return best_move, best_value
    
    def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        self.nodes += 1
        
        if depth == 0 or board.is_game_over():
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

# Función de prueba
def test_specific_position():
    board = chess.Board("rnbqkbnr/ppp1pNpp/8/3p1p2/8/8/PPPPPPPP/RNBQKB1R b KQ - 0 1")
    engine = MinimalEngine(depth=3)
    
    print("Posición inicial:")
    print(board)
    print("\nBuscando mejor movimiento...")
    
    move, value = engine.search(board)
    
    print(f"\nMejor movimiento encontrado: {move}")
    print(f"Valor: {value}")
    
    # Verificar si es una captura
    if move:
        captured_piece = board.piece_at(move.to_square)
        if captured_piece:
            print(f"¡Captura! Pieza capturada: {captured_piece.symbol()}")
    
    return board, engine

if __name__ == "__main__":
    test_specific_position()
