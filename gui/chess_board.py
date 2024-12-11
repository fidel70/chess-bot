# gui/chess_board.py
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtCore import Qt, QSize
from .components.square import Square
import chess

class ChessBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        self.board = chess.Board()
        self.initUI()
    
    def initUI(self):
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # Crear el tablero 8x8 con piezas
        for row in range(8):
            for col in range(8):
                square = Square(
                    position=(row, col),
                    is_white=(row + col) % 2 == 0
                )
                self.squares[row][col] = square
                # Nota: Invertimos las filas para que las blancas estén abajo
                self.layout.addWidget(square, 7-row, col)
        
        self.update_board()
    
    def update_board(self):
        """Actualiza la posición de todas las piezas según el estado del tablero"""
        for square in chess.SQUARES:
            row = chess.square_rank(square)  # 0-7 (1-8 rank)
            col = chess.square_file(square)  # 0-7 (a-h file)
            piece = self.board.piece_at(square)
            self.squares[row][col].set_piece(piece.symbol() if piece else None)
    
    def minimumSizeHint(self):
        return QSize(400, 400)
