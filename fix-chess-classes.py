import re

def fix_chess_classes():
    # Leer el archivo original
    with open('run-gui.py', 'r', encoding='utf-8') as file:
        content = file.read()

    # Corregir la clase ChessPiece
    new_chess_piece = '''class ChessPiece(QSvgWidget):
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
        self.setFixedSize(50, 50)'''

    # Corregir la clase ChessBoard
    new_chess_board = '''class ChessBoard(QWidget):
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

    # Reemplazar las clases en el contenido
    content = re.sub(
        r'class ChessPiece\(QSvgWidget\):.*?self\.setFixedSize\(50, 50\)',
        new_chess_piece,
        content,
        flags=re.DOTALL
    )

    # Hacer el reemplazo desde el inicio de ChessBoard
    chess_board_pattern = re.compile(r'class ChessBoard\(QWidget\):.*?def initUI', flags=re.DOTALL)
    content = chess_board_pattern.sub(f'class ChessBoard(QWidget):\n    {new_chess_board}\n\n    def initUI', content)

    # Guardar una copia de seguridad
    with open('run-gui.py.bak', 'w', encoding='utf-8') as file:
        file.write(content)

    # Guardar el archivo actualizado
    with open('run-gui.py', 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == '__main__':
    print("Corrigiendo clases de ajedrez en run-gui.py...")
    try:
        fix_chess_classes()
        print("¡Corrección completada!")
        print("Se ha creado una copia de seguridad en 'run-gui.py.bak'")
    except Exception as e:
        print(f"Error durante la corrección: {str(e)}")
