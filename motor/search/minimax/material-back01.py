import chess
import numpy as np
from typing import Dict, Set, List, Tuple

class MaterialEvaluator:
    def __init__(self):
        # Valores base de piezas en centipawns
        self.mg_piece_values = np.array([100, 320, 330, 500, 900, 0])  # Rey sin valor material
        self.eg_piece_values = np.array([120, 310, 330, 510, 880, 0])  # Peones más valiosos en finales
        
        # Tablas de posición para mediojuego
        self.mg_pawn_table = np.array([
             0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
             5,  5, 10, 25, 25, 10,  5,  5,
             0,  0,  0, 20, 20,  0,  0,  0,
             5, -5,-10,  0,  0,-10, -5,  5,
             5, 10, 10,-20,-20, 10, 10,  5,
             0,  0,  0,  0,  0,  0,  0,  0
        ])
        
        self.mg_knight_table = np.array([
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50
        ])
        
        self.mg_bishop_table = np.array([
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20
        ])
        
        # Bonus y penalizaciones
        self.bishop_pair_bonus = 30
        self.doubled_pawn_penalty = -10
        self.isolated_pawn_penalty = -20
        self.backward_pawn_penalty = -8
        self.passed_pawn_bonus = [0, 10, 20, 40, 60, 100, 150, 0]
        self.rook_open_file_bonus = 25
        self.rook_semi_open_bonus = 10
        self.undeveloped_piece_penalty = -15
        
        # Bonus de movilidad por pieza y fase
        self.mobility_bonus = {
            chess.KNIGHT: (3, 4),  # (mediojuego, final)
            chess.BISHOP: (3, 3),
            chess.ROOK: (2, 4),
            chess.QUEEN: (1, 2)
        }
        
        # Casillas centrales y centro extendido
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
        
        score = 0
        
        # Material base y posicional
        score += self._evaluate_material_and_position(board, game_phase)
        
        # Estructura de peones
        score += self._evaluate_pawn_structure(board)
        
        # Movilidad y desarrollo
        score += self._evaluate_mobility_and_development(board, game_phase)
        
        # Control del centro
        score += self._evaluate_center_control(board)
        
        # Seguridad del rey
        score += self._evaluate_king_safety(board, game_phase)
        
        return score if board.turn == chess.WHITE else -score
        
    def _get_game_phase(self, board: chess.Board) -> float:
        """Calcula la fase del juego (0 = mediojuego, 1 = final)."""
        npm = 0  # Non-pawn material
        for piece_type in range(2, 6):  # Caballos hasta dama
            npm += len(board.pieces(piece_type, chess.WHITE)) * self.mg_piece_values[piece_type-1]
            npm += len(board.pieces(piece_type, chess.BLACK)) * self.mg_piece_values[piece_type-1]
        
        # Valor máximo de material sin peones
        max_npm = 4 * self.mg_piece_values[1] + 4 * self.mg_piece_values[2] + \
                 4 * self.mg_piece_values[3] + 2 * self.mg_piece_values[4]
                 
        return 1.0 - min(1.0, npm / max_npm)
        
    def _evaluate_material_and_position(self, board: chess.Board, game_phase: float) -> float:
        """Evalúa material y valor posicional de las piezas."""
        score = 0
        
        for piece_type in chess.PIECE_TYPES:
            piece_value = (1 - game_phase) * self.mg_piece_values[piece_type-1] + \
                         game_phase * self.eg_piece_values[piece_type-1]
                         
            # Piezas blancas
            for square in board.pieces(piece_type, chess.WHITE):
                score += piece_value
                if piece_type == chess.PAWN:
                    score += self.mg_pawn_table[square]
                elif piece_type == chess.KNIGHT:
                    score += self.mg_knight_table[square]
                elif piece_type == chess.BISHOP:
                    score += self.mg_bishop_table[square]
                    
            # Piezas negras
            for square in board.pieces(piece_type, chess.BLACK):
                score -= piece_value
                if piece_type == chess.PAWN:
                    score -= self.mg_pawn_table[chess.square_mirror(square)]
                elif piece_type == chess.KNIGHT:
                    score -= self.mg_knight_table[chess.square_mirror(square)]
                elif piece_type == chess.BISHOP:
                    score -= self.mg_bishop_table[chess.square_mirror(square)]
        
        # Bonus por par de alfiles
        if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
            score += self.bishop_pair_bonus
        if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
            score -= self.bishop_pair_bonus
            
        return score
        
    def _evaluate_pawn_structure(self, board: chess.Board) -> float:
        """Evaluación detallada de la estructura de peones."""
        score = 0
        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)
        
        # Evaluar peones blancos
        white_pawn_files = [chess.square_file(s) for s in white_pawns]
        for square in white_pawns:
            file_idx = chess.square_file(square)
            rank_idx = chess.square_rank(square)
            
            # Peones doblados
            if white_pawn_files.count(file_idx) > 1:
                score += self.doubled_pawn_penalty
                
            # Peones aislados
            if file_idx > 0 and file_idx < 7:
                if file_idx-1 not in white_pawn_files and file_idx+1 not in white_pawn_files:
                    score += self.isolated_pawn_penalty
                    
            # Peones pasados
            if self._is_passed_pawn(board, square, chess.WHITE):
                score += self.passed_pawn_bonus[rank_idx]
                
        # Evaluar peones negros (similar pero con signo opuesto)
        black_pawn_files = [chess.square_file(s) for s in black_pawns]
        for square in black_pawns:
            file_idx = chess.square_file(square)
            rank_idx = 7 - chess.square_rank(square)
            
            if black_pawn_files.count(file_idx) > 1:
                score -= self.doubled_pawn_penalty
                
            if file_idx > 0 and file_idx < 7:
                if file_idx-1 not in black_pawn_files and file_idx+1 not in black_pawn_files:
                    score -= self.isolated_pawn_penalty
                    
            if self._is_passed_pawn(board, square, chess.BLACK):
                score -= self.passed_pawn_bonus[rank_idx]
                
        return score
        
    def _evaluate_mobility_and_development(self, board: chess.Board, game_phase: float) -> float:
        """Evalúa movilidad de piezas y desarrollo."""
        score = 0
        
        for color in [chess.WHITE, chess.BLACK]:
            multiplier = 1 if color == chess.WHITE else -1
            
            for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
                for square in board.pieces(piece_type, color):
                    # Movilidad
                    mobility = len(board.attacks(square))
                    mg_bonus, eg_bonus = self.mobility_bonus[piece_type]
                    bonus = (1 - game_phase) * mg_bonus + game_phase * eg_bonus
                    score += multiplier * mobility * bonus
                    
                    # Desarrollo (solo en mediojuego)
                    if game_phase < 0.5:
                        if piece_type in [chess.KNIGHT, chess.BISHOP]:
                            initial_rank = 0 if color == chess.WHITE else 7
                            if chess.square_rank(square) == initial_rank:
                                score += multiplier * self.undeveloped_piece_penalty
                                
        return score
        
    def _evaluate_center_control(self, board: chess.Board) -> float:
        """Evalúa el control del centro."""
        score = 0
        
        for square in self.central_squares:
            if board.is_attacked_by(chess.WHITE, square):
                score += 5
            if board.is_attacked_by(chess.BLACK, square):
                score -= 5
                
        for square in self.extended_center:
            if board.is_attacked_by(chess.WHITE, square):
                score += 2
            if board.is_attacked_by(chess.BLACK, square):
                score -= 2
                
        return score
        
    def _evaluate_king_safety(self, board: chess.Board, game_phase: float) -> float:
        """Evalúa la seguridad del rey."""
        score = 0
        
        # Solo considerar seguridad del rey en mediojuego
        if game_phase < 0.8:
            for color in [chess.WHITE, chess.BLACK]:
                multiplier = 1 if color == chess.WHITE else -1
                king_square = board.king(color)
                
                # Penalizar rey expuesto
                attacks = len([sq for sq in board.attacks(king_square)
                             if board.piece_at(sq) and board.piece_at(sq).color != color])
                score += multiplier * (-10 * attacks)
                
                # Bonus por enroque
                if not board.has_castling_rights(color):
                    score += multiplier * -30
                    
        return score
        
    def _is_passed_pawn(self, board: chess.Board, square: int, color: chess.Color) -> bool:
        """Determina si un peón es pasado."""
        file_idx = chess.square_file(square)
        rank_idx = chess.square_rank(square)
        
        forward_range = range(rank_idx + 1, 8) if color else range(rank_idx - 1, -1, -1)
        
        for rank in forward_range:
            for file in [file_idx - 1, file_idx, file_idx + 1]:
                if 0 <= file <= 7:
                    check_square = chess.square(file, rank)
                    piece = board.piece_at(check_square)
                    if piece and piece.piece_type == chess.PAWN and piece.color != color:
                        return False
        return True