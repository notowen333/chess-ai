#!/usr/bin/env python3
"""
Chess AI Runner - Runs 500 moves between two AIs with algorithm updates every 100 moves.
"""

import copy
import sys
import os

# Use environment variable or default to relative path from script location
PYTHON_CHESS_PATH = os.environ.get('PYTHON_CHESS_PATH',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Python-Chess'))
sys.path.insert(0, PYTHON_CHESS_PATH)

from chess_ai import ChessGame, ChessAI, PIECE_VALUES, PIECE_TABLES, piece_to_symbol

# Algorithm variation configurations
ALGORITHM_CONFIGS = [
    {
        "name": "Baseline (depth=3)",
        "depth": 3,
        "center_bonus": 100,
        "repetition_penalty": 50,
    },
    {
        "name": "Deeper Search (depth=4)",
        "depth": 4,
        "center_bonus": 100,
        "repetition_penalty": 50,
    },
    {
        "name": "Aggressive Center Control (depth=3)",
        "depth": 3,
        "center_bonus": 200,
        "repetition_penalty": 75,
    },
    {
        "name": "Anti-Repetition (depth=3)",
        "depth": 3,
        "center_bonus": 100,
        "repetition_penalty": 150,
    },
    {
        "name": "Deep + Aggressive (depth=4)",
        "depth": 4,
        "center_bonus": 150,
        "repetition_penalty": 100,
    },
]


class ConfigurableChessAI(ChessAI):
    """Chess AI with configurable parameters."""

    def __init__(self, depth=3, center_bonus=100, repetition_penalty=50):
        super().__init__(depth)
        self.center_bonus = center_bonus
        self.repetition_penalty = repetition_penalty

    def evaluate(self, game):
        """Evaluate the board position with configurable heuristics."""
        if game.is_checkmate():
            return -20000 if game.white_to_move else 20000
        if game.is_stalemate() or game.is_insufficient_material():
            return 0

        score = 0

        # Material and position evaluation
        for row in range(8):
            for col in range(8):
                piece = game.board[row][col]
                if piece == '.':
                    continue

                # Material value
                score += PIECE_VALUES.get(piece, 0)

                # Position value
                piece_type = piece.upper()
                if piece_type in PIECE_TABLES:
                    table = PIECE_TABLES[piece_type]
                    if piece.isupper():
                        score += table[7 - row][col]
                    else:
                        score -= table[row][col]

        # Penalize repetition with configurable penalty
        board_hash = self.get_board_hash(game)
        if board_hash in self.position_history:
            repetition_count = self.position_history[board_hash]
            penalty = repetition_count * self.repetition_penalty
            score -= penalty if game.white_to_move else -penalty

        return score

    def minimax(self, game, depth, alpha, beta, maximizing, ply=0):
        """Minimax with configurable center bonus."""
        self.nodes_searched += 1

        in_check = game.is_in_check()
        if in_check and depth == 0:
            depth = 1

        board_hash = self.get_board_hash(game)
        if board_hash in self.transposition_table:
            cached_depth, cached_score, cached_move = self.transposition_table[board_hash]
            if cached_depth >= depth:
                return cached_score, cached_move

        if depth == 0 or game.is_checkmate() or game.is_stalemate():
            return self.evaluate(game), None

        moves = game.get_all_moves()
        if not moves:
            return self.evaluate(game), None

        # Enhanced move ordering with configurable center bonus
        def move_score(move):
            score = 0
            from_row, from_col, to_row, to_col = move
            captured = game.board[to_row][to_col]
            moving_piece = game.board[from_row][from_col]

            if captured != '.':
                victim_value = abs(PIECE_VALUES.get(captured, 0))
                attacker_value = abs(PIECE_VALUES.get(moving_piece, 0))
                score += 10000 + victim_value * 10 - attacker_value

            if ply < len(self.killer_moves) and move in self.killer_moves[ply]:
                score += 5000

            # Configurable center control bonus
            if captured == '.' and 2 <= to_row <= 5 and 2 <= to_col <= 5:
                score += self.center_bonus

            return score

        moves.sort(key=move_score, reverse=True)
        best_move = moves[0]

        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move)
                eval_score, _ = self.minimax(game_copy, depth - 1, alpha, beta, False, ply + 1)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    if ply < len(self.killer_moves):
                        if move not in self.killer_moves[ply]:
                            self.killer_moves[ply].insert(0, move)
                            if len(self.killer_moves[ply]) > 2:
                                self.killer_moves[ply].pop()
                    break

            self.transposition_table[board_hash] = (depth, max_eval, best_move)
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move)
                eval_score, _ = self.minimax(game_copy, depth - 1, alpha, beta, True, ply + 1)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    if ply < len(self.killer_moves):
                        if move not in self.killer_moves[ply]:
                            self.killer_moves[ply].insert(0, move)
                            if len(self.killer_moves[ply]) > 2:
                                self.killer_moves[ply].pop()
                    break

            self.transposition_table[board_hash] = (depth, min_eval, best_move)
            return min_eval, best_move


