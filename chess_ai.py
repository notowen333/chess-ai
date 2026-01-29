#!/usr/bin/env python3
"""
Chess AI - Two AI players compete against each other.
Press Enter to see each move.
"""

import copy
import sys
import os

# Use environment variable or default to relative path from script location
PYTHON_CHESS_PATH = os.environ.get('PYTHON_CHESS_PATH',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Python-Chess'))
sys.path.insert(0, PYTHON_CHESS_PATH)

from chessengine.display import print_board, piece_to_symbol

# Piece values for evaluation
PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000
}

# Position tables for piece-square evaluation
PAWN_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
]

KNIGHT_TABLE = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

BISHOP_TABLE = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

ROOK_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [0,  0,  0,  5,  5,  0,  0,  0]
]

QUEEN_TABLE = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-5,  0,  5,  5,  5,  5,  0, -5],
    [0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

KING_TABLE = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20, 20,  0,  0,  0,  0, 20, 20],
    [20, 30, 10,  0,  0, 10, 30, 20]
]

PIECE_TABLES = {
    'P': PAWN_TABLE, 'N': KNIGHT_TABLE, 'B': BISHOP_TABLE,
    'R': ROOK_TABLE, 'Q': QUEEN_TABLE, 'K': KING_TABLE
}


class ChessGame:
    def __init__(self):
        # Board uses row 0 = rank 1 (white's back rank)
        self.board = self.create_initial_board()
        self.white_to_move = True
        self.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant_target = None
        self.move_history = []
        self.halfmove_clock = 0
        self.fullmove_number = 1

    def create_initial_board(self):
        """Create the initial chess board. Row 0 = rank 1, row 7 = rank 8."""
        return [
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],  # rank 1 (white)
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],  # rank 2
            ['.', '.', '.', '.', '.', '.', '.', '.'],  # rank 3
            ['.', '.', '.', '.', '.', '.', '.', '.'],  # rank 4
            ['.', '.', '.', '.', '.', '.', '.', '.'],  # rank 5
            ['.', '.', '.', '.', '.', '.', '.', '.'],  # rank 6
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],  # rank 7 (black)
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']   # rank 8
        ]

    def display(self):
        """Display the board using the shared display module."""
        print_board(self.board)

    def is_white_piece(self, piece):
        return piece.isupper()

    def is_black_piece(self, piece):
        return piece.islower()

    def is_own_piece(self, piece):
        if piece == '.':
            return False
        if self.white_to_move:
            return self.is_white_piece(piece)
        return self.is_black_piece(piece)

    def is_enemy_piece(self, piece):
        if piece == '.':
            return False
        if self.white_to_move:
            return self.is_black_piece(piece)
        return self.is_white_piece(piece)

    def get_all_moves(self, check_legal=True):
        """Get all possible moves for the current player."""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if self.is_own_piece(piece):
                    piece_moves = self.get_piece_moves(row, col, piece)
                    moves.extend(piece_moves)

        if check_legal:
            legal_moves = []
            for move in moves:
                if self.is_legal_move(move):
                    legal_moves.append(move)
            return legal_moves
        return moves

    def get_piece_moves(self, row, col, piece):
        """Get all moves for a specific piece."""
        piece_type = piece.upper()
        moves = []

        if piece_type == 'P':
            moves = self.get_pawn_moves(row, col)
        elif piece_type == 'N':
            moves = self.get_knight_moves(row, col)
        elif piece_type == 'B':
            moves = self.get_bishop_moves(row, col)
        elif piece_type == 'R':
            moves = self.get_rook_moves(row, col)
        elif piece_type == 'Q':
            moves = self.get_queen_moves(row, col)
        elif piece_type == 'K':
            moves = self.get_king_moves(row, col)

        return moves

    def get_pawn_moves(self, row, col):
        """Get pawn moves."""
        moves = []
        direction = 1 if self.white_to_move else -1
        start_row = 1 if self.white_to_move else 6

        # Forward move
        new_row = row + direction
        if 0 <= new_row < 8 and self.board[new_row][col] == '.':
            moves.append((row, col, new_row, col))
            # Double move from starting position
            if row == start_row:
                new_row2 = row + 2 * direction
                if self.board[new_row2][col] == '.':
                    moves.append((row, col, new_row2, col))

        # Captures
        for dc in [-1, 1]:
            new_col = col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if self.is_enemy_piece(self.board[new_row][new_col]):
                    moves.append((row, col, new_row, new_col))
                # En passant
                if self.en_passant_target == (new_row, new_col):
                    moves.append((row, col, new_row, new_col))

        return moves

    def get_knight_moves(self, row, col):
        """Get knight moves."""
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target == '.' or self.is_enemy_piece(target):
                    moves.append((row, col, new_row, new_col))
        return moves

    def get_sliding_moves(self, row, col, directions):
        """Get moves for sliding pieces (bishop, rook, queen)."""
        moves = []
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target == '.':
                    moves.append((row, col, new_row, new_col))
                elif self.is_enemy_piece(target):
                    moves.append((row, col, new_row, new_col))
                    break
                else:
                    break
                new_row += dr
                new_col += dc
        return moves

    def get_bishop_moves(self, row, col):
        return self.get_sliding_moves(row, col, [(-1, -1), (-1, 1), (1, -1), (1, 1)])

    def get_rook_moves(self, row, col):
        return self.get_sliding_moves(row, col, [(-1, 0), (1, 0), (0, -1), (0, 1)])

    def get_queen_moves(self, row, col):
        return self.get_sliding_moves(row, col, [(-1, -1), (-1, 1), (1, -1), (1, 1),
                                                  (-1, 0), (1, 0), (0, -1), (0, 1)])

    def get_king_moves(self, row, col):
        """Get king moves including castling."""
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.board[new_row][new_col]
                    if target == '.' or self.is_enemy_piece(target):
                        moves.append((row, col, new_row, new_col))

        # Castling
        if self.white_to_move:
            if self.castling_rights['K'] and self.can_castle_kingside(0):
                moves.append((0, 4, 0, 6))
            if self.castling_rights['Q'] and self.can_castle_queenside(0):
                moves.append((0, 4, 0, 2))
        else:
            if self.castling_rights['k'] and self.can_castle_kingside(7):
                moves.append((7, 4, 7, 6))
            if self.castling_rights['q'] and self.can_castle_queenside(7):
                moves.append((7, 4, 7, 2))

        return moves

    def can_castle_kingside(self, row):
        """Check if kingside castling is possible."""
        if self.board[row][5] != '.' or self.board[row][6] != '.':
            return False
        if self.is_square_attacked(row, 4) or self.is_square_attacked(row, 5) or self.is_square_attacked(row, 6):
            return False
        return True

    def can_castle_queenside(self, row):
        """Check if queenside castling is possible."""
        if self.board[row][1] != '.' or self.board[row][2] != '.' or self.board[row][3] != '.':
            return False
        if self.is_square_attacked(row, 4) or self.is_square_attacked(row, 3) or self.is_square_attacked(row, 2):
            return False
        return True

    def is_square_attacked(self, row, col):
        """Check if a square is attacked by the opponent (without recursion)."""
        enemy_is_white = not self.white_to_move

        # Check for pawn attacks
        pawn_dir = -1 if enemy_is_white else 1
        enemy_pawn = 'P' if enemy_is_white else 'p'
        for dc in [-1, 1]:
            pr, pc = row + pawn_dir, col + dc
            if 0 <= pr < 8 and 0 <= pc < 8:
                if self.board[pr][pc] == enemy_pawn:
                    return True

        # Check for knight attacks
        enemy_knight = 'N' if enemy_is_white else 'n'
        knight_offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                         (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_offsets:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if self.board[nr][nc] == enemy_knight:
                    return True

        # Check for king attacks (for adjacent squares)
        enemy_king = 'K' if enemy_is_white else 'k'
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                kr, kc = row + dr, col + dc
                if 0 <= kr < 8 and 0 <= kc < 8:
                    if self.board[kr][kc] == enemy_king:
                        return True

        # Check for sliding piece attacks (rook, bishop, queen)
        enemy_rook = 'R' if enemy_is_white else 'r'
        enemy_bishop = 'B' if enemy_is_white else 'b'
        enemy_queen = 'Q' if enemy_is_white else 'q'

        # Rook/Queen directions (straight lines)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                piece = self.board[nr][nc]
                if piece != '.':
                    if piece == enemy_rook or piece == enemy_queen:
                        return True
                    break  # Blocked by another piece
                nr += dr
                nc += dc

        # Bishop/Queen directions (diagonals)
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = row + dr, col + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                piece = self.board[nr][nc]
                if piece != '.':
                    if piece == enemy_bishop or piece == enemy_queen:
                        return True
                    break  # Blocked by another piece
                nr += dr
                nc += dc

        return False

    def find_king(self, white):
        """Find the king's position."""
        king = 'K' if white else 'k'
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == king:
                    return (row, col)
        return None

    def is_in_check(self):
        """Check if the current player is in check."""
        king_pos = self.find_king(self.white_to_move)
        if king_pos is None:
            return True
        return self.is_square_attacked(king_pos[0], king_pos[1])

    def is_legal_move(self, move):
        """Check if a move is legal (doesn't leave king in check)."""
        # Make move temporarily
        game_copy = copy.deepcopy(self)
        game_copy.make_move(move, check_legal=False)
        game_copy.white_to_move = not game_copy.white_to_move
        return not game_copy.is_in_check()

    def make_move(self, move, check_legal=True):
        """Make a move on the board."""
        from_row, from_col, to_row, to_col = move
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]

        # Handle en passant capture
        if piece.upper() == 'P' and (to_row, to_col) == self.en_passant_target:
            captured_row = from_row
            self.board[captured_row][to_col] = '.'

        # Update en passant target
        self.en_passant_target = None
        if piece.upper() == 'P' and abs(to_row - from_row) == 2:
            self.en_passant_target = ((from_row + to_row) // 2, from_col)

        # Handle castling
        if piece.upper() == 'K' and abs(to_col - from_col) == 2:
            if to_col == 6:  # Kingside
                self.board[from_row][7] = '.'
                self.board[from_row][5] = 'R' if self.white_to_move else 'r'
            else:  # Queenside
                self.board[from_row][0] = '.'
                self.board[from_row][3] = 'R' if self.white_to_move else 'r'

        # Update castling rights
        if piece == 'K':
            self.castling_rights['K'] = False
            self.castling_rights['Q'] = False
        elif piece == 'k':
            self.castling_rights['k'] = False
            self.castling_rights['q'] = False
        elif piece == 'R':
            if from_row == 0 and from_col == 0:
                self.castling_rights['Q'] = False
            elif from_row == 0 and from_col == 7:
                self.castling_rights['K'] = False
        elif piece == 'r':
            if from_row == 7 and from_col == 0:
                self.castling_rights['q'] = False
            elif from_row == 7 and from_col == 7:
                self.castling_rights['k'] = False

        # Make the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = '.'

        # Pawn promotion (auto-queen)
        if piece.upper() == 'P' and (to_row == 0 or to_row == 7):
            self.board[to_row][to_col] = 'Q' if self.white_to_move else 'q'

        # Update game state
        self.white_to_move = not self.white_to_move
        if self.white_to_move:
            self.fullmove_number += 1

        # Update move history
        self.move_history.append(move)

        return captured

    def move_to_algebraic(self, move):
        """Convert a move to algebraic notation."""
        from_row, from_col, to_row, to_col = move
        from_square = chr(ord('a') + from_col) + str(from_row + 1)
        to_square = chr(ord('a') + to_col) + str(to_row + 1)
        return from_square + to_square

    def is_checkmate(self):
        """Check if the current player is in checkmate."""
        if not self.is_in_check():
            return False
        return len(self.get_all_moves()) == 0

    def is_stalemate(self):
        """Check if the game is a stalemate."""
        if self.is_in_check():
            return False
        return len(self.get_all_moves()) == 0

    def is_insufficient_material(self):
        """Check for insufficient material draw."""
        pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != '.':
                    pieces.append(piece)

        # King vs King
        if len(pieces) == 2:
            return True
        # King + minor piece vs King
        if len(pieces) == 3:
            for p in pieces:
                if p.upper() in ['N', 'B']:
                    return True
        return False


class ChessAI:
    """
    Enhanced Chess AI with:
    - Opening book for fast early game
    - Quiescence search to avoid horizon effect
    - Iterative deepening for better time management
    - Enhanced evaluation (king safety, pawn structure, mobility)
    - Late move reductions for deeper effective search
    - History heuristic for better move ordering
    """

    # Opening book: maps board state to best response (first 10 moves)
    OPENING_BOOK = {
        # Standard responses to common openings
        # Format: (move_count, last_move_notation) -> response_move
        (0, None): (1, 4, 3, 4),  # e2e4 (King's pawn)
        (1, 'e2e4'): (6, 4, 4, 4),  # e7e5
        (1, 'd2d4'): (6, 3, 4, 3),  # d7d5
        (2, 'e7e5'): (0, 6, 2, 5),  # Nf3
        (2, 'd7d5'): (0, 1, 2, 2),  # Nc3
        (3, 'g1f3'): (7, 1, 5, 2),  # Nc6
        (3, 'b1c3'): (7, 6, 5, 5),  # Nf6
        (4, 'b8c6'): (0, 5, 3, 2),  # Bb5 (Ruy Lopez) or Bc4 (Italian)
        (4, 'g8f6'): (0, 5, 3, 2),  # Bc4
    }

    # Endgame king table (king should be active in endgame)
    KING_ENDGAME_TABLE = [
        [-50,-40,-30,-20,-20,-30,-40,-50],
        [-30,-20,-10,  0,  0,-10,-20,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-30,  0,  0,  0,  0,-30,-30],
        [-50,-30,-30,-30,-30,-30,-30,-50]
    ]

    def __init__(self, depth=3):
        self.depth = depth
        self.nodes_searched = 0
        self.transposition_table = {}
        self.killer_moves = [[] for _ in range(20)]
        self.position_history = {}
        # History heuristic: tracks which moves have been good historically
        self.history_table = [[0] * 64 for _ in range(64)]
        # Counter moves: response to opponent's last move
        self.counter_moves = {}

    def get_board_hash(self, game):
        """Create a hashable representation of the board state."""
        board_tuple = tuple(tuple(row) for row in game.board)
        return (board_tuple, game.white_to_move,
                tuple(sorted(game.castling_rights.items())),
                game.en_passant_target)

    def is_endgame(self, game):
        """Detect if we're in endgame phase."""
        queens = 0
        minor_major = 0
        for row in range(8):
            for col in range(8):
                piece = game.board[row][col]
                if piece.upper() == 'Q':
                    queens += 1
                elif piece.upper() in ['R', 'B', 'N']:
                    minor_major += 1
        # Endgame: no queens, or queen + 1 minor piece max per side
        return queens == 0 or (queens <= 2 and minor_major <= 2)

    def evaluate_king_safety(self, game, white):
        """Evaluate king safety based on pawn shield and attackers."""
        king_pos = game.find_king(white)
        if not king_pos:
            return 0

        kr, kc = king_pos
        score = 0
        own_pawn = 'P' if white else 'p'
        pawn_dir = 1 if white else -1

        # Pawn shield bonus
        for dc in [-1, 0, 1]:
            pc = kc + dc
            if 0 <= pc < 8:
                pr = kr + pawn_dir
                if 0 <= pr < 8 and game.board[pr][pc] == own_pawn:
                    score += 10
                pr2 = kr + 2 * pawn_dir
                if 0 <= pr2 < 8 and game.board[pr2][pc] == own_pawn:
                    score += 5

        # Penalty for open files near king
        for dc in [-1, 0, 1]:
            pc = kc + dc
            if 0 <= pc < 8:
                has_pawn = False
                for r in range(8):
                    if game.board[r][pc].upper() == 'P':
                        has_pawn = True
                        break
                if not has_pawn:
                    score -= 15

        return score

    def evaluate_pawn_structure(self, game, white):
        """Evaluate pawn structure: doubled, isolated, passed pawns."""
        score = 0
        pawn = 'P' if white else 'p'
        enemy_pawn = 'p' if white else 'P'
        direction = 1 if white else -1
        promotion_row = 7 if white else 0

        pawn_files = [0] * 8

        for col in range(8):
            for row in range(8):
                if game.board[row][col] == pawn:
                    pawn_files[col] += 1

                    # Check for passed pawn
                    is_passed = True
                    for check_row in range(row + direction, promotion_row + direction, direction):
                        if 0 <= check_row < 8:
                            for dc in [-1, 0, 1]:
                                cc = col + dc
                                if 0 <= cc < 8 and game.board[check_row][cc] == enemy_pawn:
                                    is_passed = False
                                    break
                        if not is_passed:
                            break

                    if is_passed:
                        # Passed pawn bonus increases as it advances
                        advance = row if white else (7 - row)
                        score += 20 + advance * 10

                    # Isolated pawn penalty
                    has_neighbor = False
                    for dc in [-1, 1]:
                        nc = col + dc
                        if 0 <= nc < 8 and pawn_files[nc] > 0:
                            has_neighbor = True
                            break
                    # Check adjacent columns for any pawns
                    for dc in [-1, 1]:
                        nc = col + dc
                        if 0 <= nc < 8:
                            for r in range(8):
                                if game.board[r][nc] == pawn:
                                    has_neighbor = True
                                    break
                    if not has_neighbor:
                        score -= 15

        # Doubled pawn penalty
        for count in pawn_files:
            if count > 1:
                score -= 10 * (count - 1)

        return score

    def evaluate_mobility(self, game):
        """Evaluate piece mobility (number of legal moves)."""
        # Save current state
        original_turn = game.white_to_move

        # Count white moves
        game.white_to_move = True
        white_moves = len(game.get_all_moves(check_legal=False))

        # Count black moves
        game.white_to_move = False
        black_moves = len(game.get_all_moves(check_legal=False))

        # Restore state
        game.white_to_move = original_turn

        return (white_moves - black_moves) * 2

    def evaluate(self, game):
        """Enhanced board evaluation."""
        if game.is_checkmate():
            return -20000 if game.white_to_move else 20000
        if game.is_stalemate() or game.is_insufficient_material():
            return 0

        score = 0
        is_endgame = self.is_endgame(game)

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
                    # Use endgame king table if in endgame
                    if piece_type == 'K' and is_endgame:
                        table = self.KING_ENDGAME_TABLE
                    else:
                        table = PIECE_TABLES[piece_type]

                    if piece.isupper():
                        score += table[7 - row][col]
                    else:
                        score -= table[row][col]

        # King safety (less important in endgame)
        if not is_endgame:
            score += self.evaluate_king_safety(game, True)
            score -= self.evaluate_king_safety(game, False)

        # Pawn structure
        score += self.evaluate_pawn_structure(game, True)
        score -= self.evaluate_pawn_structure(game, False)

        # Mobility (simplified - full calculation is expensive)
        if self.nodes_searched % 10 == 0:  # Only compute occasionally
            score += self.evaluate_mobility(game)

        # Repetition penalty
        board_hash = self.get_board_hash(game)
        if board_hash in self.position_history:
            repetition_count = self.position_history[board_hash]
            penalty = repetition_count * 50
            score -= penalty if game.white_to_move else -penalty

        return score

    def quiescence_search(self, game, alpha, beta, maximizing, depth=0):
        """Search captures to avoid horizon effect."""
        self.nodes_searched += 1

        stand_pat = self.evaluate(game)

        if maximizing:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)

        # Only search captures (and promotions)
        if depth > 4:  # Limit quiescence depth
            return stand_pat

        moves = game.get_all_moves()
        captures = []
        for move in moves:
            to_row, to_col = move[2], move[3]
            if game.board[to_row][to_col] != '.':
                captures.append(move)
            # Include pawn promotions
            piece = game.board[move[0]][move[1]]
            if piece.upper() == 'P' and (move[2] == 0 or move[2] == 7):
                captures.append(move)

        if not captures:
            return stand_pat

        # MVV-LVA ordering for captures
        def capture_score(move):
            captured = game.board[move[2]][move[3]]
            attacker = game.board[move[0]][move[1]]
            return abs(PIECE_VALUES.get(captured, 0)) * 10 - abs(PIECE_VALUES.get(attacker, 0))

        captures.sort(key=capture_score, reverse=True)

        for move in captures:
            game_copy = copy.deepcopy(game)
            game_copy.make_move(move)
            score = self.quiescence_search(game_copy, alpha, beta, not maximizing, depth + 1)

            if maximizing:
                if score >= beta:
                    return beta
                alpha = max(alpha, score)
            else:
                if score <= alpha:
                    return alpha
                beta = min(beta, score)

        return alpha if maximizing else beta

    def minimax(self, game, depth, alpha, beta, maximizing, ply=0, last_move=None):
        """Minimax with alpha-beta, LMR, and quiescence search."""
        self.nodes_searched += 1

        in_check = game.is_in_check()
        if in_check and depth == 0:
            depth = 1

        # Transposition table lookup
        board_hash = self.get_board_hash(game)
        if board_hash in self.transposition_table:
            cached_depth, cached_score, cached_move, cached_flag = self.transposition_table[board_hash]
            if cached_depth >= depth:
                if cached_flag == 'exact':
                    return cached_score, cached_move
                elif cached_flag == 'lower' and cached_score >= beta:
                    return cached_score, cached_move
                elif cached_flag == 'upper' and cached_score <= alpha:
                    return cached_score, cached_move

        if game.is_checkmate() or game.is_stalemate():
            return self.evaluate(game), None

        if depth == 0:
            return self.quiescence_search(game, alpha, beta, maximizing), None

        moves = game.get_all_moves()
        if not moves:
            return self.evaluate(game), None

        # Enhanced move ordering
        def move_score(move):
            score = 0
            from_sq = move[0] * 8 + move[1]
            to_sq = move[2] * 8 + move[3]
            captured = game.board[move[2]][move[3]]
            moving_piece = game.board[move[0]][move[1]]

            # Hash move from TT gets highest priority
            if board_hash in self.transposition_table:
                _, _, tt_move, _ = self.transposition_table[board_hash]
                if tt_move == move:
                    return 100000

            # MVV-LVA for captures
            if captured != '.':
                victim_value = abs(PIECE_VALUES.get(captured, 0))
                attacker_value = abs(PIECE_VALUES.get(moving_piece, 0))
                score += 50000 + victim_value * 10 - attacker_value

            # Killer moves
            if ply < len(self.killer_moves) and move in self.killer_moves[ply]:
                score += 40000

            # Counter move bonus
            if last_move and last_move in self.counter_moves:
                if self.counter_moves[last_move] == move:
                    score += 30000

            # History heuristic
            score += self.history_table[from_sq][to_sq]

            # Center control
            if 2 <= move[2] <= 5 and 2 <= move[3] <= 5:
                score += 50

            return score

        moves.sort(key=move_score, reverse=True)
        best_move = moves[0]
        original_alpha = alpha

        if maximizing:
            max_eval = float('-inf')
            for i, move in enumerate(moves):
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move)

                # Late Move Reduction
                reduction = 0
                if (i >= 4 and depth >= 3 and not in_check
                        and game.board[move[2]][move[3]] == '.'):
                    reduction = 1
                    if i >= 8:
                        reduction = 2

                eval_score, _ = self.minimax(
                    game_copy, depth - 1 - reduction, alpha, beta, False, ply + 1, move
                )

                # Re-search with full depth if reduced search looks good
                if reduction > 0 and eval_score > alpha:
                    eval_score, _ = self.minimax(
                        game_copy, depth - 1, alpha, beta, False, ply + 1, move
                    )

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    # Update killer moves
                    if ply < len(self.killer_moves) and move not in self.killer_moves[ply]:
                        self.killer_moves[ply].insert(0, move)
                        if len(self.killer_moves[ply]) > 2:
                            self.killer_moves[ply].pop()
                    # Update history
                    from_sq = move[0] * 8 + move[1]
                    to_sq = move[2] * 8 + move[3]
                    self.history_table[from_sq][to_sq] += depth * depth
                    # Update counter move
                    if last_move:
                        self.counter_moves[last_move] = move
                    break

            # Store in transposition table
            flag = 'exact' if original_alpha < max_eval < beta else ('lower' if max_eval >= beta else 'upper')
            self.transposition_table[board_hash] = (depth, max_eval, best_move, flag)
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for i, move in enumerate(moves):
                game_copy = copy.deepcopy(game)
                game_copy.make_move(move)

                # Late Move Reduction
                reduction = 0
                if (i >= 4 and depth >= 3 and not in_check
                        and game.board[move[2]][move[3]] == '.'):
                    reduction = 1
                    if i >= 8:
                        reduction = 2

                eval_score, _ = self.minimax(
                    game_copy, depth - 1 - reduction, alpha, beta, True, ply + 1, move
                )

                if reduction > 0 and eval_score < beta:
                    eval_score, _ = self.minimax(
                        game_copy, depth - 1, alpha, beta, True, ply + 1, move
                    )

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move

                beta = min(beta, eval_score)
                if beta <= alpha:
                    if ply < len(self.killer_moves) and move not in self.killer_moves[ply]:
                        self.killer_moves[ply].insert(0, move)
                        if len(self.killer_moves[ply]) > 2:
                            self.killer_moves[ply].pop()
                    from_sq = move[0] * 8 + move[1]
                    to_sq = move[2] * 8 + move[3]
                    self.history_table[from_sq][to_sq] += depth * depth
                    if last_move:
                        self.counter_moves[last_move] = move
                    break

            flag = 'exact' if alpha < min_eval < original_alpha else ('upper' if min_eval <= alpha else 'lower')
            self.transposition_table[board_hash] = (depth, min_eval, best_move, flag)
            return min_eval, best_move

    def get_opening_move(self, game):
        """Check opening book for a quick response."""
        move_count = len(game.move_history)
        if move_count > 8:
            return None

        last_notation = None
        if game.move_history:
            last_move = game.move_history[-1]
            last_notation = game.move_to_algebraic(last_move)

        key = (move_count, last_notation)
        if key in self.OPENING_BOOK:
            book_move = self.OPENING_BOOK[key]
            # Verify the move is legal
            legal_moves = game.get_all_moves()
            if book_move in legal_moves:
                return book_move
        return None

    def get_best_move(self, game):
        """Get the best move using iterative deepening."""
        self.nodes_searched = 0
        self.killer_moves = [[] for _ in range(20)]

        # Check opening book first
        book_move = self.get_opening_move(game)
        if book_move:
            return book_move, 1

        best_move = None

        # Iterative deepening
        for current_depth in range(1, self.depth + 1):
            _, best_move = self.minimax(
                game,
                current_depth,
                float('-inf'),
                float('inf'),
                game.white_to_move
            )

        # Update position history
        if best_move:
            game_copy = copy.deepcopy(game)
            game_copy.make_move(best_move)
            board_hash = self.get_board_hash(game_copy)
            self.position_history[board_hash] = self.position_history.get(board_hash, 0) + 1

        return best_move, self.nodes_searched


