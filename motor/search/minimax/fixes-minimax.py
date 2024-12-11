def search(self, board: chess.Board, time_limit: Optional[float] = None) -> Tuple[chess.Move, float]:
    self.search_info = SearchInfo()
    start_time = time.time()
    
    best_move = None
    best_value = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
    
    for current_depth in range(1, self.max_depth + 1):
        self.search_info.depth_reached = current_depth
        
        # Ventana de aspiración
        if current_depth >= 2:
            alpha = max(best_value - 50, float('-inf'))
            beta = min(best_value + 50, float('inf'))
        
        value = float('-inf')
        current_alpha = alpha
        
        hash_key = self.zobrist.compute_hash(board)
        tt_entry = self.tt.lookup(hash_key)
        tt_move = tt_entry[3] if tt_entry else None
        
        moves = self._order_moves(board, current_depth, tt_move)
        
        for move in moves:
            board.push(move)
            # Negamax: siempre buscamos el máximo del negativo
            value = -self._minimax(board, current_depth - 1, -beta, -current_alpha, True)
            board.pop()
            
            if value > current_alpha:
                current_alpha = value
                if value > best_value:
                    best_value = value
                    best_move = move
                    self.tt.store(hash_key, value, current_depth, TranspositionTable.EXACT, move)
            
            if current_alpha >= beta:
                break
            
            if time_limit and (time.time() - start_time) > time_limit:
                break
                
        if time_limit and (time.time() - start_time) > time_limit:
            break
                
    self.search_info.time_spent = time.time() - start_time
    return best_move, best_value if board.turn else -best_value

def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
    # Verificar finales
    if board.is_game_over():
        if board.is_checkmate():
            return -self.MATE_SCORE  # En negamax, siempre retornamos el negativo
        return self.DRAW_SCORE
    
    # El resto del código se mantiene igual hasta el final, donde cambiamos:
    return best_value

def _quiescence_search(self, board: chess.Board, alpha: float, beta: float) -> float:
    self.search_info.positions_evaluated += 1
    
    # En negamax, no multiplicamos por turno
    stand_pat = self.evaluator.evaluate(board)
    
    # El resto del código se mantiene igual