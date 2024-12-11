import re

def fix_chess_navigation():
    # Leer el archivo original
    with open('run-gui.py', 'r', encoding='utf-8') as file:
        content = file.read()

    # Corregir el método finish_move
    new_finish_move = '''    def finish_move(self, from_square, to_square, temp_piece):
        """Completa el movimiento después de la animación"""
        # Eliminar la pieza temporal
        temp_piece.deleteLater()
        
        # Actualizar la visualización del tablero
        self.placePieces()'''

    # Corregir el método goto_position
    new_goto_position = '''    def goto_position(self, move_number):
        """Va a una posición específica en el historial"""
        # Crear un nuevo tablero desde la posición inicial
        self.board = chess.Board()
        
        # Aplicar movimientos hasta la posición deseada
        if move_number >= -1:  # -1 es la posición inicial
            for i in range(move_number + 1):
                if i < len(self.move_history):
                    try:
                        self.board.push(self.move_history[i])
                    except AssertionError:
                        print(f"Error al reproducir movimiento {i}")
                        break
                        
        # Actualizar visualización
        self.placePieces()'''

    # Corregir el método animate_move
    new_animate_move = '''    def animate_move(self, from_square, to_square):
        """Anima el movimiento de una pieza de una casilla a otra"""
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
            print(f"Error al realizar el movimiento: {e}")'''

    # Reemplazar los métodos en el contenido
    content = re.sub(
        r'def finish_move.*?self\.placePieces\(\)\n',
        new_finish_move + '\n\n',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'def goto_position.*?self\.placePieces\(\)\n',
        new_goto_position + '\n\n',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'def animate_move.*?print\("Movimiento ilegal o no es tu turno\."\)\n',
        new_animate_move + '\n\n',
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
    print("Corrigiendo la navegación en run-gui.py...")
    try:
        fix_chess_navigation()
        print("¡Corrección completada!")
        print("Se ha creado una copia de seguridad en 'run-gui.py.bak'")
    except Exception as e:
        print(f"Error durante la corrección: {str(e)}")
