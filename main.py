from engine.evaluator.material import MaterialEvaluator
from engine.search.minimax import MinimaxEngine
import chess

def main():
    board = chess.Board()
    evaluator = MaterialEvaluator()
    engine = MinimaxEngine(evaluator, depth=3)
    
    # Implementar loop principal
    pass

if __name__ == "__main__":
    main()