def run_game_segment(game, white_ai, black_ai, start_move, end_move, config_name):
    """Run a segment of the game (e.g., 100 moves)."""
    print(f"\n{'='*60}")
    print(f"Running moves {start_move+1} to {end_move} with: {config_name}")
    print(f"{'='*60}\n")

    move_count = start_move
    captures = {"white": 0, "black": 0}

    while move_count < end_move:
        # Check for game over
        if game.is_checkmate():
            winner = "Black" if game.white_to_move else "White"
            print(f"\n*** CHECKMATE! {winner} wins after {move_count} moves! ***")
            return move_count, "checkmate", winner

        if game.is_stalemate():
            print(f"\n*** STALEMATE after {move_count} moves! ***")
            return move_count, "stalemate", None

        if game.is_insufficient_material():
            print(f"\n*** DRAW by insufficient material after {move_count} moves! ***")
            return move_count, "insufficient", None

        current_player = "White" if game.white_to_move else "Black"
        current_ai = white_ai if game.white_to_move else black_ai

        # Get AI move
        best_move, nodes = current_ai.get_best_move(game)

        if best_move is None:
            print(f"No legal moves for {current_player}!")
            return move_count, "no_moves", None

        # Record the move
        move_notation = game.move_to_algebraic(best_move)
        piece = game.board[best_move[0]][best_move[1]]
        captured = game.board[best_move[2]][best_move[3]]

        # Track captures
        if captured != '.':
            if game.white_to_move:
                captures["white"] += 1
            else:
                captures["black"] += 1

        # Make the move
        game.make_move(best_move)
        move_count += 1

        # Print progress every 10 moves
        if move_count % 10 == 0:
            check_status = " (CHECK)" if game.is_in_check() else ""
            print(f"Move {move_count}: {current_player} {piece} {move_notation}{check_status} | Nodes: {nodes}")

    print(f"\nSegment complete. White captures: {captures['white']}, Black captures: {captures['black']}")
    return move_count, "continue", None


def main():
    print("=" * 60)
    print("       CHESS AI vs AI - 500 Move Test")
    print("       Algorithm updates every 100 moves")
    print("=" * 60)

    # Initialize game
    game = ChessGame()
    total_moves = 0

    # Statistics
    stats = {
        "total_captures_white": 0,
        "total_captures_black": 0,
        "segments": []
    }

    # Run 5 segments of 100 moves each
    for segment in range(5):
        config = ALGORITHM_CONFIGS[segment]

        # Create new AI instances with updated configuration
        white_ai = ConfigurableChessAI(
            depth=config["depth"],
            center_bonus=config["center_bonus"],
            repetition_penalty=config["repetition_penalty"]
        )
        black_ai = ConfigurableChessAI(
            depth=config["depth"],
            center_bonus=config["center_bonus"],
            repetition_penalty=config["repetition_penalty"]
        )

        # Preserve position history from previous segment
        if segment > 0:
            # Transfer learned position history
            white_ai.position_history = copy.deepcopy(game.move_history)
            black_ai.position_history = copy.deepcopy(game.move_history)

        start_move = segment * 100
        end_move = (segment + 1) * 100

        # Run the segment
        moves_played, result, winner = run_game_segment(
            game, white_ai, black_ai, start_move, end_move, config["name"]
        )

        total_moves = moves_played

        stats["segments"].append({
            "segment": segment + 1,
            "config": config["name"],
            "moves_played": moves_played - start_move,
            "result": result
        })

        # Check if game ended
        if result != "continue":
            break

        # Display board state after each segment
        print(f"\n--- Board state after {moves_played} moves ---")
        game.display()
        print(f"Move count: {game.fullmove_number}, White to move: {game.white_to_move}")

    # Final summary
    print("\n" + "=" * 60)
    print("                   GAME SUMMARY")
    print("=" * 60)

    print(f"\nTotal moves played: {total_moves}")
    print(f"\nSegment breakdown:")
    for seg in stats["segments"]:
        print(f"  Segment {seg['segment']}: {seg['config']} - {seg['moves_played']} moves ({seg['result']})")

    print("\n--- Final Board Position ---")
    game.display()

    # Count remaining pieces
    pieces = {"white": [], "black": []}
    for row in range(8):
        for col in range(8):
            piece = game.board[row][col]
            if piece != '.':
                if piece.isupper():
                    pieces["white"].append(piece)
                else:
                    pieces["black"].append(piece.upper())

    print(f"\nRemaining pieces:")
    print(f"  White: {', '.join(pieces['white'])} ({len(pieces['white'])} pieces)")
    print(f"  Black: {', '.join(pieces['black'])} ({len(pieces['black'])} pieces)")


if __name__ == "__main__":
    main()
