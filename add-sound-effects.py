import re

def add_sound_effects():
    # Leer el archivo original
    with open('run-gui.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Añadir importación de QSound
    new_imports = '''import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtMultimedia import QSound
import chess'''
    
    # Reemplazar importaciones
    content = re.sub(
        r'import sys.*?import chess',
        new_imports,
        content,
        flags=re.DOTALL
    )
    
    # 2. Añadir inicialización del sonido en ChessBoard
    new_init = '''    def __init__(self):
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
    
    content = re.sub(
        r'def __init__.*?self\.current_animation = None',
        new_init,
        content,
        flags=re.DOTALL
    )
    
    # 3. Modificar handle_drop para reproducir sonido
    new_handle_drop = '''    def handle_drop(self, from_square, to_square):
        move = chess.Move(from_square, to_square)
        if self.board.turn and self.board.is_legal(move):
            # Guardar el movimiento en notación SAN antes de ejecutarlo
            move_san = self.board.san(move)
            self.board.push(move)
            self.move_history.append(move)
            self.placePieces()
            # Reproducir sonido de movimiento
            self.move_sound.play()
            # Emitir señal con el movimiento en notación SAN
            self.move_made.emit(move_san)
        else:
            print("Movimiento ilegal o no es tu turno.")'''
    
    content = re.sub(
        r'def handle_drop.*?print\("Movimiento ilegal o no es tu turno\."\)',
        new_handle_drop,
        content,
        flags=re.DOTALL
    )
    
    # 4. Modificar analyze_position para reproducir sonido
    new_analyze = '''    def analyze_position(self):
        try:
            self.engine_controls.engine_info.setText("Analizando...")
            self.statusBar().showMessage('Analizando posición...')
            self.engine_controls.btn_analyze.setEnabled(False)
            
            QApplication.processEvents()
            
            depth = self.engine_controls.depth_spin.value()
            self.engine.max_depth = depth
            current_board = self.board.board
            
            best_move, evaluation = self.engine.search(current_board)
            
            if best_move:
                from_square = best_move.from_square
                to_square = best_move.to_square
                
                # Obtener la notación SAN antes de hacer el movimiento
                move_san = current_board.san(best_move)
                
                # Actualizar el historial y emitir la señal
                current_board.push(best_move)
                self.board.move_history.append(best_move)
                self.board.placePieces()
                
                # Reproducir sonido de movimiento
                self.board.move_sound.play()
                
                self.move_list.add_move(move_san)
                
                analysis_text = f"Mejor movimiento: {move_san}\\nEvaluación: {evaluation/100:.2f}"
                self.engine_controls.engine_info.setText(analysis_text)
                self.statusBar().showMessage('Análisis completado')
                
            self.engine_controls.btn_analyze.setEnabled(True)
                
        except Exception as e:
            self.statusBar().showMessage(f'Error en el análisis: {str(e)}')
            self.engine_controls.engine_info.setText("Error durante el análisis")
            self.engine_controls.btn_analyze.setEnabled(True)'''
    
    content = re.sub(
        r'def analyze_position.*?self\.engine_controls\.btn_analyze\.setEnabled\(True\)',
        new_analyze,
        content,
        flags=re.DOTALL
    )
    
    # Guardar una copia de seguridad
    with open('run-gui.py.bak', 'w', encoding='utf-8') as file:
        file.write(content)
    
    # Guardar el archivo actualizado
    with open('run-gui.py', 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == '__main__':
    print("Añadiendo efectos de sonido a run-gui.py...")
    try:
        add_sound_effects()
        print("¡Modificaciones completadas!")
        print("Se ha creado una copia de seguridad en 'run-gui.py.bak'")
    except Exception as e:
        print(f"Error durante la modificación: {str(e)}")
