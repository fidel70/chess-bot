import chess
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from motor.search.evaluator.material import MaterialEvaluator
from minimaxengine import MinimaxEngine

def test_position():
    # Crear el tablero con el FEN donde debería capturar
    board = chess.Board("rnbqkbnr/pppp1ppp/8/4p3/3N4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1")
    
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
        # Usar el minimax como está definido en tu versión original
        value = engine._minimax(board, 2, float('-inf'), float('inf'),True)
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