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
        self.search_info = SearchInfo()
        start_time = time.time()
        
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        for current_depth in range(1, self.max_depth + 1):
            self.search_info.depth_reached = current_depth
            
            # Por esto:
            if current_depth >= 2:
                window_size = 30 + abs(best_value) * 0.1  # Ventana dinámica
                alpha = max(best_value - window_size, float('-inf'))
                beta = min(best_value + window_size, float('inf'))
            
            value = float('-inf')
            current_alpha = alpha
            
            hash_key = self.zobrist.compute_hash(board)
            tt_entry = self.tt.lookup(hash_key)
            tt_move = tt_entry[3] if tt_entry else None
            
            moves = self._order_moves(board, current_depth, tt_move)
            
            for move in moves:
                board.push(move)
                # Negamax: siempre buscamos el máximo del negativo
                value = -self._minimax(board, current_depth - 1, -beta, -current_alpha, not board.turn)
                board.pop()
                
                if value > current_alpha:
                    current_alpha = value
                    if value > best_value:
                        best_value = value
                        best_move = move
                        self.tt.store(hash_key, value, current_depth, TranspositionTable.EXACT, move)
                
                if current_alpha >= beta:
                    break
                
                if time_limit and (time.time() - start_time) > time_limit:
                    break
                    
            if time_limit and (time.time() - start_time) > time_limit:
                break
                    
        self.search_info.time_spent = time.time() - start_time
        return best_move, best_value if board.turn else -best_value

    def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        # Verificar finales
        if board.is_game_over():
            # Por esto:
            if board.is_checkmate():
                return -self.MATE_SCORE + depth  # Preferimos mates más cortos
            
        # Verificar tabla de transposición
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
            return self._quiescence_search(board, alpha, beta)

        tt_move = tt_entry[3] if tt_entry else None
        moves = self._order_moves(board, depth, tt_move)
        best_value = float('-inf') if maximizing else float('inf')
        best_move = None
        original_alpha = alpha
        
        # Poda null move (aplicar en ambos lados)
        if depth > 2 and not board.is_check():
            R = 3 if depth > 6 else 2
            board.push(chess.Move.null())
            null_value = -self._minimax(board, depth - R - 1, -beta, -beta + 1, not maximizing)
            board.pop()
            if maximizing and null_value >= beta:
                return beta
            elif not maximizing and null_value <= alpha:
                return alpha

        for i, move in enumerate(moves):
            # Late Move Reduction
            do_lmr = (i >= 4 and 
                     depth >= 3 and 
                     not board.is_capture(move) and 
                     not board.gives_check(move))
            reduction = 1 if do_lmr else 0
                
            board.push(move)
            self.search_info.nodes_searched += 1
            
            value = -self._minimax(
                board, 
                depth - 1 - reduction,
                -beta,
                -alpha,
                not maximizing
            )
            
            # Re-búsqueda si LMR falló alto
            if reduction and ((maximizing and value > alpha) or (not maximizing and value < beta)):
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
                if value < best_value:
                    best_value = value
                    best_move = move
                    if not board.is_capture(move) and depth < len(self.killer_moves):
                        self.killer_moves[depth][1] = self.killer_moves[depth][0]
                        self.killer_moves[depth][0] = move
                beta = min(beta, value)
                
            if beta <= alpha:
                if not board.is_capture(move):
                    move_key = (board.piece_at(move.from_square), move.to_square)
                    self.history_table[move_key] = self.history_table.get(move_key, 0) + depth * depth
                break

        # Almacenar en tabla de transposición
        if best_move:  # Solo almacenar si encontramos un mejor movimiento
            flag = (TranspositionTable.EXACT if alpha > original_alpha and beta > best_value
                  else TranspositionTable.BETA if beta <= best_value
                  else TranspositionTable.ALPHA)
            self.tt.store(hash_key, best_value, depth, flag, best_move)

        return best_value
        
    def _is_tactical_position(self, board: chess.Board) -> bool:
        return board.is_check() or any(board.is_capture(move) for move in board.legal_moves)
        
    def _quiescence_search(self, board: chess.Board, alpha: float, beta: float) -> float:
        self.search_info.positions_evaluated += 1
        
        # En negamax, no multiplicamos por turno
        # Por esto:
        stand_pat = self.evaluator.evaluate(board) * (1 if board.turn else -1)
        
        # El resto del código se mantiene igual
        
        if stand_pat >= beta:
            return beta
        
        alpha = max(alpha, stand_pat)
        
        # Ordenar capturas por MVV-LVA
        captures = []
        for move in board.legal_moves:
            if board.is_capture(move) or move.promotion == chess.QUEEN:
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                if victim and attacker:
                    score = victim.piece_type * 10 - attacker.piece_type
                    captures.append((move, score))
        
        # Ordenar capturas por score
        captures.sort(key=lambda x: x[1], reverse=True)
        
        for move, _ in captures:
            board.push(move)
            score = -self._quiescence_search(board, -beta, -alpha)
            board.pop()
            
            if score >= beta:
                return beta
            alpha = max(alpha, score)
                    
        return alpha
