import chess
from dataclasses import dataclass

class MaterialEvaluator:
    def __init__(self):
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
        }
    
    def evaluate(self, board: chess.Board) -> float:
        """Evaluación puramente material."""
        score = 0
        for piece_type in self.piece_values:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.piece_values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.piece_values[piece_type]
        return score

def test_position():
    # Crear el tablero con el FEN donde debería capturar
    board = chess.Board("rnbqkbnr/ppp1pNpp/8/3p1p2/8/8/PPPPPPPP/RNBQKB1R b KQ - 0 1")
    
    print(f"Posición inicial:")
    print(board)
    print(f"\nFEN: {board.fen()}")
    print(f"Turno: {'Negras' if board.turn == chess.BLACK else 'Blancas'}")
    
    # Crear evaluador y motor
    evaluator = MaterialEvaluator()
    engine = MinimaxEngine(evaluator, depth=3)
    
    # Evaluar cada movimiento legal y mostrar valores
    print("\nEvaluando movimientos legales:")
    for move in board.legal_moves:
        board.push(move)
        value = -engine._minimax(board, 2, float('-inf'), float('inf'))
        board.pop()
        print(f"Movimiento: {move.uci()} ({board.san(move)}), Valor: {value}")
    
    # Buscar el mejor movimiento
    best_move, best_value = engine.search(board)
    print(f"\nMejor movimiento encontrado: {board.san(best_move)}")
    print(f"Valor de la posición: {best_value}")
    print(f"Nodos explorados: {engine.search_info.nodes_searched}")
    print(f"Posiciones evaluadas: {engine.search_info.positions_evaluated}")
    print(f"Tiempo de búsqueda: {engine.search_info.time_spent:.2f} segundos")

if __name__ == "__main__":
    test_position()
