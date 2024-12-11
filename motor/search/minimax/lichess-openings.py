import requests
import chess.pgn
import io

class LichessOpenings:
    def __init__(self):
        self.base_url = "https://explorer.lichess.ovh/masters"
        self.opening_cache = {}
        
    def get_move(self, board: chess.Board):
        fen = board.fen()
        
        if fen in self.opening_cache:
            return self.opening_cache[fen]
            
        params = {'fen': fen}
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['moves']:
                # Obtener el movimiento más jugado
                best_move = chess.Move.from_uci(data['moves'][0]['uci'])
                self.opening_cache[fen] = best_move
                return best_move
                
        return None
