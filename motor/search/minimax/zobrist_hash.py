import numpy as np
import chess
from typing import Dict, Optional

class ZobristHash:
    def __init__(self, seed: Optional[int] = 42):
        # Inicializar generador de números aleatorios
        rng = np.random.RandomState(seed)
        
        # Crear tablas de hash para:
        # [pieza_tipo][color][casilla]
        self.piece_keys = np.zeros((7, 2, 64), dtype=np.uint64)
        for piece in range(7):  # 0 = vacío, 1-6 = piezas
            for color in range(2):
                for square in range(64):
                    self.piece_keys[piece, color, square] = rng.randint(0, np.iinfo(np.uint64).max, dtype=np.uint64)
        
        # Hash para el turno (blancas/negras)
        self.side_key = rng.randint(0, np.iinfo(np.uint64).max, dtype=np.uint64)
        
        # Hash para derechos de enroque
        self.castling_keys = np.zeros(16, dtype=np.uint64)
        for i in range(16):
            self.castling_keys[i] = rng.randint(0, np.iinfo(np.uint64).max, dtype=np.uint64)
            
        # Hash para casilla de en passant
        self.enpassant_keys = np.zeros(64, dtype=np.uint64)
        for square in range(64):
            self.enpassant_keys[square] = rng.randint(0, np.iinfo(np.uint64).max, dtype=np.uint64)

    def compute_hash(self, board: chess.Board) -> np.uint64:
        """Calcula el hash Zobrist para una posición dada."""
        hash_value = np.uint64(0)
        
        # Hash de las piezas
        for square in range(64):
            piece = board.piece_at(square)
            if piece is not None:
                piece_idx = piece.piece_type
                color_idx = int(piece.color)
                hash_value ^= self.piece_keys[piece_idx, color_idx, square]
        
        # Hash del turno
        if board.turn:
            hash_value ^= self.side_key
            
        # Hash de los derechos de enroque
        castling = 0
        if board.has_kingside_castling_rights(chess.WHITE):
            castling |= 1
        if board.has_queenside_castling_rights(chess.WHITE):
            castling |= 2
        if board.has_kingside_castling_rights(chess.BLACK):
            castling |= 4
        if board.has_queenside_castling_rights(chess.BLACK):
            castling |= 8
        hash_value ^= self.castling_keys[castling]
        
        # Hash de en passant
        if board.ep_square is not None:
            hash_value ^= self.enpassant_keys[board.ep_square]
            
        return hash_value

class TranspositionTable:
    EXACT = 0
    ALPHA = 1
    BETA = 2
    
    def __init__(self, size_mb: int = 32):
        # Calcular número de entradas basado en el tamaño en MB
        # Cada entrada: hash (8 bytes) + value (4 bytes) + flag (1 byte) + depth (1 byte) = 14 bytes
        self.size = (size_mb * 1024 * 1024) // 14
        self.table: Dict[np.uint64, tuple[float, int, int, Optional[chess.Move]]] = {}
        
    def store(self, hash_key: np.uint64, value: float, depth: int, 
             flag: int, best_move: Optional[chess.Move] = None):
        """Almacena una entrada en la tabla de transposición."""
        if len(self.table) >= self.size:
            # Si la tabla está llena, eliminar entrada aleatoria
            # En una implementación más sofisticada, usaríamos un esquema de reemplazo
            self.table.pop(next(iter(self.table)))
            
        self.table[hash_key] = (value, depth, flag, best_move)
        
    def lookup(self, hash_key: np.uint64) -> Optional[tuple[float, int, int, Optional[chess.Move]]]:
        """Busca una entrada en la tabla de transposición."""
        return self.table.get(hash_key)
