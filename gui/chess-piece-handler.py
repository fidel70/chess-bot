from PyQt5.QtWidgets import QLabel
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QDrag, QPainter
import chess
import os

class ChessPiece(QSvgWidget):
    def __init__(self, piece, parent=None):
        super().__init__(parent)
        self.piece = piece
        self.load_svg()
        
    def load_svg(self):
        # Mapeo de piezas a archivos SVG
        piece_to_svg = {
            'P': 'wP.svg', 'N': 'wN.svg', 'B': 'wB.svg',
            'R': 'wR.svg', 'Q': 'wQ.svg', 'K': 'wK.svg',
            'p': 'bP.svg', 'n': 'bN.svg', 'b': 'bB.svg',
            'r': 'bR.svg', 'q': 'bQ.svg', 'k': 'bK.svg'
        }
        
        # Ruta al archivo SVG
        svg_path = os.path.join('gui', 'resources', 'pieces', piece_to_svg[self.piece])
        self.load(svg_path)
        
    def sizeHint(self):
        return QSize(45, 45)  # Tamaño estándar para piezas
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            # Aquí implementaremos el drag & drop más adelante
            drag.exec_()
            
class Square(QWidget):
    def __init__(self, is_white=True, piece=None, parent=None):
        super().__init__(parent)
        self.is_white = is_white
        self.piece = None
        self.initUI()
        if piece:
            self.set_piece(piece)
    
    def initUI(self):
        self.setMinimumSize(50, 50)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
    
    def set_piece(self, piece):
        if self.piece:
            self.layout.removeWidget(self.piece)
            self.piece.deleteLater()
        if piece:
            self.piece = ChessPiece(piece, self)
            self.layout.addWidget(self.piece)
        else:
            self.piece = None
    
    def paintEvent(self, event):
        painter = QPainter(self)
        color = QColor('#F0D9B5') if self.is_white else QColor('#B58863')
        painter.fillRect(event.rect(), color)

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
                square = Square(is_white=(row + col) % 2 == 0)
                self.squares[row][col] = square
                self.layout.addWidget(square, row, col)
        
        self.update_board()
    
    def update_board(self):
        """Actualiza la posición de todas las piezas según el estado del tablero"""
        for square in chess.SQUARES:
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            piece = self.board.piece_at(square)
            self.squares[row][col].set_piece(piece.symbol() if piece else None)
    
    def minimumSizeHint(self):
        return QSize(400, 400)
