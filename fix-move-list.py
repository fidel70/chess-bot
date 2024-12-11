import re

def fix_move_list():
    # Leer el archivo original
    with open('run-gui.py', 'r', encoding='utf-8') as file:
        content = file.read()

    # Nuevo método analyze_position corregido
    new_analyze_position = '''    def analyze_position(self):
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
                
                # Realizar el movimiento en el tablero interno
                current_board.push(best_move)
                self.board.move_history.append(best_move)
                
                # Actualizar la visualización
                self.board.placePieces()
                
                # Añadir el movimiento a la lista
                self.move_list.add_move(move_san)
                
                analysis_text = f"Mejor movimiento: {move_san}\\nEvaluación: {evaluation/100:.2f}"
                self.engine_controls.engine_info.setText(analysis_text)
                self.statusBar().showMessage('Análisis completado')
                
            self.engine_controls.btn_analyze.setEnabled(True)
                
        except Exception as e:
            self.statusBar().showMessage(f'Error en el análisis: {str(e)}')
            self.engine_controls.engine_info.setText("Error durante el análisis")
            self.engine_controls.btn_analyze.setEnabled(True)'''

    # Encontrar y reemplazar el método analyze_position
    pattern = re.compile(r'def analyze_position.*?self\.engine_controls\.btn_analyze\.setEnabled\(True\)  # Rehabilitar botón\n', re.DOTALL)
    content = pattern.sub(new_analyze_position + '\n', content)

    # Guardar una copia de seguridad
    with open('run-gui.py.bak', 'w', encoding='utf-8') as file:
        file.write(content)

    # Guardar el archivo actualizado
    with open('run-gui.py', 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == '__main__':
    print("Corrigiendo la lista de movimientos en run-gui.py...")
    try:
        fix_move_list()
        print("¡Corrección completada!")
        print("Se ha creado una copia de seguridad en 'run-gui.py.bak'")
    except Exception as e:
        print(f"Error durante la corrección: {str(e)}")
