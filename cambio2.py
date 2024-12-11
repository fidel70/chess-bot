class ChessEngine:
    """Motor de ajedrez principal que combina minimax con base de datos de aperturas"""
    def __init__(self, evaluator, depth=3):
        self.minimax_engine = MinimaxEngine(evaluator, depth)
        self.lichess_db = LichessOpenings()
        
    def search(self, board: chess.Board) -> Tuple[chess.Move, float, Optional[str]]:
        """Busca el mejor movimiento usando libro de aperturas o motor"""
        # Intentar obtener movimiento del libro
        book_move, opening_info = self.lichess_db.get_move(board)
        
        if book_move is not None:
            print("[INFO] Usando movimiento del libro de aperturas")
            return book_move, 0.0, opening_info
            
        # Si no hay movimiento en el libro, usar el motor
        print("[INFO] Libro de aperturas agotado, usando motor minimax")
        move, evaluation = self.minimax_engine.search(board)
        return move, evaluation, None
