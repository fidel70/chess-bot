import sys
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QApplication
from chess_gui_v_10 import MainWindow as BaseWindow, ChessBoard as BaseBoard
import chess

class CapturedPiecesDisplay(QLabel):
    """Display simple de piezas capturadas"""
    def __init__(self, color):
        super().__init__()
        self.color = color
        self.captured = []
        self.setStyleSheet("font-family: monospace; font-size: 14px; padding: 5px;")
        self.update_display()
        
    def add_piece(self, piece_type):
        self.captured.append(piece_type)
        self.update_display()
        
    def clear(self):
        self.captured.clear()
        self.update_display()
        
    def update_display(self):
        piece_symbols = {
            chess.PAWN: 'P',
            chess.KNIGHT: 'N',
            chess.BISHOP: 'B',
            chess.ROOK: 'R',
            chess.QUEEN: 'Q'
        }
        text = []
        for piece in sorted(self.captured):
            text.append(piece_symbols.get(piece, ''))
        self.setText(' '.join(text))

class ChessBoardWithCaptures(BaseBoard):
    def __init__(self):
        super().__init__()
        # Crear displays de piezas capturadas
        self.white_captured = CapturedPiecesDisplay(chess.WHITE)
        self.black_captured = CapturedPiecesDisplay(chess.BLACK)
        self.add_captured_displays()
        
    def add_captured_displays(self):
        # Crear layout para los displays de capturas
        captures_layout = QHBoxLayout()
        captures_layout.addWidget(QLabel("Capturadas blancas:"))
        captures_layout.addWidget(self.white_captured)
        captures_layout.addStretch()
        captures_layout.addWidget(QLabel("Capturadas negras:"))
        captures_layout.addWidget(self.black_captured)
        
        # Obtener el layout actual y añadir el display de capturas
        current_layout = self.layout()
        new_layout = QVBoxLayout()
        
        # Mover todos los widgets del layout actual al nuevo
        while current_layout.count():
            item = current_layout.takeAt(0)
            new_layout.addItem(item)
            
        # Añadir el display de capturas
        new_layout.addLayout(captures_layout)
        
        # Establecer el nuevo layout
        self.setLayout(new_layout)
        
    def _complete_move(self, move, move_san):
        # Verificar capturas antes de completar el movimiento
        if self.board.is_capture(move):
            captured_square = move.to_square
            captured_piece = self.board.piece_at(captured_square)
            if captured_piece:
                if captured_piece.color == chess.WHITE:
                    self.white_captured.add_piece(captured_piece.piece_type)
                else:
                    self.black_captured.add_piece(captured_piece.piece_type)
        
        # Llamar al método original
        super()._complete_move(move, move_san)
        
    def set_position_from_fen(self, fen: str):
        super().set_position_from_fen(fen)
        self.white_captured.clear()
        self.black_captured.clear()

class EnhancedMainWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        # Reemplazar el tablero base con nuestra versión mejorada
        self.board = ChessBoardWithCaptures()
        
        # Actualizar las conexiones del tablero
        self.board.move_made.connect(self.move_list.add_move)
        self.move_list.move_selected.connect(self.board.goto_position)
        
        # Actualizar el layout
        central_widget = self.centralWidget()
        layout = central_widget.layout()
        layout.removeWidget(layout.itemAt(0).widget())  # Remover el tablero antiguo
        layout.insertWidget(0, self.board)

def main():
    app = QApplication(sys.argv)
    window = EnhancedMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
