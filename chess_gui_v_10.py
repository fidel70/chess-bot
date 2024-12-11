import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import QSvgWidget
import chess
import time
import random
import requests
from typing import Optional, Tuple, List
import pygame
pygame.mixer.init()

# Obtener la ruta absoluta del directorio raíz del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(project_root)
sys.path.append(project_root)

# # Configuración del proyecto
# project_root = os.path.dirname(os.path.abspath(__file__))
# if project_root not in sys.path:
#     sys.path.append(project_root)

# Importaciones del motor
#from motor.search.evaluator.material import MaterialEvaluator
from chess_bot.motor.search.minimax.simple_chess_engine import MinimaxEngine, MaterialEvaluator
#from chess_bot.motor.search.zobrist_hash import ZobristHash

class LichessOpenings:
    """Clase mejorada para manejar la base de datos de aperturas de Lichess"""
    def __init__(self):
        self.base_url = "https://explorer.lichess.ovh/masters"
        self.opening_cache = {}
        self.last_request_time = 0
        self.headers = {
            'User-Agent': 'Chess Engine/1.0'
        }
        
    def get_move(self, board: chess.Board) -> Tuple[Optional[chess.Move], Optional[str]]:
        """Obtiene un movimiento de la base de datos de aperturas de Lichess"""
        try:
            # Revisar cache primero
            fen = board.fen()
            if fen in self.opening_cache:
                print("[INFO] Usando movimiento cacheado")
                return random.choice(self.opening_cache[fen]), self.opening_cache.get(f"{fen}_opening")
            
            # Preparar parámetros de la consulta
            params = {
                'fen': fen,
                'topGames': 0,
                'recentGames': 0,
                'moves': 50,
                'variant': 'standard'
            }
            
            print(f"[INFO] Consultando Lichess API para FEN: {fen}")
            response = requests.get(
                self.base_url, 
                params=params, 
                headers=self.headers,
                timeout=5
            )
            
            # Verificar respuesta HTTP
            if response.status_code != 200:
                print(f"[WARNING] Error HTTP {response.status_code} al consultar Lichess")
                return None, None
                
            # Parsear respuesta JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                print("[ERROR] Error al decodificar respuesta JSON de Lichess")
                return None, None
                
            # Procesar información de apertura
            opening_info = None
            if 'opening' in data and data['opening']:
                opening_info = f"{data['opening'].get('name', 'Unknown')} ({data['opening'].get('eco', '?')})"
                print(f"[INFO] Apertura encontrada: {opening_info}")
            
            # Verificar si hay movimientos disponibles
            if not data.get('moves'):
                print("[INFO] No se encontraron movimientos en la base de datos de aperturas")
                return None, None
            
            # Procesar movimientos
            available_moves = []
            total_plays = 0
            
            # Calcular total de jugadas para ponderación
            for move_data in data['moves']:
                total_plays += move_data.get('white', 0) + move_data.get('black', 0)
            
            if total_plays == 0:
                print("[INFO] No hay estadísticas de juego disponibles")
                return None, None
            
            # Procesar cada movimiento
            for move_data in data['moves']:
                if 'uci' not in move_data:
                    continue
                    
                try:
                    move = chess.Move.from_uci(move_data['uci'])
                    if move not in board.legal_moves:
                        continue
                        
                    # Calcular peso basado en frecuencia
                    weight = (move_data.get('white', 0) + move_data.get('black', 0)) / total_plays
                    num_entries = int(weight * 100)
                    
                    if num_entries > 0:
                        available_moves.extend([move] * num_entries)
                        print(f"[INFO] Movimiento añadido: {move_data.get('san', move_data['uci'])} "
                              f"(peso: {weight:.2f}, entradas: {num_entries})")
                        
                except ValueError as e:
                    print(f"[WARNING] Error al procesar movimiento {move_data.get('uci')}: {e}")
                    continue
            
            if available_moves:
                # Guardar en cache
                self.opening_cache[fen] = available_moves
                if opening_info:
                    self.opening_cache[f"{fen}_opening"] = opening_info
                
                # Seleccionar movimiento
                chosen_move = random.choice(available_moves)
                print(f"[INFO] Movimiento elegido del libro: {board.san(chosen_move)}")
                return chosen_move, opening_info
            else:
                print("[INFO] No se encontraron movimientos válidos en la base de datos")
                return None, None
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error en la petición HTTP: {str(e)}")
            return None, None
        except Exception as e:
            print(f"[ERROR] Error inesperado al consultar base de datos: {str(e)}")
            return None, None

