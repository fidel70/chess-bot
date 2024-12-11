import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import QSvgWidget
import chess
import pygame
pygame.mixer.init()

# Importar todas las clases necesarias del GUI original
from chess_gui_v_10 import (
    MainWindow as BaseWindow,
    ChessBoard as BaseBoard,
    ChessPiece,
    MoveList,
    EngineControls
)

# Importar el motor
from chess_bot.motor.search.minimax.simple_chess_engine import MinimaxEngine, MaterialEvaluator

class CapturedPiecesPanel(QLabel):
    """Panel simple para mostrar piezas capturadas como texto"""
    def __init__(self, color):
        super().__init__()
        self.color = color
        self.captured = []
        self.piece_symbols = {
            chess.PAWN: 'P',
            chess.KNIGHT: 'N',
            chess.BISHOP: 'B',
            chess.ROOK: 'R',
            chess.QUEEN: 'Q'
        }
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setStyleSheet("""
            QLabel {
                font-family: monospace;
                font-size: 12px;
                font-weight: bold;
                padding: 2px;
            }
        """)
        self.update_display()
        
    def add_piece(self, piece_type):
        self.captured.append(piece_type)
        self.update_display()
        
    def clear(self):
        self.captured.clear()
        self.update_display()
        
    def update_display(self):
        counts = {}
        for piece in self.captured:
            counts[piece] = counts.get(piece, 0) + 1
            
        text = []
        for piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]:
            if piece_type in counts:
                count = counts[piece_type]
                symbol = self.piece_symbols[piece_type]
                text.append(f"{symbol}×{count}" if count > 1 else symbol)
                
        self.setText(" ".join(text))

class ChessBoardWithCaptures(BaseBoard):
    """Tablero de ajedrez con paneles para piezas capturadas"""
    def __init__(self):
        super().__init__()
        self.white_captures = CapturedPiecesPanel(chess.WHITE)
        self.black_captures = CapturedPiecesPanel(chess.BLACK)
        self.add_capture_panels()
        
    def add_capture_panels(self):
        # Crear un nuevo layout principal
        new_layout = QVBoxLayout()
        new_layout.setSpacing(0)
        new_layout.setContentsMargins(0, 0, 0, 0)
        
        # Mover el contenido del tablero existente
        chess_widget = QWidget()
        chess_layout = QVBoxLayout(chess_widget)
        chess_layout.setSpacing(0)
        chess_layout.setContentsMargins(0, 0, 0, 0)
        
        # Mover todos los widgets del layout anterior al nuevo
        old_layout = self.layout()
        while old_layout.count():
            item = old_layout.takeAt(0)
            if item.widget():
                chess_layout.addWidget(item.widget())
        
        new_layout.addWidget(chess_widget)
        
        # Añadir los paneles de capturas
        captures_widget = QWidget()
        captures_layout = QVBoxLayout(captures_widget)
        captures_layout.setSpacing(0)
        captures_layout.setContentsMargins(5, 0, 5, 0)
        
        # Panel de capturas blancas
        white_row = QHBoxLayout()
        white_row.addWidget(QLabel("Blancas:"))
        white_row.addWidget(self.white_captures)
        white_row.addStretch()
        captures_layout.addLayout(white_row)
        
        # Panel de capturas negras
        black_row = QHBoxLayout()
        black_row.addWidget(QLabel("Negras:"))
        black_row.addWidget(self.black_captures)
        black_row.addStretch()
        captures_layout.addLayout(black_row)
        
        new_layout.addWidget(captures_widget)
        
        # Establecer el nuevo layout
        QWidget().setLayout(self.layout())
        self.setLayout(new_layout)
        
    def _complete_move(self, move, move_san):
        # Verificar si hay captura antes de hacer el movimiento
        if self.board.is_capture(move):
            captured_square = move.to_square
            captured_piece = self.board.piece_at(captured_square)
            if captured_piece:
                if captured_piece.color == chess.WHITE:
                    self.white_captures.add_piece(captured_piece.piece_type)
                else:
                    self.black_captures.add_piece(captured_piece.piece_type)
        
        # Ejecutar el movimiento original
        super()._complete_move(move, move_san)
        
    def set_position_from_fen(self, fen: str):
        super().set_position_from_fen(fen)
        self.white_captures.clear()
        self.black_captures.clear()

class EnhancedMainWindow(BaseWindow):
    """Ventana principal mejorada con soporte para piezas capturadas"""
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('Motor de Ajedrez - Con Piezas Capturadas')
        self.setMinimumSize(1000, 700)
        
        # Inicializar componentes
        self.material_evaluator = MaterialEvaluator()
        self.engine = MinimaxEngine(self.material_evaluator, depth=3)
        
        # Configurar sonido
        sound_path = os.path.join('gui', 'resources', 'sounds', 'move.mp3')
        self.move_sound = pygame.mixer.Sound(sound_path) if os.path.exists(sound_path) else None
        
        # Inicializar UI
        self.initUI()
        self.create_status_bar()
    
    def initUI(self):
        # Mantener el estilo original
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 10px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.createMenuBar()
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Panel izquierdo con el tablero mejorado
        left_panel = QVBoxLayout()
        self.board = ChessBoardWithCaptures()
        left_panel.addWidget(self.board)
        
        # Panel derecho (igual que el original)
        right_panel = QVBoxLayout()
        self.move_list = MoveList()
        self.engine_controls = EngineControls()
        
        right_panel.addWidget(self.move_list)
        right_panel.addWidget(self.engine_controls)
        
        # Conectar señales
        self.engine_controls.btn_set_position.clicked.connect(self.set_position)
        self.engine_controls.btn_analyze.clicked.connect(self.analyze_position)
        self.board.move_made.connect(self.move_list.add_move)
        self.move_list.move_selected.connect(self.board.goto_position)
        
        # Añadir paneles al layout principal
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = EnhancedMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()