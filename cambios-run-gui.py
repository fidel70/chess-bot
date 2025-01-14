class LichessOpenings:
    def __init__(self):
        self.base_url = "https://explorer.lichess.ovh/masters"
        self.opening_cache = {}
        self.last_request_time = 0
        
    def get_move(self, board: chess.Board) -> Tuple[Optional[chess.Move], Optional[str]]:
        try:
            fen = board.fen()
            if fen in self.opening_cache:
                return random.choice(self.opening_cache[fen]), self.opening_cache.get(f"{fen}_opening")
            
            params = {'fen': fen, 'topGames': 50, 'recentGames': 0}
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                # Obtener información de la apertura
                opening_info = None
                if 'opening' in data:
                    opening_info = f"{data['opening']['name']} ({data['opening']['eco']})"
                
                if 'moves' in data and data['moves']:
                    available_moves = []
                    for move_data in data['moves']:
                        if 'uci' in move_data:
                            try:
                                move = chess.Move.from_uci(move_data['uci'])
                                if move in board.legal_moves:
                                    available_moves.append(move)
                            except ValueError:
                                continue
                    
                    if available_moves:
                        self.opening_cache[fen] = available_moves
                        if opening_info:
                            self.opening_cache[f"{fen}_opening"] = opening_info
                        chosen_move = random.choice(available_moves)
                        return chosen_move, opening_info
                        
        except Exception as e:
            print(f"Error al consultar la base de datos: {str(e)}")
        return None, None

class EngineControls(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
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
        
        # Controles de profundidad
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(1, 20)
        self.depth_spin.setValue(3)
        layout.addWidget(QLabel("Profundidad:"))
        layout.addWidget(self.depth_spin)
        
        # Botón de análisis
        self.btn_analyze = QPushButton("Analizar")
        layout.addWidget(self.btn_analyze)
        
        # Panel de información del motor
        self.engine_info = QTextEdit()
        self.engine_info.setReadOnly(True)
        layout.addWidget(self.engine_info)

class ChessEngine:
    def __init__(self, evaluator, depth=3):
        self.minimax_engine = MinimaxEngine(evaluator, depth)
        self.lichess_db = LichessOpenings()
        
    def search(self, board: chess.Board) -> Tuple[chess.Move, float, Optional[str]]:
        # Primero intentar obtener un movimiento del libro de aperturas
        book_move, opening_info = self.lichess_db.get_move(board)
        
        if book_move:
            print(f"Usando movimiento del libro")
            return book_move, 0.0, opening_info
            
        # Si no hay movimiento del libro, usar el motor
        move, evaluation = self.minimax_engine.search(board)
        return move, evaluation, None

class MainWindow(QMainWindow):
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
                # Obtener la notación SAN antes de hacer el movimiento
                move_san = current_board.san(best_move)
                
                # Reproducir sonido y ejecutar el movimiento
                self.move_sound.play()
                QTimer.singleShot(1500, lambda: self._complete_engine_move(
                    best_move, move_san, current_board, evaluation))
            else:
                self.engine_controls.btn_analyze.setEnabled(True)
                self.engine_controls.engine_info.setText("No se encontró un movimiento válido")
                
        except Exception as e:
            print(f"Error detallado: {str(e)}")
            self.statusBar().showMessage(f'Error en el análisis: {str(e)}')