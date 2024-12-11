import chess
from typing import Optional, Tuple, List
import time
from dataclasses import dataclass

def minimax(board, depth, maximizing_player):
    """
    Minimax algorithm for chess.

    :param board: chess.Board object representing the current state of the board.
    :param depth: How deep to search the game tree.
    :param maximizing_player: True if the current player is maximizing, False otherwise.
    :return: The best score for the player and the best move to achieve it.
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None

    if maximizing_player:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, False)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
        return max_eval, best_move

    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, True)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
        return min_eval, best_move

def evaluate_board(board):
    """
    Simple board evaluation function.

    :param board: chess.Board object representing the current state of the board.
    :return: Evaluation score (positive for white advantage, negative for black advantage).
    """
    # Piece values
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value

    return score

# Example usage
if __name__ == "__main__":
    board = chess.Board()
    print("Initial board:")
    print(board)

    while not board.is_game_over():
        if board.turn == chess.WHITE:
            print("White's turn")
            _, move = minimax(board, 3, True)
        else:
            print("Black's turn")
            _, move = minimax(board, 3, False)

        print(f"Move chosen: {move}")
        board.push(move)
        print(board)

    print("Game over!")
    print("Result: ", board.result())
