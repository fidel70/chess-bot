import re

def fix_sound_timing():
    # Leer el archivo original
    with open('run-gui.py', 'r', encoding='utf-8') as file:
        content = file.read()

    # Modificar el método handle_drop en ChessBoard
    new_handle_drop = '''    def handle_drop(self, from_square, to_square):
        move = chess.Move(from_square, to_square)
        if self.board.turn and self.board.is_legal(move):
            # Guardar el movimiento en notación SAN antes de ejecutarlo
            move_san = self.board.san(move)
            
            # Reproducir sonido y esperar un momento
            self.move_sound.play()
            
            # Usar QTimer para dar tiempo al sonido
            QTimer.singleShot(100, lambda: self._complete_move(move, move_san))
        else:
            print("Movimiento ilegal o no es tu turno.")
            
    def _complete_move(self, move, move_san):
        self.board.push(move)
        self.move_history.append(move)
        self.placePieces()
        # Emitir señal con el movimiento en notación SAN
        self.move_made.emit(move_san)'''

    # Modificar el método analyze_position en MainWindow
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
                
                # Reproducir sonido primero
                self.board.move_sound.play()
                
                # Usar QTimer para dar tiempo al sonido
                QTimer.singleShot(100, lambda: self._complete_engine_move(
                    best_move, move_san, current_board, evaluation))
            else:
                self.engine_controls.btn_analyze.setEnabled(True)
                
        except Exception as e:
            self.statusBar().showMessage(f'Error en el análisis: {str(e)}')
            self.engine_controls.engine_info.setText("Error durante el análisis")
            self.engine_controls.btn_analyze.setEnabled(True)
            
    def _complete_engine_move(self, move, move_san, current_board, evaluation):
        # Actualizar el historial y emitir la señal
        current_board.push(move)
        self.board.move_history.append(move)
        self.board.placePieces()
        
        self.move_list.add_move(move_san)
        
        analysis_text = f"Mejor movimiento: {move_san}\\n" + f"Evaluación: {evaluation/100:.2f}"
        self.engine_controls.engine_info.setText(analysis_text)
        self.statusBar().showMessage('Análisis completado')
        
        self.engine_controls.btn_analyze.setEnabled(True)'''

    # Reemplazar en el contenido usando expresiones regulares
    pattern_handle = re.compile(r'def handle_drop.*?print\("Movimiento ilegal o no es tu turno\."\)', re.DOTALL)
    content = pattern_handle.sub(new_handle_drop, content)
    
    pattern_analyze = re.compile(r'def analyze_position.*?self\.engine_controls\.btn_analyze\.setEnabled\(True\)', re.DOTALL)
    content = pattern_analyze.sub(new_analyze, content)

    # Guardar una copia de seguridad
    with open('run-gui.py.bak', 'w', encoding='utf-8') as file:
        file.write(content)

    # Guardar el archivo actualizado
    with open('run-gui.py', 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == '__main__':
    print("Corrigiendo la temporización del sonido en run-gui.py...")
    try:
        fix_sound_timing()
        print("¡Corrección completada!")
        print("Se ha creado una copia de seguridad en 'run-gui.py.bak'")
    except Exception as e:
        print(f"Error durante la corrección: {str(e)}")
