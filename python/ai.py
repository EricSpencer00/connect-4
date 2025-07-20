import random
import math
import os
from connect4 import ROWS, COLS, EMPTY, PLAYER_PIECE, AI_PIECE, winning_move, get_next_open_row, drop_piece

# Import the dataset-based AI
try:
    from dataset_ai import get_dataset_ai_move
    DATASET_AI_AVAILABLE = True
    print("Dataset-based AI loaded successfully")
except Exception as e:
    print(f"Warning: Could not load dataset AI: {e}")
    DATASET_AI_AVAILABLE = False

def evaluate_window(window, piece):
    """Evaluates a four-piece window."""
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    # Winning move - highest priority
    if window.count(piece) == 4:
        score += 100
    # Near win - high priority
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    # Developing threat - medium priority
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    # Opponent threats - needs to be valued correctly relative to our own threats
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 10  # Blocking an opponent's win is very important

    # Opponent developing threats
    if window.count(opp_piece) == 2 and window.count(EMPTY) == 2:
        score -= 2  # Block developing threats

    return score

def score_position(board, piece):
    """Scores the entire board."""
    score = 0
    opponent_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    # First check for immediate winning threats
    for col in range(COLS):
        row = get_next_open_row(board, col)
        if row is not None:
            # Check if this move would win
            b_copy = [r[:] for r in board]
            drop_piece(b_copy, row, col, piece)
            if winning_move(b_copy, piece):
                score += 50  # High score for potential winning move
                
            # Check if opponent would win if they play here
            b_copy = [r[:] for r in board]
            drop_piece(b_copy, row, col, opponent_piece)
            if winning_move(b_copy, opponent_piece):
                score -= 50  # High penalty for not blocking

    ## Score center column (control of center is advantageous)
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

    ## Score positive sloped diagonal
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    ## Score negative sloped diagonal
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
    """Gets the best move for the AI using either dataset-based approach or minimax."""
    # Try to use the dataset-based AI if available
    if DATASET_AI_AVAILABLE:
        try:
            # Use the dataset-based approach
            return get_dataset_ai_move(board)
        except Exception as e:
            print(f"Error using dataset AI: {e}. Falling back to minimax.")
            # Fall back to minimax if there's an error
    
    # Minimax with alpha-beta pruning as fallback
    valid_locations = get_valid_locations(board)
    
    # Check for immediate winning moves or blocking moves before entering minimax
    if maximizingPlayer:  # AI's turn
        # First check if AI can win in one move
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row is not None:
                b_copy = [r[:] for r in board]
                drop_piece(b_copy, row, col, AI_PIECE)
                if winning_move(b_copy, AI_PIECE):
                    return col, 100000000000000
                
        # Then check if need to block opponent from winning
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row is not None:
                b_copy = [r[:] for r in board]
                drop_piece(b_copy, row, col, PLAYER_PIECE)
                if winning_move(b_copy, PLAYER_PIECE):
                    return col, 99000000000000  # Slightly less than winning, but still very high
    
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations) if valid_locations else None
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row is None:
                continue
                
            b_copy = [r[:] for r in board]
            drop_piece(b_copy, row, col, AI_PIECE)
            
            new_score = get_ai_move(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:  # Minimizing player (opponent)
        value = math.inf
        column = random.choice(valid_locations) if valid_locations else None
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row is None:
                continue
                
            b_copy = [r[:] for r in board]
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            
            new_score = get_ai_move(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value