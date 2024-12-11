
import os
import re
import shutil
from datetime import datetime

def create_directory_structure():
    """Crea la estructura de directorios necesaria."""
    dirs = [
        'gui/resources/pieces',
        'gui/resources/sounds'
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Directorio creado/verificado: {d}")

def backup_file(file_path):
    """Crea una copia de respaldo del archivo original."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{file_path}.{timestamp}.bak"
        shutil.copy2(file_path, backup_path)
        print(f"Backup creado: {backup_path}")
        return True
    except Exception as e:
        print(f"Error creando backup: {str(e)}")
        return False

def validate_source_file(content):
    """Valida que el archivo fuente contenga las secciones necesarias."""
    required_patterns = [
        r"# \[Las clases ChessPiece, ChessSquare y ChessBoard se mantienen igual\]",
        r"# \[La clase MoveList se mantiene igual\]",
        r"# \[Resto de los métodos de MainWindow se mantienen igual"
    ]
    
    for pattern in required_patterns:
        if not re.search(pattern, content):
            return False
    return True

def fix_chess_gui(file_path):
    """Corrige y actualiza el código del GUI."""
    print("\nIniciando proceso de corrección...")
    
    # Verificar estructura de directorios
    create_directory_structure()
    
    # Leer archivo original
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise Exception(f"Error leyendo archivo: {str(e)}")
    
    # Validar contenido
    if not validate_source_file(content):
        raise Exception("El archivo no contiene las secciones necesarias para la actualización")
    
    # Crear backup
    if not backup_file(file_path):
        raise Exception("No se pudo crear el backup")
    
    # Definir las clases y métodos a insertar
    chess_classes = """
class ChessPiece(QSvgWidget):
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
    move_made = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        self.squares = {}
        self.pieces = {}
        self.move_history = []
        self.initUI()
        self.placePieces()
        self.current_animation = None
        sound_path = os.path.join(project_root, 'gui', 'resources', 'sounds', 'move.mp3')
        self.move_sound = pygame.mixer.Sound(sound_path)
        
        print(f"Ruta del archivo de sonido: {os.path.abspath(sound_path)}")
        if os.path.exists(sound_path):
            print("El archivo existe!")
            print(f"Tamaño del archivo: {os.path.getsize(sound_path)} bytes")
        else:
            print("El archivo NO existe en la ruta especificada")

    def initUI(self):
        main_layout = QGridLayout()
        self.setLayout(main_layout)
        board_grid = QGridLayout()
        colors = ['#F0D9B5', '#B58863']
        
        for rank in range(8):
            rank_label = QLabel(str(8 - rank))
            rank_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            main_layout.addWidget(rank_label, rank + 1, 0)
        
        for file in range(8):
            file_label = QLabel(chr(97 + file))
            file_label.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
            main_layout.addWidget(file_label, 9, file + 1)
        
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
        move = chess.Move(from_square, to_square)
        if self.board.turn and self.board.is_legal(move):
            move_san = self.board.san(move)
            self.move_sound.play()
            QTimer.singleShot(1500, lambda: self._complete_move(move, move_san))
        else:
            print("Movimiento ilegal o no es tu turno.")

    def _complete_move(self, move, move_san):
        self.board.push(move)
        self.move_history.append(move)
        self.placePieces()
        self.move_made.emit(move_san)
"""

    movelist_class = """
class MoveList(QWidget):
    move_selected = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_move = -1
        self.moves = []
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.move_list = QListWidget()
        self.move_list.itemClicked.connect(self.on_move_clicked)
        layout.addWidget(self.move_list)
        
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
        move_number = len(self.moves) // 2 + 1
        if len(self.moves) % 2 == 0:
            self.moves.append(move_san)
            text = f"{move_number}. {move_san}"
        else:
            self.moves.append(move_san)
            text = f"{move_number}... {move_san}"
        
        self.move_list.addItem(text)
        self.current_move = len(self.moves) - 1
        self.move_list.setCurrentRow(self.current_move)
        self.update_navigation_buttons()
"""

    mainwindow_methods = """
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
        
        self.engine_controls.btn_set_position.clicked.connect(self.set_position)
        self.engine_controls.btn_analyze.clicked.connect(self.analyze_position)
        
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_panel, 1)
        
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

    def _complete_engine_move(self, move, move_san, current_board, evaluation):
        try:
            current_board.push(move)
            self.board.move_history.append(move)
            self.board.placePieces()
            
            self.move_list.add_move(move_san)
            
            analysis_text = f"Mejor movimiento: {move_san} - Evaluación: {evaluation/100:.2f}"
            self.engine_controls.engine_info.setText(analysis_text)
            self.statusBar().showMessage('Análisis completado')
            
        except Exception as e:
            self.statusBar().showMessage(f'Error al completar el movimiento: {str(e)}')
            self.engine_controls.engine_info.setText("Error al ejecutar el movimiento")
        finally:
            self.engine_controls.btn_analyze.setEnabled(True)
"""

    try:
        # Reemplazar los comentarios con el código real
        content = content.replace("# [Las clases ChessPiece, ChessSquare y ChessBoard se mantienen igual]", chess_classes)
        content = content.replace("# [La clase MoveList se mantiene igual]", movelist_class)
        content = content.replace("# [Resto de los métodos de MainWindow se mantienen igual pero con el método analyze_position actualizado]", mainwindow_methods)
        content = content.replace("# [El resto de los métodos se mantienen igual]", "")

        # Guardar el archivo actualizado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\nGUI actualizado exitosamente!")
        return True
    except Exception as e:
        print(f"Error durante la actualización del archivo: {str(e)}")
        return False

def main():
    print("Script de corrección del GUI de Ajedrez")
    print("======================================")
    
    # Verificar archivo
    gui_path = input("\nIntroduce el nombre del archivo GUI (presiona Enter para usar chess_gui.py): ").strip()
    if not gui_path:
        gui_path = "chess_gui.py"
    
    if not os.path.exists(gui_path):
        print(f"\nNo se encontró el archivo {gui_path}")
        crear = input("¿Deseas crear un nuevo archivo? (s/n): ").lower().strip()
        if crear != 's':
            print("Operación cancelada.")
            return
        
        try:
            with open(gui_path, 'w', encoding='utf-8') as f:
                f.write("""# Archivo generado automáticamente
# Versión inicial del GUI de ajedrez""")
        except Exception as e:
            print(f"Error creando archivo: {str(e)}")
            return
    
    try:
        if fix_chess_gui(gui_path):
            print("\nProceso completado exitosamente!")
            print(f"El archivo {gui_path} ha sido actualizado.")
            print("\nVerifica que tengas:")
            print("1. La carpeta 'gui/resources/pieces' con las imágenes SVG de las piezas")
            print("2. La carpeta 'gui/resources/sounds' con el archivo move.mp3")
            print("3. Todas las dependencias instaladas (PyQt5, python-chess, etc.)")
    except Exception as e:
        print(f"\nError durante la actualización: {str(e)}")
        print("Se mantuvo una copia de respaldo del archivo original.")

if __name__ == "__main__":
    main()