class ChessEngine:
    """Motor de ajedrez principal que combina minimax con base de datos de aperturas"""
    def __init__(self, evaluator, depth):
        self.minimax_engine = MinimaxEngine(evaluator, depth)
        self.lichess_db = LichessOpenings()
        
    def search(self, board: chess.Board) -> Tuple[chess.Move, float, Optional[str]]:
        """Busca el mejor movimiento usando libro de aperturas o motor"""
        # Intentar obtener movimiento del libro
        book_move, opening_info = self.lichess_db.get_move(board)
        
        if book_move is not None:
            print("[INFO] Usando movimiento del libro de aperturas")
            return book_move, 0.0, opening_info
            
        # Si no hay movimiento en el libro, usar el motor
        print("[INFO] Libro de aperturas agotado, usando motor minimax")
        move, evaluation = self.minimax_engine.search(board)
        return move, evaluation, None

class ChessPiece(QSvgWidget):
    """Widget para representar una pieza de ajedrez usando SVG"""
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
    """Representa una casilla del tablero con soporte para drag & drop"""
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
    """Tablero de ajedrez interactivo"""
    move_made = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        self.squares = {}
        self.pieces = {}
        self.move_history = []
        self.current_animation = None
        self.initUI()
        self.placePieces()
        
        # Configurar sonido
        sound_path = os.path.join('gui', 'resources', 'sounds', 'move.mp3')
        self.move_sound = pygame.mixer.Sound(sound_path) if os.path.exists(sound_path) else None

    def initUI(self):
        """Inicializa la interfaz del tablero"""
        main_layout = QGridLayout()
        self.setLayout(main_layout)
        board_grid = QGridLayout()
        colors = ['#F0D9B5', '#B58863']
        
        # Añadir etiquetas de filas y columnas
        for rank in range(8):
            rank_label = QLabel(str(8 - rank))
            rank_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            main_layout.addWidget(rank_label, rank + 1, 0)
        
        for file in range(8):
            file_label = QLabel(chr(97 + file))
            file_label.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
            main_layout.addWidget(file_label, 9, file + 1)
        
        # Crear casillas del tablero
        for rank in range(8):
            for file in range(8):
                color = colors[(rank + file) % 2]
                position = chess.square(file, 7-rank)
                square = ChessSquare(position, color)
                self.squares[position] = square
                board_grid.addWidget(square, rank, file)
        
        main_layout.addLayout(board_grid, 1, 1, 8, 8)
        main_layout.setSpacing(5)
        board_grid.setSpacing(0)

    def handle_drop(self, from_square, to_square):
        """Maneja el evento de soltar una pieza"""
        move = chess.Move(from_square, to_square)
        if self.board.is_legal(move):
            if self.move_sound:
                self.move_sound.play()
            move_san = self.board.san(move)
            QTimer.singleShot(500, lambda: self._complete_move(move, move_san))
        else:
            print("Movimiento ilegal")

    def _complete_move(self, move, move_san):
        """Completa un movimiento y actualiza el estado del juego"""
        self.board.push(move)
        self.move_history.append(move)
        self.placePieces()
        self.move_made.emit(move_san)

    def goto_position(self, move_index):
        """Va a una posición específica en la historia de movimientos"""
        self.board = chess.Board()
        for i in range(move_index + 1):
            if i < len(self.move_history):
                self.board.push(self.move_history[i])
        self.placePieces()

    def placePieces(self):
        """Coloca las piezas en el tablero"""
        # Limpiar piezas existentes
        for square in chess.SQUARES:
            if self.squares[square].layout():
                old_layout = self.squares[square].layout()
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                QWidget().setLayout(old_layout)

        self.pieces.clear()

        # Colocar nuevas piezas
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                chess_piece = ChessPiece(piece.symbol())
                layout = QVBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(chess_piece)
                self.squares[square].setLayout(layout)
                self.pieces[square] = chess_piece

    def set_position_from_fen(self, fen: str):
        """Establece una posición a partir de una cadena FEN"""
        try:
            self.board = chess.Board(fen)
            self.move_history.clear()
            self.placePieces()
        except ValueError as e:
            raise ValueError(f"FEN inválido: {str(e)}")

