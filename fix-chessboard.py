import re

def fix_chessboard():
    # Leer el archivo original
    with open('run-gui.py', 'r', encoding='utf-8') as file:
        content = file.read()

    # Definir la clase ChessBoard completa
    chessboard_complete = '''class ChessBoard(QWidget):
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
        
        # Inicializar sonido de movimiento
        sound_path = os.path.join('gui', 'resources', 'sounds', 'move.wav')
        self.move_sound = QSound(sound_path)

    def initUI(self):
        main_layout = QGridLayout()
        self.setLayout(main_layout)
        
        # Grid del tablero
        board_grid = QGridLayout()
        colors = ['#F0D9B5', '#B58863']
        
        # Añadir etiquetas de coordenadas (filas)
        for rank in range(8):
            rank_label = QLabel(str(8 - rank))
            rank_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            main_layout.addWidget(rank_label, rank + 1, 0)
            
        # Añadir etiquetas de coordenadas (columnas)
        for file in range(8):
            file_label = QLabel(chr(97 + file))
            file_label.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
            main_layout.addWidget(file_label, 9, file + 1)
            
        # Crear y añadir el tablero
        for rank in range(8):
            for file in range(8):
                color = colors[(rank + file) % 2]
                position = chess.square(file, 7-rank)
                square = ChessSquare(position, color)
                self.squares[position] = square
                board_grid.addWidget(square, rank, file)
        
        # Añadir el grid del tablero al layout principal
        main_layout.addLayout(board_grid, 1, 1, 8, 8)
        main_layout.setSpacing(5)
        board_grid.setSpacing(0)

    def handle_drop(self, from_square, to_square):
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
            print("Movimiento ilegal o no es tu turno.")

    def animate_move(self, from_square, to_square):
        if from_square not in self.pieces:
            return
                
        piece = self.pieces[from_square]
        move = chess.Move(from_square, to_square)
        
        if not self.board.is_legal(move):
            return
            
        # Guardar el movimiento en notación SAN antes de ejecutarlo
        try:
            move_san = self.board.san(move)
            self.board.push(move)
            self.move_history.append(move)
            
            # Obtener las posiciones inicial y final
            start_pos = self.squares[from_square].pos()
            end_pos = self.squares[to_square].pos()
            
            # Crear copia temporal de la pieza para la animación
            temp_piece = ChessPiece(piece.piece, self)
            temp_piece.setFixedSize(50, 50)
            temp_piece.move(start_pos)
            temp_piece.show()
            
            # Crear la animación
            self.current_animation = QPropertyAnimation(temp_piece, b"pos")
            self.current_animation.setDuration(500)
            self.current_animation.setStartValue(start_pos)
            self.current_animation.setEndValue(end_pos)
            self.current_animation.setEasingCurve(QEasingCurve.InOutQuad)
            
            # Conectar la señal finished
            self.current_animation.finished.connect(
                lambda: self.finish_move(from_square, to_square, temp_piece)
            )
            
            # Iniciar la animación
            self.current_animation.start()
            
            # Emitir señal con el movimiento en notación SAN
            self.move_made.emit(move_san)
            
        except ValueError as e:
            print(f"Error al realizar el movimiento: {e}")

    def finish_move(self, from_square, to_square, temp_piece):
        temp_piece.deleteLater()
        self.placePieces()

    def placePieces(self):
        for square in chess.SQUARES:
            if self.squares[square].layout():
                old_layout = self.squares[square].layout()
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                QWidget().setLayout(old_layout)

        self.pieces.clear()

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                chess_piece = ChessPiece(piece.symbol())
                layout = QVBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(chess_piece)
                self.squares[square].setLayout(layout)
                self.pieces[square] = chess_piece

    def goto_position(self, move_number):
        self.board = chess.Board()
        
        if move_number >= -1:
            for i in range(move_number + 1):
                if i < len(self.move_history):
                    try:
                        self.board.push(self.move_history[i])
                    except AssertionError:
                        print(f"Error al reproducir movimiento {i}")
                        break
                        
        self.placePieces()

    def set_position_from_fen(self, fen: str):
        try:
            self.board = chess.Board(fen)
            
            for square in chess.SQUARES:
                if self.squares[square].layout():
                    old_layout = self.squares[square].layout()
                    while old_layout.count():
                        item = old_layout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                    QWidget().setLayout(old_layout)
            
            self.pieces.clear()
            
            for square in chess.SQUARES:
                piece = self.board.piece_at(square)
                if piece:
                    chess_piece = ChessPiece(piece.symbol())
                    layout = QVBoxLayout()
                    layout.addWidget(chess_piece)
                    self.squares[square].setLayout(layout)
                    self.pieces[square] = chess_piece
                    
        except ValueError as e:
            raise ValueError(f"FEN inválido: {str(e)}")'''

    # Encontrar y reemplazar la clase ChessBoard
    start = content.find('class ChessBoard')
    end = content.find('class MoveList')
    
    # Reemplazar la clase ChessBoard manteniendo el resto del contenido
    new_content = content[:start] + chessboard_complete + '\n\n' + content[end:]

    # Guardar una copia de seguridad
    with open('run-gui.py.bak', 'w', encoding='utf-8') as file:
        file.write(content)

    # Guardar el archivo actualizado
    with open('run-gui.py', 'w', encoding='utf-8') as file:
        file.write(new_content)

if __name__ == '__main__':
    print("Completando la clase ChessBoard en run-gui.py...")
    try:
        fix_chessboard()
        print("¡Corrección completada!")
        print("Se ha creado una copia de seguridad en 'run-gui.py.bak'")
    except Exception as e:
        print(f"Error durante la corrección: {str(e)}")
