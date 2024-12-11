from typing import Optional, Tuple, List
import os
import chess
import time
from dataclasses import dataclass
import numpy as np
import sys
# Obtener la ruta absoluta del directorio raíz del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(project_root)
sys.path.append(project_root)

from evaluator.material import MaterialEvaluator
from minimax.zobrist_hash import ZobristHash, TranspositionTable   

@dataclass
class SearchInfo:
    nodes_searched: int = 0
    positions_evaluated: int = 0
    time_spent: float = 0.0
    depth_reached: int = 0
    pv_line: List[chess.Move] = None

class MinimaxEngine:
    def __init__(self, evaluator, depth=3, tt_size_mb=32):
        self.evaluator = evaluator
        self.max_depth = depth
        self.search_info = SearchInfo()
        self.MATE_SCORE = 20000
        self.DRAW_SCORE = 0
        
        # Inicializar Zobrist Hashing y Tabla de Transposición
        self.zobrist = ZobristHash()
        self.tt = TranspositionTable(tt_size_mb)
        
        # Movimientos asesinos (killer moves)
        self.killer_moves = [[None] * 2 for _ in range(32)]
        
        # Historia heurística
        self.history_table = {}
    
    def _order_moves(self, board: chess.Board, depth: int, tt_move: Optional[chess.Move] = None) -> List[chess.Move]:
        moves = list(board.legal_moves)
        move_scores = []
        
        for move in moves:
            score = 0
            
            # Prioridad al movimiento de la TT
            if tt_move and move == tt_move:
                score += 10000
                
            # MVV-LVA para capturas
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                if victim and attacker:
                    score += (victim.piece_type * 10 - attacker.piece_type)
            
            # Killer moves
            if depth < len(self.killer_moves) and (
                self.killer_moves[depth][0] == move or 
                self.killer_moves[depth][1] == move):
                score += 90
            
            # Historia heurística
            move_key = (board.piece_at(move.from_square), move.to_square)
            if move_key in self.history_table:
                score += min(self.history_table[move_key], 50)
            
            # Promociones
            if move.promotion:
                score += 800 if move.promotion == chess.QUEEN else 300
                
            # Jaque
            if board.gives_check(move):
                score += 50
                
            move_scores.append((move, score))
        
        return [move for move, _ in sorted(move_scores, key=lambda x: x[1], reverse=True)]

    def search(self, board: chess.Board, time_limit: Optional[float] = None) -> Tuple[chess.Move, float]:
        """
        Método principal de búsqueda que devuelve el mejor movimiento y su evaluación
        """
        self.search_info = SearchInfo()
        start_time = time.time()
        
        best_move = None
        best_value = float('-inf')
        
        # Iterative deepening
        for current_depth in range(1, self.max_depth + 1):
            self.search_info.depth_reached = current_depth
            value = float('-inf')
            alpha = float('-inf')
            beta = float('inf')
            
            hash_key = self.zobrist.compute_hash(board)
            tt_entry = self.tt.lookup(hash_key)
            tt_move = tt_entry[3] if tt_entry else None
            
            moves = self._order_moves(board, current_depth, tt_move)
            
            for move in moves:
                board.push(move)
                # CAMBIO CLAVE: Negamos el valor y pasamos !maximizing
                value = -self._minimax(
                    board,
                    current_depth - 1,
                    -beta,
                    -alpha,
                    False  # Siempre empezamos con maximizing=False porque ya negamos el valor
                )
                board.pop()
                
                if value > best_value:
                    best_value = value
                    best_move = move
                    alpha = value
                    # Guardamos en la tabla de transposición
                    self.tt.store(hash_key, value, current_depth, TranspositionTable.EXACT, move)
                
                if time_limit and (time.time() - start_time) > time_limit:
                    break
            
            if time_limit and (time.time() - start_time) > time_limit:
                break
        
        self.search_info.time_spent = time.time() - start_time
        return best_move, best_value

    def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """
        Implementación corregida del algoritmo minimax
        """
        # Verificar finales de juego
        if board.is_game_over():
            if board.is_checkmate():
                return -self.MATE_SCORE + (self.max_depth - depth)  # Preferimos mates más cortos
            return self.DRAW_SCORE
            
        # Verificar la tabla de transposición
        hash_key = self.zobrist.compute_hash(board)
        tt_entry = self.tt.lookup(hash_key)
        
        if tt_entry and tt_entry[1] >= depth:
            value, stored_depth, flag, _ = tt_entry
            if flag == TranspositionTable.EXACT:
                return value
            elif flag == TranspositionTable.ALPHA and value <= alpha:
                return alpha
            elif flag == TranspositionTable.BETA and value >= beta:
                return beta
            
        if depth == 0:
            # CAMBIO CLAVE: El valor de quiescence ahora tiene en cuenta maximizing
            return self._quiescence_search(board, alpha, beta, maximizing)
        
        tt_move = tt_entry[3] if tt_entry else None
        moves = self._order_moves(board, depth, tt_move)
        best_value = float('-inf') if maximizing else float('inf')
        best_move = None
        original_alpha = alpha
        
        # Poda null move
        if depth > 2 and not board.is_check():
            R = 3 if depth > 6 else 2
            board.push(chess.Move.null())
            null_value = -self._minimax(board, depth - R - 1, -beta, -beta + 1, not maximizing)
            board.pop()
            if null_value >= beta:
                return beta
        
        for move in moves:
            board.push(move)
            self.search_info.nodes_searched += 1
            
            # CAMBIO CLAVE: Siempre negamos el valor y alternamos maximizing
            value = -self._minimax(board, depth - 1, -beta, -alpha, not maximizing)
            
            board.pop()
            
            if maximizing:
                if value > best_value:
                    best_value = value
                    best_move = move
                    if not board.is_capture(move) and depth < len(self.killer_moves):
                        self.killer_moves[depth][1] = self.killer_moves[depth][0]
                        self.killer_moves[depth][0] = move
                alpha = max(alpha, value)
            else:
                best_value = min(best_value, value)
                beta = min(beta, value)
            
            if beta <= alpha:
                if not board.is_capture(move):
                    move_key = (board.piece_at(move.from_square), move.to_square)
                    self.history_table[move_key] = self.history_table.get(move_key, 0) + depth * depth
                break
        
        # Almacenar en tabla de transposición
        flag = (TranspositionTable.EXACT if alpha < best_value <= beta
               else TranspositionTable.BETA if best_value >= beta
               else TranspositionTable.ALPHA)
        self.tt.store(hash_key, best_value, depth, flag, best_move)
        
        return best_value

    def _quiescence_search(self, board: chess.Board, alpha: float, beta: float, maximizing: bool) -> float:
        """
        Búsqueda de quietud corregida que tiene en cuenta maximizing
        """
        self.search_info.positions_evaluated += 1
        
        # CAMBIO CLAVE: Evaluación según maximizing
        stand_pat = self.evaluator.evaluate(board)
        
        if maximizing:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)
        
        for move in board.legal_moves:
            if not board.is_capture(move) and not (move.promotion == chess.QUEEN):
                continue
                
            board.push(move)
            value = -self._quiescence_search(board, -beta, -alpha, not maximizing)
            board.pop()
            
            if maximizing:
                if value >= beta:
                    return beta
                alpha = max(alpha, value)
            else:
                if value <= alpha:
                    return alpha
                beta = min(beta, value)
                    
        return stand_pat