import re

def fix_move_duplication():
    # Leer el archivo original
    with open('run-gui.py', 'r', encoding='utf-8') as file:
        content = file.read()

    # 1. Eliminar la duplicación de las conexiones de señales en MainWindow
    new_connections = '''        # Conectar señales
        self.engine_controls.btn_set_position.clicked.connect(self.set_position)
        self.engine_controls.btn_analyze.clicked.connect(self.analyze_position)
        
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_panel, 1)
        
        # Conectar señales del tablero y la lista de movimientos
        self.board.move_made.connect(self.move_list.add_move)
        self.move_list.move_selected.connect(self.board.goto_position)'''

    # Reemplazar la sección duplicada
    content = re.sub(
        r'# Conectar señales.*?self\.move_list\.move_selected\.connect\(self\.board\.goto_position\)\n\s+# Conectar señales del tablero.*?self\.board\.goto_position\)',
        new_connections,
        content,
        flags=re.DOTALL
    )

    # 2. Corregir el método analyze_position para evitar emisión duplicada
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
                
                # Actualizar el historial y emitir la señal
                current_board.push(best_move)
                self.board.move_history.append(best_move)
                self.board.placePieces()
                self.move_list.add_move(move_san)
                
                analysis_text = f"Mejor movimiento: {move_san}\\nEvaluación: {evaluation/100:.2f}"
                self.engine_controls.engine_info.setText(analysis_text)
                self.statusBar().showMessage('Análisis completado')
                
            self.engine_controls.btn_analyze.setEnabled(True)
                
        except Exception as e:
            self.statusBar().showMessage(f'Error en el análisis: {str(e)}')
            self.engine_controls.engine_info.setText("Error durante el análisis")
            self.engine_controls.btn_analyze.setEnabled(True)'''

    # Reemplazar el método analyze_position
    content = re.sub(
        r'def analyze_position\(self\):.*?self\.engine_controls\.btn_analyze\.setEnabled\(True\)',
        new_analyze_position,
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
    print("Corrigiendo duplicación de movimientos en run-gui.py...")
    try:
        fix_move_duplication()
        print("¡Corrección completada!")
        print("Se ha creado una copia de seguridad en 'run-gui.py.bak'")
    except Exception as e:
        print(f"Error durante la corrección: {str(e)}")
