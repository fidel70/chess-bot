import re

# Cargar el archivo original
file_path = "run-gui.py"
with open(file_path, "r", encoding="utf-8") as file:
    original_code = file.read()

# Añadir los métodos necesarios a ChessSquare
square_modifications = """
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
            mime_data.setText(str(self.position))  # Transfiere la posición de origen
            drag.setMimeData(mime_data)

            piece = self.parent().pieces[self.position]
            pixmap = piece.grab()  # Captura la pieza para arrastrar
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())  # Define el punto de arrastre
            drag.exec_(Qt.MoveAction)
"""

# Insertar en la clase ChessSquare
modified_code = re.sub(
    r"class ChessSquare\(QLabel\):",
    r"class ChessSquare(QLabel):" + square_modifications,
    original_code,
)

# Añadir el método handle_drop a ChessBoard
board_modifications = """
    def handle_drop(self, from_square, to_square):
        move = chess.Move(from_square, to_square)
        if self.board.turn and self.board.is_legal(move):
            self.board.push(move)
            self.placePieces()
        else:
            print("Movimiento ilegal o no es tu turno.")
"""

# Insertar en la clase ChessBoard
modified_code = re.sub(
    r"class ChessBoard\(QWidget\):",
    r"class ChessBoard(QWidget):" + board_modifications,
    modified_code,
)

# Añadir soporte para arrastrar y soltar en ChessSquare
square_init_modifications = """
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
"""

# Insertar en el constructor de ChessSquare
modified_code = re.sub(
    r"def __init__\(self, position, color, parent=None\):\s*super\(\).__init__\(parent\)",
    r"def __init__(self, position, color, parent=None):\n        super().__init__(parent)" + square_init_modifications,
    modified_code,
)

# Guardar el archivo modificado
output_path = "run-gui-modified.py"
with open(output_path, "w", encoding="utf-8") as file:
    file.write(modified_code)

print(f"Código modificado guardado en {output_path}.")