def main():
    print("=" * 50)
    print("       CHESS AI vs AI")
    print("=" * 50)
    print("\nPress Enter to see each move.")
    print("Press Ctrl+C to quit.\n")

    game = ChessGame()
    white_ai = ChessAI(depth=3)
    black_ai = ChessAI(depth=3)

    move_count = 0

    try:
        while True:
            game.display()

            # Check for game over
            if game.is_checkmate():
                winner = "Black" if game.white_to_move else "White"
                print(f"Checkmate! {winner} wins!")
                break

            if game.is_stalemate():
                print("Stalemate! It's a draw.")
                break

            if game.is_insufficient_material():
                print("Draw by insufficient material.")
                break

            if move_count >= 500:
                print("Draw by move limit (500 moves).")
                break

            # Get current player info
            current_player = "White" if game.white_to_move else "Black"
            current_ai = white_ai if game.white_to_move else black_ai

            if game.is_in_check():
                print(f"{current_player} is in CHECK!")

            print(f"Move {move_count + 1}: {current_player}'s turn")
            input("Press Enter to see the move...")

            # AI makes a move
            best_move, nodes = current_ai.get_best_move(game)

            if best_move is None:
                print("No legal moves available!")
                break

            move_notation = game.move_to_algebraic(best_move)
            piece = game.board[best_move[0]][best_move[1]]
            piece_symbol = piece_to_symbol(piece)
            captured = game.board[best_move[2]][best_move[3]]

            game.make_move(best_move)
            move_count += 1

            # Display move info
            capture_str = f" captures {piece_to_symbol(captured)}" if captured != '.' else ""
            print(f"\n{current_player} plays: {piece_symbol} {move_notation}{capture_str}")
            print(f"(Searched {nodes} positions)\n")

    except KeyboardInterrupt:
        print("\n\nGame interrupted.")

    print("\nFinal position:")
    game.display()
    print(f"Total moves played: {move_count}")


if __name__ == "__main__":
    main()
