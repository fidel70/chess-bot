import os
import sys
import glob
import re

def fix_chess_board_class():
    """Agrega los métodos faltantes a la clase ChessBoard"""
    fixes = """
    def goto_position(self, move_index):
        # Recrear el tablero hasta el movimiento seleccionado
        self.board = chess.Board()
        for i in range(move_index + 1):
            if i < len(self.move_history):
                self.board.push(self.move_history[i])
        self.placePieces()

    def animate_move(self, from_square, to_square):
        if from_square not in self.pieces:
            return
                
        piece = self.pieces[from_square]
        start_pos = self.squares[from_square].pos()
        end_pos = self.squares[to_square].pos()
        
        temp_piece = ChessPiece(piece.piece, self)
        temp_piece.setFixedSize(50, 50)
        temp_piece.move(start_pos)
        temp_piece.show()
        
        self.current_animation = QPropertyAnimation(temp_piece, b"pos")
        self.current_animation.setDuration(500)
        self.current_animation.setStartValue(start_pos)
        self.current_animation.setEndValue(end_pos)
        self.current_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.current_animation.finished.connect(
            lambda: self.finish_move(from_square, to_square, temp_piece)
        )
        
        self.current_animation.start()

    def finish_move(self, from_square, to_square, temp_piece):
        temp_piece.deleteLater()
        move = chess.Move(from_square, to_square)
        if self.board.is_legal(move):
            self.board.push(move)
            self.move_history.append(move)
            self.placePieces()
            self.move_made.emit(self.board.san(move))
    """
    return fixes

def fix_move_list_class():
    """Agrega los métodos de navegación faltantes a MoveList"""
    fixes = """
    def goto_first(self):
        if self.moves:
            self.current_move = 0
            self.move_list.setCurrentRow(0)
            self.move_selected.emit(0)
            self.update_navigation_buttons()

    def goto_prev(self):
        if self.current_move > 0:
            self.current_move -= 1
            self.move_list.setCurrentRow(self.current_move)
            self.move_selected.emit(self.current_move)
            self.update_navigation_buttons()

    def goto_next(self):
        if self.current_move < len(self.moves) - 1:
            self.current_move += 1
            self.move_list.setCurrentRow(self.current_move)
            self.move_selected.emit(self.current_move)
            self.update_navigation_buttons()

    def goto_last(self):
        if self.moves:
            self.current_move = len(self.moves) - 1
            self.move_list.setCurrentRow(self.current_move)
            self.move_selected.emit(self.current_move)
            self.update_navigation_buttons()

    def on_move_clicked(self, item):
        row = self.move_list.row(item)
        self.current_move = row
        self.move_selected.emit(row)
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        has_moves = bool(self.moves)
        self.btn_first.setEnabled(has_moves and self.current_move > 0)
        self.btn_prev.setEnabled(has_moves and self.current_move > 0)
        self.btn_next.setEnabled(has_moves and self.current_move < len(self.moves) - 1)
        self.btn_last.setEnabled(has_moves and self.current_move < len(self.moves) - 1)
    """
    return fixes

def fix_main_window_class():
    """Corrige la gestión del sonido y conexiones en MainWindow"""
    fixes = """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chess Engine GUI')
        self.setMinimumSize(800, 600)
        
        # Inicializar evaluador y motor
        self.material_evaluator = MaterialEvaluator()
        self.engine = ChessEngine(self.material_evaluator, depth=3)
        
        self.initUI()
    """
    return fixes

def create_resource_directories():
    """Crea las carpetas necesarias para recursos"""
    dirs = [
        'gui/resources/pieces',
        'gui/resources/sounds'
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def apply_fixes(file_path):
    """Aplica todas las correcciones al archivo"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Reemplazar las clases con las versiones corregidas
    content = re.sub(
        r'class ChessBoard\(QWidget\):.*?def initUI\(self\):',
        'class ChessBoard(QWidget):\n' + fix_chess_board_class() + '\n    def initUI(self):',
        content,
        flags=re.DOTALL
    )

    content = re.sub(
        r'class MoveList\(QWidget\):.*?def initUI\(self\):',
        'class MoveList(QWidget):\n' + fix_move_list_class() + '\n    def initUI(self):',
        content,
        flags=re.DOTALL
    )

    content = re.sub(
        r'class MainWindow\(QMainWindow\):.*?def initUI\(self\):',
        'class MainWindow(QMainWindow):\n' + fix_main_window_class() + '\n    def initUI(self):',
        content,
        flags=re.DOTALL
    )

    # Guardar el archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # Crear estructura de directorios
    create_resource_directories()
    
    # Buscar y corregir el archivo principal
    main_file = glob.glob('*.py')[0]
    apply_fixes(main_file)
    
    print(f"Correcciones aplicadas exitosamente a {main_file}")
    print("\nPasos adicionales necesarios:")
    print("1. Asegúrate de tener los archivos de sonido en gui/resources/sounds/")
    print("2. Coloca las imágenes SVG de las piezas en gui/resources/pieces/")
    print("3. Instala las dependencias necesarias:")
    print("   pip install python-chess PyQt5 pygame requests")

if __name__ == '__main__':
    main()
