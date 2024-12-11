def analyze_position(self):
    """Analiza la posición actual y ejecuta el mejor movimiento encontrado"""
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
            # Obtener la notación SAN antes de hacer el movimiento
            move_san = current_board.san(best_move)
            
            # Reproducir sonido primero
            self.board.move_sound.play()
            
            # Dar tiempo para el sonido y completar el movimiento
            QTimer.singleShot(100, lambda: self._complete_engine_move(
                best_move, move_san, current_board, evaluation))
        else:
            self.engine_controls.btn_analyze.setEnabled(True)
            self.engine_controls.engine_info.setText("No se encontró un movimiento válido")
            
    except Exception as e:
        self.statusBar().showMessage(f'Error en el análisis: {str(e)}')
        self.engine_controls.engine_info.setText("Error durante el análisis")
        self.engine_controls.btn_analyze.setEnabled(True)

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