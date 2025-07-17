"""
Connect 4 Game Engine
This module provides core game mechanics and evaluation for Connect 4.
"""

import math
import copy
import random
import time
from connect4 import ROWS, COLS, EMPTY, PLAYER_PIECE, AI_PIECE, winning_move, get_next_open_row, drop_piece, is_valid_location

def get_valid_locations(board):
    """Gets a list of valid columns to move."""
    valid_locations = []
    for col in range(COLS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def is_terminal_node(board):
    """Checks if the game is over."""
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def get_winning_positions(board, piece):
    """Returns all positions that form winning lines for a given piece."""
    winning_positions = set()
    
    # Check horizontal positions
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                for i in range(4):
                    winning_positions.add((r, c + i))
    
    # Check vertical positions
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                for i in range(4):
                    winning_positions.add((r + i, c))
    
    # Check positively sloped diagonals
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                for i in range(4):
                    winning_positions.add((r + i, c + i))
    
    # Check negatively sloped diagonals
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                for i in range(4):
                    winning_positions.add((r - i, c + i))
    
    return winning_positions

def find_winning_move(board, piece):
    """Find a winning move for the given piece if one exists.
    Returns (column, row) of the winning move or (None, None) if no winning move exists.
    """
    valid_locations = get_valid_locations(board)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        if row is not None:
            temp_board = [r[:] for r in board]
            drop_piece(temp_board, row, col, piece)
            if winning_move(temp_board, piece):
                return col, row
    return None, None

def find_forced_win_sequence(board, depth, piece, max_depth=10):
    """
    Find a sequence of moves that forces a win for the given piece.
    Returns a list of moves (column, row) that leads to a win, or empty list if no forced win.
    """
    if depth > max_depth:
        return []
    
    # If it's a win already, return empty list (base case - already won)
    if winning_move(board, piece):
        return []
    
    # If it's a terminal position without a win, no forced win exists
    if is_terminal_node(board) or len(get_valid_locations(board)) == 0:
        return []
    
    # Check for immediate win
    winning_col, winning_row = find_winning_move(board, piece)
    if winning_col is not None:
        return [(winning_col, winning_row)]
    
    # If it's player's turn (piece), try each move and see if it leads to a forced win
    opponent_piece = AI_PIECE if piece == PLAYER_PIECE else PLAYER_PIECE
    
    for col in get_valid_locations(board):
        row = get_next_open_row(board, col)
        if row is not None:
            # Make the move
            board_copy = [r[:] for r in board]
            drop_piece(board_copy, row, col, piece)
            
            # For each opponent response, check if we can force a win
            all_opponent_moves_lead_to_win = True
            winning_sequence = []
            
            for opp_col in get_valid_locations(board_copy):
                opp_row = get_next_open_row(board_copy, opp_col)
                if opp_row is not None:
                    # Make opponent's move
                    opp_board = [r[:] for r in board_copy]
                    drop_piece(opp_board, opp_row, opp_col, opponent_piece)
                    
                    # Check if we can still force a win
                    next_sequence = find_forced_win_sequence(opp_board, depth + 1, piece, max_depth)
                    
                    if not next_sequence:  # If any opponent move prevents a forced win
                        all_opponent_moves_lead_to_win = False
                        break
                    
                    if not winning_sequence or len(next_sequence) < len(winning_sequence):
                        winning_sequence = next_sequence
            
            if all_opponent_moves_lead_to_win and winning_sequence:
                return [(col, row)] + winning_sequence
    
    # No forced win found
    return []

def score_position(board, piece):
    """Score the position for the given piece."""
    from ai import score_position
    return score_position(board, piece)

def get_best_move(board, depth, maximizing_player=True):
    """Get the best move using minimax algorithm with alpha-beta pruning."""
    from ai import get_ai_move
    column, score = get_ai_move(board, depth, -math.inf, math.inf, maximizing_player)
    return column, score

def evaluate_board_outcome(board, max_depth=8):
    """
    Evaluates the board and determines the expected outcome with perfect play.
    Returns:
        (outcome, moves, winning_positions)
        outcome: "Player wins", "AI wins", "Draw", or "Undetermined"
        moves: number of moves to reach the outcome, or None if undetermined
        winning_positions: set of (row, col) tuples of the winning line, or empty set
    """
    # Check if game is already over
    if winning_move(board, PLAYER_PIECE):
        return "Player wins", 0, get_winning_positions(board, PLAYER_PIECE)
    if winning_move(board, AI_PIECE):
        return "AI wins", 0, get_winning_positions(board, AI_PIECE)
    if len(get_valid_locations(board)) == 0:
        return "Draw", 0, set()
    
    # Check for immediate win for either player
    ai_col, ai_row = find_winning_move(board, AI_PIECE)
    player_col, player_row = find_winning_move(board, PLAYER_PIECE)
    
    if player_col is not None:
        return "Player wins", 1, set([(player_row, player_col)])
    if ai_col is not None:
        return "AI wins", 1, set([(ai_row, ai_col)])
    
    # Use minimax with pruning to determine outcome
    from evaluator import minimax_mate_finder, evaluate_mate_in_x
    
    # Try to find a forced win sequence
    ai_sequence = find_forced_win_sequence(board, 0, AI_PIECE, max_depth // 2)
    player_sequence = find_forced_win_sequence(board, 0, PLAYER_PIECE, max_depth // 2)
    
    if ai_sequence:
        winning_positions = set()
        for col, row in ai_sequence:
            winning_positions.add((row, col))
        return "AI wins", len(ai_sequence), winning_positions
    
    if player_sequence:
        winning_positions = set()
        for col, row in player_sequence:
            winning_positions.add((row, col))
        return "Player wins", len(player_sequence), winning_positions
    
    # Fall back to evaluate_mate_in_x for deeper analysis
    result, moves = evaluate_mate_in_x(board, max_depth)
    
    if result == "AI wins":
        # We don't have the exact winning positions, but we know AI wins
        return result, moves, set()
    elif result == "Player wins":
        return result, moves, set()
    elif result == "Draw":
        return result, 0, set()
    
    # If no conclusive result, return evaluation based on heuristic
    ai_score = score_position(board, AI_PIECE)
    player_score = score_position(board, PLAYER_PIECE)
    
    if ai_score > player_score + 20:  # Significant advantage
        return "AI likely wins", None, set()
    elif player_score > ai_score + 20:
        return "Player likely wins", None, set()
    else:
        return "Undetermined", None, set()
