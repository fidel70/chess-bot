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
