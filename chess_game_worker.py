#!/usr/bin/env python3
"""
Chess AI Worker - Runs a single game with the improved algorithm.
"""

import copy
import sys
import os
import json
import argparse

PYTHON_CHESS_PATH = os.environ.get('PYTHON_CHESS_PATH',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Python-Chess'))
sys.path.insert(0, PYTHON_CHESS_PATH)

from chess_ai import ChessGame, ChessAI


def run_game(game_id, depth=2, max_moves=100):
    """Run a single game and return results."""
    game = ChessGame()
    white_ai = ChessAI(depth=depth)
    black_ai = ChessAI(depth=depth)

    move_count = 0
    moves_log = []
    result = "ongoing"
    winner = None
    captures = {"white": 0, "black": 0}

    while move_count < max_moves:
        if game.is_checkmate():
            winner = "black" if game.white_to_move else "white"
            result = "checkmate"
            break
        if game.is_stalemate():
            result = "stalemate"
            break
        if game.is_insufficient_material():
            result = "insufficient_material"
            break

        current_ai = white_ai if game.white_to_move else black_ai
        best_move, nodes = current_ai.get_best_move(game)

        if best_move is None:
            result = "no_moves"
            break

        move_notation = game.move_to_algebraic(best_move)
        piece = game.board[best_move[0]][best_move[1]]
        captured = game.board[best_move[2]][best_move[3]]

        if captured != '.':
            if game.white_to_move:
                captures["white"] += 1
            else:
                captures["black"] += 1

        moves_log.append({
            "move": move_count + 1,
            "player": "white" if game.white_to_move else "black",
            "notation": move_notation,
            "piece": piece,
            "capture": captured != '.',
            "nodes": nodes
        })

        game.make_move(best_move)
        move_count += 1

        # Progress output
        if move_count % 20 == 0:
            print(f"Game {game_id}: Move {move_count}", file=sys.stderr)

    if move_count >= max_moves and result == "ongoing":
        result = "move_limit"

    # Count remaining pieces
    white_pieces = []
    black_pieces = []
    for row in range(8):
        for col in range(8):
            piece = game.board[row][col]
            if piece != '.':
                if piece.isupper():
                    white_pieces.append(piece)
                else:
                    black_pieces.append(piece.upper())

    return {
        "game_id": game_id,
        "depth": depth,
        "total_moves": move_count,
        "result": result,
        "winner": winner,
        "white_captures": captures["white"],
        "black_captures": captures["black"],
        "white_pieces_remaining": len(white_pieces),
        "black_pieces_remaining": len(black_pieces),
        "white_pieces": white_pieces,
        "black_pieces": black_pieces,
        "last_moves": moves_log[-10:] if len(moves_log) >= 10 else moves_log
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-id", type=int, required=True)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--max-moves", type=int, default=100)
    args = parser.parse_args()

    result = run_game(args.game_id, args.depth, args.max_moves)
    print(json.dumps(result))
