import random
import math
from connect4 import ROWS, COLS, EMPTY, PLAYER_PIECE, AI_PIECE, winning_move, get_next_open_row, drop_piece

def evaluate_window(window, piece):
    """Evaluates a four-piece window."""
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    """Scores the entire board."""
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(zip(*board))[COLS // 2]]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(ROWS):
        row_array = [int(i) for i in board[r]]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COLS):
        col_array = [int(i) for i in list(zip(*board))[c]]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    ## Score posiive sloped diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + 3 - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score


def get_valid_locations(board):
    """Gets a list of valid columns to move."""
    valid_locations = []
    for col in range(COLS):
        if board[ROWS - 1][col] == EMPTY:
            valid_locations.append(col)
    return valid_locations


def is_terminal_node(board):
    """Checks if the game is over."""
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def get_ai_move(board, depth, alpha, beta, maximizingPlayer):
    """Gets the best move for the AI using minimax with alpha-beta pruning."""
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = [row[:] for row in board]
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = get_ai_move(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = [row[:] for row in board]
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = get_ai_move(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value