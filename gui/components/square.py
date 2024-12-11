# gui/components/square.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QColor, QDrag

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
        svg_path = f"gui/resources/pieces/{piece_to_svg[self.piece]}"
        self.load(svg_path)
        
    def sizeHint(self):
        return QSize(45, 45)

class Square(QWidget):
    def __init__(self, position, is_white=True, piece=None, parent=None):
        super().__init__(parent)
        self.position = position  # Tupla (fila, columna)
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
            self.layout.addWidget(self.piece, alignment=Qt.AlignCenter)
        else:
            self.piece = None
    
    def paintEvent(self, event):
        painter = QPainter(self)
        color = QColor('#F0D9B5') if self.is_white else QColor('#B58863')
        painter.fillRect(event.rect(), color)
