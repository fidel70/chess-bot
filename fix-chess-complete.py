import re

def fix_chess_complete():
    # Leer el archivo original
    with open('run-gui.py', 'r', encoding='utf-8') as file:
        content = file.read()

    # Definir las clases en el orden correcto
    chess_classes = '''class ChessPiece(QSvgWidget):
    def __init__(self, piece, parent=None):
        super().__init__(parent)
        self.piece = piece
        self.load_svg()
        
    def load_svg(self):
        piece_map = {
            'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK',
            'p': 'bP', 'n': 'bN', 'b': 'bB', 'r': 'bR', 'q': 'bQ', 'k': 'bK'
        }
        piece_file = f"{piece_map[self.piece]}.svg"
        path = os.path.join('gui', 'resources', 'pieces', piece_file)
        self.load(path)
        self.setFixedSize(50, 50)

class ChessSquare(QLabel):
    def __init__(self, position, color, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.position = position
        self.setFixedSize(70, 70)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"background-color: {color};")

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        source_square = int(event.mimeData().text())
        destination_square = self.position
        self.parent().handle_drop(source_square, destination_square)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.parent().pieces.get(self.position):
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(str(self.position))
            drag.setMimeData(mime_data)
            piece = self.parent().pieces[self.position]
            pixmap = piece.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.MoveAction)

class ChessBoard(QWidget):
    move_made = pyqtSignal(str)  # Nueva señal para movimientos realizados

    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        self.squares = {}
        self.pieces = {}
        self.move_history = []  # Lista para almacenar el historial de movimientos
        self.initUI()
        self.placePieces()
        self.current_animation = None
        
        # Inicializar sonido de movimiento
        sound_path = os.path.join('gui', 'resources', 'sounds', 'move.wav')
        self.move_sound = QSound(sound_path)'''

    # Encontrar dónde empiezan las clases actuales
    start = content.find('class ChessPiece')
    end = content.find('class MoveList')

    # Reemplazar las clases antiguas con las nuevas
    new_content = content[:start] + chess_classes + '\n\n' + content[end:]

    # Guardar una copia de seguridad
    with open('run-gui.py.bak', 'w', encoding='utf-8') as file:
        file.write(content)

    # Guardar el archivo actualizado
    with open('run-gui.py', 'w', encoding='utf-8') as file:
        file.write(new_content)

if __name__ == '__main__':
    print("Corrigiendo completamente las clases de ajedrez en run-gui.py...")
    try:
        fix_chess_complete()
        print("¡Corrección completada!")
        print("Se ha creado una copia de seguridad en 'run-gui.py.bak'")
    except Exception as e:
        print(f"Error durante la corrección: {str(e)}")
