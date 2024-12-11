import re

def fix_chess_gui():
    # Leer el archivo original
    with open('run-gui.py', 'r', encoding='utf-8') as file:
        content = file.read()

    # 1. Limpiar importaciones duplicadas
    clean_imports = '''import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import QSvgWidget
import chess

# Configurar path del proyecto
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Importaciones del motor
from engine.search.evaluator.material import MaterialEvaluator
from engine.search.minimax import MinimaxEngine
from engine.search.zobrist_hash import ZobristHash'''

    # Encontrar dónde terminan las importaciones
    imports_end = content.find('class ChessPiece')
    content = clean_imports + '\n\n' + content[imports_end:]

    # 2. Corregir la clase ChessBoard
    chessboard_start = '''class ChessBoard(QWidget):
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

    def handle_drop(self, from_square, to_square):
        move = chess.Move(from_square, to_square)
        if self.board.turn and self.board.is_legal(move):
            # Guardar el movimiento en notación SAN antes de ejecutarlo
            move_san = self.board.san(move)
            self.board.push(move)
            self.move_history.append(move)
            self.placePieces()
            # Emitir señal con el movimiento en notación SAN
            self.move_made.emit(move_san)
        else:
            print("Movimiento ilegal o no es tu turno.")'''

    # Reemplazar la clase ChessBoard
    old_chessboard = re.search(r'class ChessBoard.*?def initUI', content, re.DOTALL).group()
    content = content.replace(old_chessboard, chessboard_start + "\n\n    def initUI")

    # 3. Asegurar que las conexiones de señales estén correctas en MainWindow
    mainwindow_signals = '''        # Conectar señales
        self.engine_controls.btn_set_position.clicked.connect(self.set_position)
        self.engine_controls.btn_analyze.clicked.connect(self.analyze_position)
        
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_panel, 1)
        
        # Conectar señales del tablero y la lista de movimientos
        self.board.move_made.connect(self.move_list.add_move)
        self.move_list.move_selected.connect(self.board.goto_position)'''

    # Reemplazar las conexiones de señales en MainWindow
    content = re.sub(
        r'# Conectar señales.*?main_layout\.addLayout\(right_panel, 1\)',
        mainwindow_signals,
        content,
        flags=re.DOTALL
    )

    # Guardar una copia de seguridad del archivo original
    with open('run-gui.py.bak', 'w', encoding='utf-8') as file:
        file.write(content)

    # Escribir el archivo corregido
    with open('run-gui.py', 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == '__main__':
    print("Corrigiendo run-gui.py...")
    try:
        fix_chess_gui()
        print("¡Corrección completada!")
        print("Se ha creado una copia de seguridad en 'run-gui.py.bak'")
    except Exception as e:
        print(f"Error durante la corrección: {str(e)}")
