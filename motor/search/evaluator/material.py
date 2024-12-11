import chess
import numpy as np
from typing import Dict, Set, List, Tuple

class MaterialEvaluator:
    def __init__(self):
        # Valores base de piezas (en centipawns)
        self.mg_piece_values = np.array([100, 325, 335, 500, 975, 20000])
        self.eg_piece_values = np.array([145, 315, 325, 550, 1000, 20000])
        
        # Tablas de peones
        self.mg_pawn_table = np.array([
              0,   0,   0,   0,   0,   0,   0,   0,
            150, 150, 150, 150, 150, 150, 150, 150,
             60,  60,  70,  90,  90,  70,  60,  60,
             25,  25,  35,  45,  45,  35,  25,  25,
             15,  15,  20,  40,  40,  20,  15,  15,
             10,   5,   0,   0,   0,   0,   5,  10,
             10,  10,   0, -20, -20,   0,  10,  10,
              0,   0,   0,   0,   0,   0,   0,   0
        ])
        
        self.eg_pawn_table = np.array([
              0,   0,   0,   0,   0,   0,   0,   0,
            175, 175, 175, 175, 175, 175, 175, 175,
             85,  85,  90, 100, 100,  90,  85,  85,
             45,  45,  50,  60,  60,  50,  45,  45,
             30,  30,  35,  45,  45,  35,  30,  30,
             15,  15,  20,  20,  20,  20,  15,  15,
             10,  10,  10,   0,   0,  10,  10,  10,
              0,   0,   0,   0,   0,   0,   0,   0
        ])
        
        # Tablas de caballos
        self.mg_knight_table = np.array([
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20,   0,   5,   5,   0, -20, -40,
            -30,   5,  15,  20,  20,  15,   5, -30,
            -30,   0,  20,  25,  25,  20,   0, -30,
            -30,   5,  20,  25,  25,  20,   5, -30,
            -30,   0,  15,  20,  20,  15,   0, -30,
            -40, -20,   0,   0,   0,   0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50
        ])
        
        self.eg_knight_table = np.array([
            -40, -30, -20, -20, -20, -20, -30, -40,
            -30, -20,   0,   5,   5,   0, -20, -30,
            -20,   5,  15,  20,  20,  15,   5, -20,
            -20,   5,  20,  25,  25,  20,   5, -20,
            -20,   5,  20,  25,  25,  20,   5, -20,
            -20,   5,  15,  20,  20,  15,   5, -20,
            -30, -20,   0,   5,   5,   0, -20, -30,
            -40, -30, -20, -20, -20, -20, -30, -40
        ])
        
        # Tablas de alfiles
        self.mg_bishop_table = np.array([
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10,   5,   0,   0,   0,   0,   5, -10,
            -10,  10,  10,  10,  10,  10,  10, -10,
            -10,   0,  10,  15,  15,  10,   0, -10,
            -10,   5,   5,  15,  15,   5,   5, -10,
            -10,   0,   5,  10,  10,   5,   0, -10,
            -10,   0,   0,   0,   0,   0,   0, -10,
            -20, -10, -10, -10, -10, -10, -10, -20
        ])
        
        self.eg_bishop_table = np.array([
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10,   0,   0,   0,   0,   0,   0, -10,
            -10,   0,   5,   5,   5,   5,   0, -10,
            -10,   0,   5,  10,  10,   5,   0, -10,
            -10,   0,   5,  10,  10,   5,   0, -10,
            -10,   0,   5,   5,   5,   5,   0, -10,
            -10,   0,   0,   0,   0,   0,   0, -10,
            -20, -10, -10, -10, -10, -10, -10, -20
        ])
        
        # Tablas de torres
        self.mg_rook_table = np.array([
              0,   0,   0,   5,   5,   0,   0,   0,
             -5,   0,   0,   0,   0,   0,   0,  -5,
             -5,   0,   0,   0,   0,   0,   0,  -5,
             -5,   0,   0,   0,   0,   0,   0,  -5,
             -5,   0,   0,   0,   0,   0,   0,  -5,
             -5,   0,   0,   0,   0,   0,   0,  -5,
              5,  10,  10,  10,  10,  10,  10,   5,
              0,   0,   0,   0,   0,   0,   0,   0
        ])
        
        self.eg_rook_table = np.array([
              0,   0,   0,   0,   0,   0,   0,   0,
              5,  10,  10,  10,  10,  10,  10,   5,
             -5,   0,   0,   0,   0,   0,   0,  -5,
             -5,   0,   0,   0,   0,   0,   0,  -5,
             -5,   0,   0,   0,   0,   0,   0,  -5,
             -5,   0,   0,   0,   0,   0,   0,  -5,
             -5,   0,   0,   0,   0,   0,   0,  -5,
              0,   0,   0,   5,   5,   0,   0,   0
        ])
        
        # Tablas de dama
        self.mg_queen_table = np.array([
            -20, -10, -10,  -5,  -5, -10, -10, -20,
            -10,   0,   0,   0,   0,   0,   0, -10,
            -10,   0,   5,   5,   5,   5,   0, -10,
             -5,   0,   5,   5,   5,   5,   0,  -5,
              0,   0,   5,   5,   5,   5,   0,  -5,
            -10,   5,   5,   5,   5,   5,   0, -10,
            -10,   0,   5,   0,   0,   0,   0, -10,
            -20, -10, -10,  -5,  -5, -10, -10, -20
        ])
        
        self.eg_queen_table = np.array([
            -20, -10, -10,  -5,  -5, -10, -10, -20,
            -10,   0,   0,   0,   0,   0,   0, -10,
            -10,   0,   5,   5,   5,   5,   0, -10,
             -5,   0,   5,   5,   5,   5,   0,  -5,
              0,   0,   5,   5,   5,   5,   0,  -5,
            -10,   5,   5,   5,   5,   5,   0, -10,
            -10,   0,   5,   0,   0,   0,   0, -10,
            -20, -10, -10,  -5,  -5, -10, -10, -20
        ])

        # Tabla del rey para mediojuego (prioriza seguridad)
        self.mg_king_table = np.array([
             20,  30,  10,   0,   0,  10,  30,  20,
             20,  20,   0,   0,   0,   0,  20,  20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30
        ])

        # Tabla del rey para finales (prioriza actividad)
        self.eg_king_table = np.array([
            -50, -40, -30, -20, -20, -30, -40, -50,
            -30, -20, -10,   0,   0, -10, -20, -30,
            -30, -10,  20,  30,  30,  20, -10, -30,
            -30, -10,  30,  40,  40,  30, -10, -30,
            -30, -10,  30,  40,  40,  30, -10, -30,
            -30, -10,  20,  30,  30,  20, -10, -30,
            -30, -30,   0,   0,   0,   0, -30, -30,
            -50, -30, -30, -30, -30, -30, -30, -50
        ])
        
        # Bonus y penalizaciones ajustados
        self.bishop_pair_bonus = 50
        self.doubled_pawn_penalty = -30
        self.isolated_pawn_penalty = -40
        self.backward_pawn_penalty = -20
        self.passed_pawn_bonus = [0, 20, 40, 60, 100, 150, 200, 0]
        self.rook_open_file_bonus = 50
        self.rook_semi_open_bonus = 25
        self.mobility_bonus = {
            chess.KNIGHT: (4, 5),    # (mediojuego, final)
            chess.BISHOP: (5, 5),
            chess.ROOK: (3, 6),
            chess.QUEEN: (2, 4)
        }
        
        # Control del centro
        self.central_squares = {chess.E4, chess.D4, chess.E5, chess.D5}
        self.extended_center = {
            chess.C3, chess.D3, chess.E3, chess.F3,
            chess.C4, chess.D4, chess.E4, chess.F4,
            chess.C5, chess.D5, chess.E5, chess.F5,
            chess.C6, chess.D6, chess.E6, chess.F6
        }
        
    def evaluate(self, board: chess.Board) -> float:
        """Evaluación principal de la posición."""
        if board.is_checkmate():
            return -20000 if board.turn else 20000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
            
        # Determinar fase del juego
        game_phase = self._get_game_phase(board)
        
        # Evaluación desde perspectiva de las blancas
        score = (
            self._evaluate_material_and_position(board, game_phase) +
            self._evaluate_pawn_structure(board) +
            self._evaluate_mobility(board, game_phase) +
            self._evaluate_center_control(board) +
            self._evaluate_king_safety(board, game_phase)
        )
        
        # IMPORTANTE: Ya no invertimos el score basado en el turno
        return score if board.turn == chess.WHITE else -score
        
        
    def _get_game_phase(self, board: chess.Board) -> float:
        """Calcula la fase del juego."""
        npm = 0  # Non-pawn material
        for piece_type in range(2, 6):
            npm += len(board.pieces(piece_type, chess.WHITE)) * self.mg_piece_values[piece_type-1]
            npm += len(board.pieces(piece_type, chess.BLACK)) * self.mg_piece_values[piece_type-1]
        
        max_npm = 4 * self.mg_piece_values[1] + 4 * self.mg_piece_values[2] + \
                 4 * self.mg_piece_values[3] + 2 * self.mg_piece_values[4]
                 
        return 1.0 - min(1.0, npm / max_npm)
        
    def _evaluate_material_and_position(self, board: chess.Board, game_phase: float) -> float:
        """Evalúa material y valor posicional."""
        score = 0
        piece_tables = {
            chess.PAWN: (self.mg_pawn_table, self.eg_pawn_table),
            chess.KNIGHT: (self.mg_knight_table, self.eg_knight_table),
            chess.BISHOP: (self.mg_bishop_table, self.eg_bishop_table),
            chess.ROOK: (self.mg_rook_table, self.eg_rook_table),
            chess.QUEEN: (self.mg_queen_table, self.eg_queen_table),
            chess.KING: (self.mg_king_table, self.eg_king_table)
        }
        
        for piece_type in chess.PIECE_TYPES:
            mg_table, eg_table = piece_tables[piece_type]
            piece_value = (1 - game_phase) * self.mg_piece_values[piece_type-1] + \
                 game_phase * self.eg_piece_values[piece_type-1]
            
            # Piezas blancas
            for square in board.pieces(piece_type, chess.WHITE):
                score += piece_value
                mg_pos_score = mg_table[square]
                eg_pos_score = eg_table[square]
                score += (1 - game_phase) * mg_pos_score + game_phase * eg_pos_score
                
            # Piezas negras
            for square in board.pieces(piece_type, chess.BLACK):
                score -= piece_value
                mg_pos_score = mg_table[chess.square_mirror(square)]
                eg_pos_score = eg_table[chess.square_mirror(square)]
                score -= (1 - game_phase) * mg_pos_score + game_phase * eg_pos_score
        
        # Bonus por par de alfiles (ajustado según la fase)
        if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
            score += self.bishop_pair_bonus * (1 + game_phase)
        if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
            score -= self.bishop_pair_bonus * (1 + game_phase)
            
        return score
        
    def _evaluate_pawn_structure(self, board: chess.Board) -> float:
        """Evaluación mejorada de la estructura de peones."""
        score = 0
        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)
        
        # Evaluar peones blancos
        white_pawn_files = [chess.square_file(s) for s in white_pawns]
        for square in white_pawns:
            file_idx = chess.square_file(square)
            rank_idx = chess.square_rank(square)
            
            # Peones doblados (penalización mayor en columnas centrales)
            if white_pawn_files.count(file_idx) > 1:
                central_file_penalty = 1.5 if 2 <= file_idx <= 5 else 1.0
                score += self.doubled_pawn_penalty * central_file_penalty
                
            # Peones aislados (penalización mayor en columnas centrales)
            if file_idx > 0 and file_idx < 7:
                if file_idx-1 not in white_pawn_files and file_idx+1 not in white_pawn_files:
                    central_file_penalty = 1.5 if 2 <= file_idx <= 5 else 1.0
                    score += self.isolated_pawn_penalty * central_file_penalty
                    
            # Peones pasados (bonus mayor en columnas centrales y avanzados)
            if self._is_passed_pawn(board, square, chess.WHITE):
                central_file_bonus = 1.3 if 2 <= file_idx <= 5 else 1.0
                score += self.passed_pawn_bonus[rank_idx] * central_file_bonus
                
            # Peones retrasados
            if self._is_backward_pawn(board, square, chess.WHITE):
                score += self.backward_pawn_penalty
                
        # Evaluar peones negros (similar pero con signo opuesto)
        black_pawn_files = [chess.square_file(s) for s in black_pawns]
        for square in black_pawns:
            file_idx = chess.square_file(square)
            rank_idx = 7 - chess.square_rank(square)
            
            if black_pawn_files.count(file_idx) > 1:
                central_file_penalty = 1.5 if 2 <= file_idx <= 5 else 1.0
                score -= self.doubled_pawn_penalty * central_file_penalty
                
            if file_idx > 0 and file_idx < 7:
                if file_idx-1 not in black_pawn_files and file_idx+1 not in black_pawn_files:
                    central_file_penalty = 1.5 if 2 <= file_idx <= 5 else 1.0
                    score -= self.isolated_pawn_penalty * central_file_penalty
                    
            if self._is_passed_pawn(board, square, chess.BLACK):
                central_file_bonus = 1.3 if 2 <= file_idx <= 5 else 1.0
                score -= self.passed_pawn_bonus[rank_idx] * central_file_bonus
                
            if self._is_backward_pawn(board, square, chess.BLACK):
                score -= self.backward_pawn_penalty
                
        return score
        
    def _evaluate_mobility(self, board: chess.Board, game_phase: float) -> float:
        """Evaluación mejorada de movilidad."""
        score = 0
        
        for color in [chess.WHITE, chess.BLACK]:
            multiplier = 1 if color == chess.WHITE else -1
            
            for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
                mg_bonus, eg_bonus = self.mobility_bonus[piece_type]
                for square in board.pieces(piece_type, color):
                    # Calcular movimientos legales reales
                    moves = 0
                    for move in board.legal_moves:
                        if move.from_square == square:
                            moves += 1
                    
                    # Bonus de movilidad ajustado por fase
                    mobility_bonus = (1 - game_phase) * mg_bonus + game_phase * eg_bonus
                    score += multiplier * moves * mobility_bonus
                    
                    # Bonus especial para torres en columnas abiertas o semi-abiertas
                    if piece_type == chess.ROOK:
                        file_idx = chess.square_file(square)
                        if not any(chess.square_file(s) == file_idx for s in board.pieces(chess.PAWN, color)):
                            if not any(chess.square_file(s) == file_idx for s in board.pieces(chess.PAWN, not color)):
                                score += multiplier * self.rook_open_file_bonus
                            else:
                                score += multiplier * self.rook_semi_open_bonus
                    
        return score
        
    def _evaluate_center_control(self, board: chess.Board) -> float:
        """Evaluación mejorada del control del centro."""
        score = 0
        
        # Control de casillas centrales
        central_control = {sq: 0 for sq in self.central_squares}
        extended_control = {sq: 0 for sq in self.extended_center}
        
        # Evaluar control por ataques y ocupación
        for square in self.central_squares:
            # Ocupación directa vale más que ataque
            piece = board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE:
                    score += 15
                else:
                    score -= 15
            
            # Ataques
            if board.is_attacked_by(chess.WHITE, square):
                score += 8
            if board.is_attacked_by(chess.BLACK, square):
                score -= 8
                
        # Control del centro extendido
        for square in self.extended_center:
            piece = board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE:
                    score += 7
                else:
                    score -= 7
                    
            if board.is_attacked_by(chess.WHITE, square):
                score += 3
            if board.is_attacked_by(chess.BLACK, square):
                score -= 3
                
        return score
        
    def _evaluate_king_safety(self, board: chess.Board, game_phase: float) -> float:
        """Evaluación mejorada de seguridad del rey."""
        score = 0
        
        # La seguridad del rey es más importante en mediojuego
        if game_phase < 0.8:
            for color in [chess.WHITE, chess.BLACK]:
                king_square = board.king(color)
                if not king_square:
                    continue
                    
                multiplier = 1 if color == chess.WHITE else -1
                file_idx = chess.square_file(king_square)
                rank_idx = chess.square_rank(king_square)
                
                # Evaluar protección de peones
                pawn_shield_score = self._evaluate_pawn_shield(board, king_square, color)
                score += multiplier * pawn_shield_score * (1 - game_phase)
                
                # Evaluar ataques al rey
                attacks = len([sq for sq in board.attacks(king_square)
                             if board.piece_at(sq) and board.piece_at(sq).color != color])
                attack_penalty = -20 * attacks * (1 - game_phase)
                score += multiplier * attack_penalty
                
                # Penalizar rey expuesto en mediojuego
                if game_phase < 0.5:
                    exposed_penalty = 0
                    if 2 <= file_idx <= 5 and rank_idx <= 2:
                        exposed_penalty = -30
                    score += multiplier * exposed_penalty
                
        return score
        
    def _evaluate_pawn_shield(self, board: chess.Board, king_square: int, color: chess.Color) -> float:
        """Evalúa la protección de peones alrededor del rey."""
        score = 0
        file_idx = chess.square_file(king_square)
        rank_idx = chess.square_rank(king_square)
        
        # Definir casillas a revisar para el escudo de peones
        shield_squares = []
        base_rank = 0 if color == chess.WHITE else 7
        pawn_direction = 1 if color == chess.WHITE else -1
        
        if abs(rank_idx - base_rank) <= 2:
            for f in range(max(0, file_idx - 1), min(8, file_idx + 2)):
                for r in range(rank_idx, rank_idx + 2 * pawn_direction, pawn_direction):
                    if 0 <= r < 8:
                        shield_squares.append(chess.square(f, r))
        
        # Evaluar cada casilla del escudo
        for square in shield_squares:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                score += 10
                
        return score
        
    def _is_backward_pawn(self, board: chess.Board, square: int, color: chess.Color) -> bool:
        """Determina si un peón está retrasado."""
        file_idx = chess.square_file(square)
        rank_idx = chess.square_rank(square)
        
        # No puede ser retrasado si tiene peones amigos en columnas adyacentes detrás
        forward_range = range(rank_idx + 1, 8) if color else range(rank_idx - 1, -1, -1)
        
        # Verificar si puede ser defendido por peones adyacentes
        can_be_defended = False
        for adj_file in [file_idx - 1, file_idx + 1]:
            if 0 <= adj_file < 8:
                adj_rank = rank_idx + (1 if color else -1)
                if 0 <= adj_rank < 8:
                    adj_square = chess.square(adj_file, adj_rank)
                    if board.piece_at(adj_square) and \
                       board.piece_at(adj_square).piece_type == chess.PAWN and \
                       board.piece_at(adj_square).color == color:
                        can_be_defended = True
                        break
        
        return not can_be_defended
        
    def _is_passed_pawn(self, board: chess.Board, square: int, color: chess.Color) -> bool:
        """Determina si un peón es pasado."""
        file_idx = chess.square_file(square)
        rank_idx = chess.square_rank(square)
        
        forward_range = range(rank_idx + 1, 8) if color else range(rank_idx - 1, -1, -1)
        
        for rank in forward_range:
            for file in [file_idx - 1, file_idx, file_idx + 1]:
                if 0 <= file < 8:
                    check_square = chess.square(file, rank)
                    piece = board.piece_at(check_square)
                    if piece and piece.piece_type == chess.PAWN and piece.color != color:
                        return False
        return True