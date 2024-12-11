import re

# Ruta del archivo original
file_path = "run-gui-modified.py"

# Leer el contenido original del archivo
with open(file_path, "r", encoding="utf-8") as file:
    original_code = file.read()

# Añadir el botón de reinicio en `initUI`
reset_button_code = """
        # Añadir botón de reinicio debajo del tablero
        self.reset_button = QPushButton("Reiniciar partida")
        self.reset_button.clicked.connect(self.reset_game)
        left_layout.addWidget(self.reset_button)
"""

modified_code = re.sub(
    r"self.board = ChessBoard\(\)\s+left_layout\.addWidget\(self\.board\)",
    r"self.board = ChessBoard()\n        left_layout.addWidget(self.board)" + reset_button_code,
    original_code,
)

# Añadir el método reset_game en la clase MainWindow
reset_game_method = """
    def reset_game(self):
        \"\"\"Reinicia la partida colocando el tablero en la posición inicial.\"\"\"
        if not self.engine_controls.btn_analyze.isEnabled():
            self.statusBar().showMessage("Espera a que termine el análisis antes de reiniciar.")
            return
        self.board.board.reset()  # Resetea el tablero de ajedrez
        self.board.placePieces()  # Actualiza la visualización del tablero
        self.move_list.move_list.clear()  # Limpia la lista de movimientos
        self.engine_controls.engine_info.clear()  # Limpia la información del motor
        self.statusBar().showMessage("Partida reiniciada.")
"""

modified_code = re.sub(
    r"(class MainWindow\(QMainWindow\):.*?def createMenuBar\(self\):)",
    r"\1" + reset_game_method,
    modified_code,
    flags=re.DOTALL,
)

# Guardar el archivo modificado
output_path = "run-gui-with-reset.py"
with open(output_path, "w", encoding="utf-8") as file:
    file.write(modified_code)

print(f"Archivo modificado guardado como {output_path}.")
