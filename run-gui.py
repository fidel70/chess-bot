import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from typing import Optional, Tuple, List
import chess
import pygame
import time
import random
import requests
from typing import Optional
pygame.mixer.init()

# Configurar path del proyecto
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Importaciones del motor
from engine.search.evaluator.material import MaterialEvaluator
from engine.search.minimax import MinimaxEngine
from engine.search.zobrist_hash import ZobristHash


class LichessOpenings:
    def __init__(self):
        self.base_url = "https://explorer.lichess.ovh/masters"
        self.opening_cache = {}
        self.last_request_time = 0
        
    # Modificar la clase MainWindow, solo el método __init__:
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chess Engine GUI')
        self.setMinimumSize(800, 600)
        
        # Inicializar el sonido
        sound_path = os.path.join(os.path.dirname(__file__), 'gui', 'resources', 'sounds', 'move.mp3')
        self.move_sound = pygame.mixer.Sound(sound_path)
        
        self.material_evaluator = MaterialEvaluator()
        self.engine = ChessEngine(self.material_evaluator, depth=3)
        
        self.initUI()
            
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.createMenuBar()
        
        main_layout = QHBoxLayout(central_widget)
        
        left_layout = QVBoxLayout()
        self.board = ChessBoard()
        left_layout.addWidget(self.board)
        
        right_panel = QVBoxLayout()
        
        self.move_list = MoveList()
        right_panel.addWidget(self.move_list)
        
        self.engine_controls = EngineControls()
        right_panel.addWidget(self.engine_controls)
        
                        # Conectar señales
        self.engine_controls.btn_set_position.clicked.connect(self.set_position)
        self.engine_controls.btn_analyze.clicked.connect(self.analyze_position)
        
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_panel, 1)
        
        # Conectar señales del tablero y la lista de movimientos
        self.board.move_made.connect(self.move_list.add_move)
        self.move_list.move_selected.connect(self.board.goto_position)

    def createMenuBar(self):
        menubar = self.menuBar()
            
        file_menu = menubar.addMenu('Archivo')
        new_game = file_menu.addAction('Nueva Partida')
        load_game = file_menu.addAction('Cargar PGN')
        save_game = file_menu.addAction('Guardar PGN')
        file_menu.addSeparator()
        exit_action = file_menu.addAction('Salir')
        
        engine_menu = menubar.addMenu('Motor')
        start_analysis = engine_menu.addAction('Iniciar Análisis')
        stop_analysis = engine_menu.addAction('Detener Análisis')
        engine_menu.addSeparator()
        engine_settings = engine_menu.addAction('Configuración')

    def analyze_position(self):
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
            self.statusBar().showMessage(f'Error en el análisis: {str(e)}')
                self.engine_controls.engine_info.setText("No se encontró un movimiento válido")
                
        except Exception as e:
            print(f"Error detallado: {str(e)}")  # Debug
            self.statusBar().showMessage(f'Error en el análisis: {str(e)}')
            
    def _complete_engine_move(self, move, move_san, current_board, evaluation):
        """Completa el movimiento del motor y actualiza la interfaz"""
        try:
            # Actualizar el historial y emitir la señal
            current_board.push(move)
            self.board.move_history.append(move)
            self.board.placePieces()
            
            # Actualizar la lista de movimientos
            self.move_list.add_move(move_san)
            
            # Actualizar la información del análisis
            analysis_text = f"Mejor movimiento: {move_san} - Evaluación: {evaluation/100:.2f}"
            self.engine_controls.engine_info.setText(analysis_text)
            self.statusBar().showMessage('Análisis completado')
            
        except Exception as e:
            self.statusBar().showMessage(f'Error al completar el movimiento: {str(e)}')
            self.engine_controls.engine_info.setText("Error al ejecutar el movimiento")
        finally:
            self.engine_controls.btn_analyze.setEnabled(True)       

    
    def set_position(self):
        try:
            fen = self.engine_controls.fen_input.text()
            self.board.set_position_from_fen(fen)
            self.statusBar().showMessage('Posición establecida')
        except ValueError as e:
            self.statusBar().showMessage(f'Error: {str(e)}')        

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
