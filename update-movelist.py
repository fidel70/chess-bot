import re

def update_run_gui():
    # Leer el archivo original
    with open('run-gui.py', 'r', encoding='utf-8') as file:
        content = file.read()

    # Actualizar la clase MoveList
    new_movelist = '''class MoveList(QWidget):
    move_selected = pyqtSignal(int)  # Nueva señal para cuando se selecciona un movimiento
    
    def __init__(self):
        super().__init__()
        self.current_move = -1
        self.moves = []  # Lista para almacenar los movimientos
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Lista de movimientos
        self.move_list = QListWidget()
        self.move_list.itemClicked.connect(self.on_move_clicked)
        layout.addWidget(self.move_list)
        
        # Botones de navegación
        nav_layout = QHBoxLayout()
        self.btn_first = QPushButton("<<")
        self.btn_prev = QPushButton("<")
        self.btn_next = QPushButton(">")
        self.btn_last = QPushButton(">>")
        
        # Conectar botones
        self.btn_first.clicked.connect(self.goto_first)
        self.btn_prev.clicked.connect(self.goto_prev)
        self.btn_next.clicked.connect(self.goto_next)
        self.btn_last.clicked.connect(self.goto_last)
        
        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last]:
            nav_layout.addWidget(btn)
            
        layout.addLayout(nav_layout)
        self.update_navigation_buttons()

    def add_move(self, move_san):
        """Añade un nuevo movimiento a la lista"""
        move_number = len(self.moves) // 2 + 1
        if len(self.moves) % 2 == 0:
            # Movimiento blanco
            self.moves.append(move_san)
            text = f"{move_number}. {move_san}"
        else:
            # Movimiento negro
            self.moves.append(move_san)
            text = f"{move_number}... {move_san}"
        
        self.move_list.addItem(text)
        self.current_move = len(self.moves) - 1
        self.move_list.setCurrentRow(self.current_move)
        self.update_navigation_buttons()
        
    def goto_first(self):
        """Ir al primer movimiento"""
        if self.moves:
            self.current_move = -1
            self.move_list.setCurrentRow(-1)
            self.move_selected.emit(self.current_move)
            self.update_navigation_buttons()
    
    def goto_prev(self):
        """Ir al movimiento anterior"""
        if self.current_move > -1:
            self.current_move -= 1
            self.move_list.setCurrentRow(self.current_move)
            self.move_selected.emit(self.current_move)
            self.update_navigation_buttons()
    
    def goto_next(self):
        """Ir al siguiente movimiento"""
        if self.current_move < len(self.moves) - 1:
            self.current_move += 1
            self.move_list.setCurrentRow(self.current_move)
            self.move_selected.emit(self.current_move)
            self.update_navigation_buttons()
    
    def goto_last(self):
        """Ir al último movimiento"""
        if self.moves:
            self.current_move = len(self.moves) - 1
            self.move_list.setCurrentRow(self.current_move)
            self.move_selected.emit(self.current_move)
            self.update_navigation_buttons()
    
    def on_move_clicked(self, item):
        """Manejador para cuando se hace clic en un movimiento"""
        self.current_move = self.move_list.row(item)
        self.move_selected.emit(self.current_move)
        self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        """Actualiza el estado de los botones de navegación"""
        self.btn_first.setEnabled(self.current_move > -1)
        self.btn_prev.setEnabled(self.current_move > -1)
        self.btn_next.setEnabled(self.current_move < len(self.moves) - 1)
        self.btn_last.setEnabled(self.current_move < len(self.moves) - 1)
    
    def clear(self):
        """Limpia la lista de movimientos"""
        self.moves.clear()
        self.move_list.clear()
        self.current_move = -1
        self.update_navigation_buttons()'''

    # Actualizar la clase ChessBoard
    chessboard_additions = '''    move_made = pyqtSignal(str)  # Nueva señal para movimientos realizados

    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        self.squares = {}
        self.pieces = {}
        self.move_history = []  # Lista para almacenar el historial de movimientos
        self.initUI()
        self.placePieces()
        self.current_animation = None'''

    # Actualizar el método handle_drop
    new_handle_drop = '''    def handle_drop(self, from_square, to_square):
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

    # Añadir método goto_position
    goto_position = '''    def goto_position(self, move_number):
        """Va a una posición específica en el historial"""
        # Crear un nuevo tablero desde la posición inicial
        self.board = chess.Board()
        # Aplicar movimientos hasta la posición deseada
        for i in range(move_number + 1):
            if i < len(self.move_history):
                self.board.push(self.move_history[i])
        self.placePieces()'''

    # Actualizar la clase MainWindow
    mainwindow_additions = '''        # Conectar señales del tablero y la lista de movimientos
        self.board.move_made.connect(self.move_list.add_move)
        self.move_list.move_selected.connect(self.board.goto_position)'''

    # Realizar las sustituciones
    # 1. Reemplazar la clase MoveList
    content = re.sub(
        r'class MoveList\(QWidget\):.*?(?=class|$)',
        new_movelist,
        content,
        flags=re.DOTALL
    )

    # 2. Actualizar la inicialización de ChessBoard
    content = re.sub(
        r'def __init__\(self\):\s+super\(\)\.__init__\(\)\s+self\.board = chess\.Board\(\)\s+self\.squares = \{\}\s+self\.pieces = \{\}\s+self\.initUI\(\)\s+self\.placePieces\(\)\s+self\.current_animation = None',
        chessboard_additions,
        content
    )

    # 3. Actualizar handle_drop
    content = re.sub(
        r'def handle_drop.*?print\("Movimiento ilegal o no es tu turno\."\)',
        new_handle_drop,
        content,
        flags=re.DOTALL
    )

    # 4. Añadir goto_position antes del último método de ChessBoard
    content = content.replace(
        'def set_position_from_fen',
        goto_position + '\n\n    def set_position_from_fen'
    )

    # 5. Añadir las conexiones de señales en MainWindow
    content = content.replace(
        'main_layout.addLayout(right_panel, 1)',
        'main_layout.addLayout(right_panel, 1)\n        ' + mainwindow_additions
    )

    # Guardar una copia de seguridad del archivo original
    with open('run-gui.py.bak', 'w', encoding='utf-8') as file:
        file.write(content)

    # Escribir el archivo actualizado
    with open('run-gui.py', 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == '__main__':
    print("Actualizando run-gui.py...")
    try:
        update_run_gui()
        print("¡Actualización completada!")
        print("Se ha creado una copia de seguridad en 'run-gui.py.bak'")
    except Exception as e:
        print(f"Error durante la actualización: {str(e)}")