class MoveList(QWidget):
    """Lista de movimientos con controles de navegación"""
    move_selected = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_move = -1
        self.moves = []
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Lista de movimientos
        self.move_list = QListWidget()
        self.move_list.itemClicked.connect(self.on_move_clicked)
        layout.addWidget(self.move_list)
        
        # Controles de navegación
        nav_layout = QHBoxLayout()
        self.btn_first = QPushButton("<<")
        self.btn_prev = QPushButton("<")
        self.btn_next = QPushButton(">")
        self.btn_last = QPushButton(">>")
        
        self.btn_first.clicked.connect(self.goto_first)
        self.btn_prev.clicked.connect(self.goto_prev)
        self.btn_next.clicked.connect(self.goto_next)
        self.btn_last.clicked.connect(self.goto_last)
        
        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last]:
            nav_layout.addWidget(btn)
            
        layout.addLayout(nav_layout)
        self.update_navigation_buttons()

    def add_move(self, move_san):
        """Añade un movimiento a la lista"""
        move_number = len(self.moves) // 2 + 1
        if len(self.moves) % 2 == 0:
            text = f"{move_number}. {move_san}"
        else:
            text = f"{move_number}... {move_san}"
            
        self.moves.append(move_san)
        self.move_list.addItem(text)
        self.current_move = len(self.moves) - 1
        self.move_list.setCurrentRow(self.current_move)
        self.update_navigation_buttons()

    def goto_first(self):
        """Va al primer movimiento"""
        if self.moves:
            self.current_move = 0
            self.move_list.setCurrentRow(0)
            self.move_selected.emit(0)
            self.update_navigation_buttons()

    def goto_prev(self):
        """Va al movimiento anterior"""
        if self.current_move > 0:
            self.current_move -= 1
            self.move_list.setCurrentRow(self.current_move)
            self.move_selected.emit(self.current_move)
            self.update_navigation_buttons()

    def goto_next(self):
        """Va al siguiente movimiento"""
        if self.current_move < len(self.moves) - 1:
            self.current_move += 1
            self.move_list.setCurrentRow(self.current_move)
            self.move_selected.emit(self.current_move)
            self.update_navigation_buttons()

    def goto_last(self):
        """Va al último movimiento"""
        if self.moves:
            self.current_move = len(self.moves) - 1
            self.move_list.setCurrentRow(self.current_move)
            self.move_selected.emit(self.current_move)
            self.update_navigation_buttons()

    def on_move_clicked(self, item):
        """Maneja el clic en un movimiento"""
        row = self.move_list.row(item)
        self.current_move = row
        self.move_selected.emit(row)
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Actualiza el estado de los botones de navegación"""
        has_moves = bool(self.moves)
        self.btn_first.setEnabled(has_moves and self.current_move > 0)
        self.btn_prev.setEnabled(has_moves and self.current_move > 0)
        self.btn_next.setEnabled(has_moves and self.current_move < len(self.moves) - 1)
        self.btn_last.setEnabled(has_moves and self.current_move < len(self.moves) - 1)

class EngineControls(QWidget):
    """Panel de control del motor de ajedrez"""
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayoutlayout = QVBoxLayout()
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
        
        # Control de profundidad
        depth_layout = QHBoxLayout()
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(1, 6)
        self.depth_spin.setValue(3)
        depth_layout.addWidget(QLabel("Profundidad de búsqueda:"))
        depth_layout.addWidget(self.depth_spin)
        layout.addLayout(depth_layout)
        
        # Botón de análisis
        self.btn_analyze = QPushButton("Analizar Posición")
        self.btn_analyze.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219a52;
            }
        """)
        layout.addWidget(self.btn_analyze)
        
        # Panel de información del motor
        info_group = QGroupBox("Información del Análisis")
        info_layout = QVBoxLayout()
        self.engine_info = QTextEdit()
        self.engine_info.setReadOnly(True)
        self.engine_info.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        info_layout.addWidget(self.engine_info)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    def __init__(self):
        depth = 3
        super().__init__()
        self.setWindowTitle('Motor de Ajedrez - Análisis Inteligente')
        self.setMinimumSize(1000, 700)
        
        # Inicializar componentes del motor
        self.material_evaluator = MaterialEvaluator()
        #self.engine = ChessEngine(self.material_evaluator)

        self.engine = MinimaxEngine(self.material_evaluator, depth=3)



        # Configurar sonido
        sound_path = os.path.join('gui', 'resources', 'sounds', 'move.mp3')
        pygame.mixer.init()
        self.move_sound = pygame.mixer.Sound(sound_path) if os.path.exists(sound_path) else None
        
        self.initUI()
        self.create_status_bar()
    
    def initUI(self):
        """Inicializa la interfaz de usuario principal"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Crear menú
        self.createMenuBar()
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Panel izquierdo (tablero)
        left_panel = QVBoxLayout()
        self.board = ChessBoard()
        left_panel.addWidget(self.board)
        
        # Panel derecho (controles)
        right_panel = QVBoxLayout()
        
        # Lista de movimientos
        self.move_list = MoveList()
        right_panel.addWidget(self.move_list)
        
        # Controles del motor
        self.engine_controls = EngineControls()
        right_panel.addWidget(self.engine_controls)
        
        # Conectar señales
        self.engine_controls.btn_set_position.clicked.connect(self.set_position)
        self.engine_controls.btn_analyze.clicked.connect(self.analyze_position)
        self.board.move_made.connect(self.move_list.add_move)
        self.move_list.move_selected.connect(self.board.goto_position)
        
        # Añadir paneles al layout principal
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)

    def createMenuBar(self):
        """Crea la barra de menú"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu('Archivo')
        new_game = file_menu.addAction('Nueva Partida')
        new_game.triggered.connect(self.new_game)
        load_game = file_menu.addAction('Cargar PGN')
        load_game.triggered.connect(self.load_pgn)
        save_game = file_menu.addAction('Guardar PGN')
        save_game.triggered.connect(self.save_pgn)
        file_menu.addSeparator()
        exit_action = file_menu.addAction('Salir')
        exit_action.triggered.connect(self.close)
        
        # Menú Motor
        engine_menu = menubar.addMenu('Motor')
        engine_settings = engine_menu.addAction('Configuración')
        engine_settings.triggered.connect(self.show_engine_settings)

    def create_status_bar(self):
        """Crea la barra de estado"""
        self.statusBar().showMessage('Listo')

    def analyze_position(self):
        """Analiza la posición actual"""
        try:
            self.engine_controls.engine_info.setText("Analizando posición...")
            self.statusBar().showMessage('Analizando...')
            self.engine_controls.btn_analyze.setEnabled(False)
            
            QApplication.processEvents()
            
            depth = self.engine_controls.depth_spin.value()
            self.engine.max_depth = depth  # Ahora esto funciona directamente
            current_board = self.board.board
            
            # Debug prints
            print(f"[DEBUG] Posición actual FEN: {current_board.fen()}")
            print(f"[DEBUG] Turno actual: {'Negras' if current_board.turn == chess.BLACK else 'Blancas'}")
            print(f"[DEBUG] Movimientos legales: {[current_board.san(move) for move in current_board.legal_moves]}")
            
            # Ahora llamamos directamente al motor
            best_move, evaluation = self.engine.search(current_board)
            
            if best_move:
                move_san = current_board.san(best_move)
                if self.move_sound:
                    self.move_sound.play()
                QTimer.singleShot(500, lambda: self._complete_engine_move(
                    best_move, move_san, current_board, evaluation))
                
                self.engine_controls.opening_label.setText("Apertura: (Fuera del libro)")
                
        except Exception as e:
            self.statusBar().showMessage(f'Error: {str(e)}')
            self.engine_controls.engine_info.setText(f"Error en el análisis: {str(e)}")
            self.engine_controls.btn_analyze.setEnabled(True)

    def _complete_engine_move(self, move, move_san, current_board, evaluation):
        """Completa el movimiento del motor"""
        try:
            current_board.push(move)
            self.board.move_history.append(move)
            self.board.placePieces()
            
            self.move_list.add_move(move_san)
            
            eval_text = "+" if evaluation > 0 else "" if evaluation == 0 else "-"
            eval_text += f"{abs(evaluation/100):.2f}"
            
            analysis_text = (
                f"Mejor movimiento: {move_san}\n"
                f"Evaluación: {eval_text}\n"
                f"Profundidad: {self.engine_controls.depth_spin.value()}"
            )
            self.engine_controls.engine_info.setText(analysis_text)
            self.statusBar().showMessage('Análisis completado')
            
        except Exception as e:
            self.statusBar().showMessage(f'Error al completar movimiento: {str(e)}')
            self.engine_controls.engine_info.setText("Error al ejecutar el movimiento")
        finally:
            self.engine_controls.btn_analyze.setEnabled(True)

    def set_position(self):
        """Establece una posición FEN"""
        try:
            fen = self.engine_controls.fen_input.text()
            self.board.set_position_from_fen(fen)
            self.move_list.moves.clear()
            self.move_list.move_list.clear()
            self.statusBar().showMessage('Posición establecida')
            self.engine_controls.opening_label.setText("Apertura: ")
        except ValueError as e:
            self.statusBar().showMessage(f'Error: {str(e)}')
            QMessageBox.warning(self, "Error", f"FEN inválido: {str(e)}")

    def new_game(self):
        """Inicia una nueva partida"""
        self.board.set_position_from_fen(chess.STARTING_FEN)
        self.move_list.moves.clear()
        self.move_list.move_list.clear()
        self.engine_controls.opening_label.setText("Apertura: ")
        self.engine_controls.engine_info.clear()
        self.statusBar().showMessage('Nueva partida iniciada')

    def load_pgn(self):
        """Carga una partida desde archivo PGN"""
        # TODO: Implementar carga de PGN
        self.statusBar().showMessage('Función no implementada')

    def save_pgn(self):
        """Guarda la partida en formato PGN"""
        # TODO: Implementar guardado de PGN
        self.statusBar().showMessage('Función no implementada')

    def show_engine_settings(self):
        """Muestra la ventana de configuración del motor"""
        # TODO: Implementar ventana de configuración
        self.statusBar().showMessage('Función no implementada')

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Configurar estilo global
    app.setStyle('Fusion')
    
    # Crear y mostrar la ventana principal
    window = MainWindow()
    window.show()
    
    # Ejecutar la aplicación
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()