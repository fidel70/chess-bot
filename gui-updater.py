import os
import shutil
import re
from datetime import datetime

def backup_file(file_path):
    """Crea una copia de respaldo del archivo original."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{file_path}.{timestamp}.bak"
    shutil.copy2(file_path, backup_path)
    print(f"Backup creado: {backup_path}")

def update_gui_code(file_path):
    """Actualiza el código del GUI con los nuevos cambios."""
    # Hacer backup primero
    backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Eliminar el método get_move duplicado
    content = re.sub(r'def get_move\(self, board: chess\.Board\).*?return None, None\n\n\n', 
                    '', 
                    content, 
                    flags=re.DOTALL)
    
    # Actualizar la clase ChessEngine
    old_chess_engine = r'class ChessEngine:.*?def search\(self, board: chess\.Board\).*?return self\.minimax_engine\.search\(board\)'
    new_chess_engine = '''class ChessEngine:
    def __init__(self, evaluator, depth=3):
        self.minimax_engine = MinimaxEngine(evaluator, depth)
        self.lichess_db = LichessOpenings()
        
    def search(self, board: chess.Board) -> Tuple[chess.Move, float, Optional[str]]:
        # Primero intentar obtener un movimiento del libro de aperturas
        book_move, opening_info = self.lichess_db.get_move(board)
        
        if book_move:
            print(f"Usando movimiento del libro")
            return book_move, 0.0, opening_info
            
        # Si no hay movimiento del libro, usar el motor
        move, evaluation = self.minimax_engine.search(board)
        return move, evaluation, None'''
    
    content = re.sub(old_chess_engine, new_chess_engine, content, flags=re.DOTALL)
    
    # Actualizar la clase EngineControls
    old_engine_controls = r'class EngineControls\(QWidget\):.*?self\.engine_info\.setReadOnly\(True\)'
    new_engine_controls = '''class EngineControls(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Panel de apertura
        opening_panel = QGroupBox("Información de Apertura")
        opening_layout = QVBoxLayout()
        self.opening_label = QLabel("Apertura: ")
        self.opening_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #2c3e50;
                font-size: 12px;
                padding: 5px;
                background-color: #ecf0f1;
                border-radius: 3px;
            }
        """)
        opening_layout.addWidget(self.opening_label)
        opening_panel.setLayout(opening_layout)
        layout.addWidget(opening_panel)
        
        # Campo FEN
        fen_layout = QHBoxLayout()
        self.fen_input = QLineEdit()
        self.fen_input.setPlaceholderText("Introduce posición FEN")
        self.btn_set_position = QPushButton("Establecer")
        fen_layout.addWidget(self.fen_input)
        fen_layout.addWidget(self.btn_set_position)
        layout.addLayout(fen_layout)
        
        # Controles de profundidad
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(1, 20)
        self.depth_spin.setValue(3)
        layout.addWidget(QLabel("Profundidad:"))
        layout.addWidget(self.depth_spin)
        
        # Botón de análisis
        self.btn_analyze = QPushButton("Analizar")
        layout.addWidget(self.btn_analyze)
        
        # Panel de información del motor
        self.engine_info = QTextEdit()
        self.engine_info.setReadOnly(True)
        layout.addWidget(self.engine_info)'''
    
    content = re.sub(old_engine_controls, new_engine_controls, content, flags=re.DOTALL)
    
    # Actualizar el método analyze_position
    old_analyze = r'def analyze_position\(self\):.*?self\.engine_controls\.btn_analyze\.setEnabled\(True\)'
    new_analyze = '''def analyze_position(self):
        try:
            self.engine_controls.engine_info.setText("Analizando...")
            self.statusBar().showMessage('Analizando posición...')
            self.engine_controls.btn_analyze.setEnabled(False)
            
            QApplication.processEvents()
            
            depth = self.engine_controls.depth_spin.value()
            self.engine.max_depth = depth
            current_board = self.board.board
            
            best_move, evaluation, opening_info = self.engine.search(current_board)
            
            if opening_info:
                self.engine_controls.opening_label.setText(f"Apertura: {opening_info}")
            else:
                self.engine_controls.opening_label.setText("Apertura: (Fuera del libro de aperturas)")
            
            if best_move:
                move_san = current_board.san(best_move)
                self.move_sound.play()
                QTimer.singleShot(1500, lambda: self._complete_engine_move(
                    best_move, move_san, current_board, evaluation))
            else:
                self.engine_controls.btn_analyze.setEnabled(True)
                self.engine_controls.engine_info.setText("No se encontró un movimiento válido")
                
        except Exception as e:
            print(f"Error detallado: {str(e)}")
            self.statusBar().showMessage(f'Error en el análisis: {str(e)}')'''
    
    content = re.sub(old_analyze, new_analyze, content, flags=re.DOTALL)
    
    # Guardar los cambios
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("GUI actualizado exitosamente!")

def main():
    # Ruta al archivo run-gui.py
    gui_path = "run-gui.py"
    
    if not os.path.exists(gui_path):
        print(f"Error: No se encontró el archivo {gui_path}")
        return
    
    try:
        update_gui_code(gui_path)
    except Exception as e:
        print(f"Error actualizando el GUI: {str(e)}")

if __name__ == "__main__":
    main()
