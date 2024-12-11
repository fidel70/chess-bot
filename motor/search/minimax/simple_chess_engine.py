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
        """Evaluación material corregida"""
        if board.is_checkmate():
            return -20000 if board.turn else 20000
            
        # Calculamos el score desde la perspectiva de las blancas
        score = 0
        for piece_type in chess.PIECE_TYPES:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.piece_values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.piece_values[piece_type]
        
        # Si juegan las negras, negamos el score
        return score if board.turn == chess.WHITE else -score
        
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
        self.debug_mode = True
        
    def _order_moves(self, board: chess.Board) -> List[chess.Move]:
        """Ordenamiento mejorado de movimientos para poda alfa-beta más eficiente"""
        moves = list(board.legal_moves)
        move_scores = []
        
        for move in moves:
            score = 0
            
            # 1. Capturas
            if board.is_capture(move):
                # Valorar MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                if victim and attacker:
                    score = 10 * victim.piece_type - attacker.piece_type
                    
            # 2. Jaque
            board.push(move)
            gives_check = board.is_check()
            board.pop()
            if gives_check:
                score += 8
                
            # 3. Promociones
            if move.promotion:
                score += 15
                
            move_scores.append((move, score))
            
        # Ordenar movimientos por puntuación
        return [move for move, _ in sorted(move_scores, key=lambda x: x[1], reverse=True)]
        
    def search(self, board: chess.Board) -> Tuple[Optional[chess.Move], float]:
        self.search_info = SearchInfo()
        start_time = time.time()
        
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Usar el nuevo ordenamiento de movimientos
        move_evaluations = []
        moves = self._order_moves(board)
        
        for move in moves:
            board.push(move)
            self.search_info.nodes_searched += 1
            value = -self._alpha_beta(board, self.max_depth - 1, -beta, -alpha, False)
            board.pop()
            
            move_evaluations.append((move, value))
            
            if value > best_value:
                best_value = value
                best_move = move
                alpha = value
        
        if self.debug_mode:
            print("\n=== Análisis de movimientos ===")
            print(f"Profundidad de búsqueda: {self.max_depth}")
            print("\nMejores movimientos encontrados:")
            print("-" * 40)
            print(f"{'Movimiento':<10} {'Evaluación':>10} {'Capturas':^10}")
            print("-" * 40)
            
            # Ordenar por evaluación
            move_evaluations.sort(key=lambda x: x[1], reverse=True)
            for move, eval in move_evaluations:
                move_san = board.san(move)
                is_capture = "Sí" if board.is_capture(move) else "No"
                print(f"{move_san:<10} {eval/100:>10.2f} {is_capture:^10}")
            
            print("\nEstadísticas de búsqueda:")
            print(f"Posiciones evaluadas: {self.search_info.positions_evaluated}")
            print(f"Nodos explorados: {self.search_info.nodes_searched}")
            print(f"Tiempo usado: {time.time() - start_time:.2f} segundos")
            print("=" * 40)
        
        return best_move, best_value
        
    def _alpha_beta(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        if depth == 0 or board.is_game_over():
            self.search_info.positions_evaluated += 1
            return self.evaluator.evaluate(board)
            
        moves = self._order_moves(board)  # Usar el nuevo ordenamiento también en la recursión
        
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