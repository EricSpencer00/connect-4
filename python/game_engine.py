"""
Connect 4 Game Engine
This module provides core game mechanics and evaluation for Connect 4.
"""

import math
import copy
import random
import time
import logging
from python.connect4 import ROWS, COLS, EMPTY, PLAYER_PIECE, AI_PIECE, winning_move, get_next_open_row, drop_piece, is_valid_location

# Configure logging
logger = logging.getLogger('connect4_analyzer')

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
    logger.debug(f"find_forced_win_sequence: depth={depth}, piece={piece}, max_depth={max_depth}")
    
    if depth > max_depth:
        logger.debug(f"Max depth {max_depth} reached, stopping search")
        return []
    
    # If it's a win already, return empty list (base case - already won)
    if winning_move(board, piece):
        logger.debug(f"Player {piece} already won")
        return []
    
    # If it's a terminal position without a win, no forced win exists
    if is_terminal_node(board) or len(get_valid_locations(board)) == 0:
        logger.debug("Terminal node without win, no forced win")
        return []
    
    # Check for immediate win
    winning_col, winning_row = find_winning_move(board, piece)
    if winning_col is not None:
        logger.debug(f"Immediate win found at column {winning_col+1}")
        return [(winning_col, winning_row)]
    
    # If it's player's turn (piece), try each move and see if it leads to a forced win
    opponent_piece = AI_PIECE if piece == PLAYER_PIECE else PLAYER_PIECE
    player_name = "RED" if piece == PLAYER_PIECE else "YELLOW"
    
    logger.debug(f"{player_name} checking for forced wins...")
    
    # First, check if opponent has an immediate win - must block it
    opponent_win_col, opponent_win_row = find_winning_move(board, opponent_piece)
    if opponent_win_col is not None:
        logger.debug(f"Opponent has immediate win at column {opponent_win_col+1}, must block")
        # Check if after blocking, we can still force a win
        row = get_next_open_row(board, opponent_win_col)
        if row is not None:
            board_copy = [r[:] for r in board]
            drop_piece(board_copy, row, opponent_win_col, piece)
            
            # Check for subsequent forced win
            next_sequence = find_forced_win_sequence(board_copy, depth + 1, piece, max_depth)
            if next_sequence:
                logger.debug(f"After blocking, found forced win of length {len(next_sequence)}")
                return [(opponent_win_col, row)] + next_sequence
            else:
                logger.debug("No forced win after blocking opponent")
                return []
    
    # Try each possible move
    best_sequence = []
    
    for col in get_valid_locations(board):
        row = get_next_open_row(board, col)
        if row is not None:
            # Make the move
            board_copy = [r[:] for r in board]
            drop_piece(board_copy, row, col, piece)
            logger.debug(f"{player_name} trying column {col+1}")
            
            # For each opponent response, check if we can force a win
            all_opponent_moves_lead_to_win = True
            winning_sequence = []
            
            opponent_name = "YELLOW" if piece == PLAYER_PIECE else "RED"
            opponent_valid_moves = get_valid_locations(board_copy)
            
            # Special case: if there are no valid moves for opponent, this is a draw
            if not opponent_valid_moves:
                logger.debug("No valid moves for opponent - position is a draw")
                all_opponent_moves_lead_to_win = False
                continue
                
            logger.debug(f"{opponent_name} has {len(opponent_valid_moves)} possible responses")
            
            for opp_col in opponent_valid_moves:
                opp_row = get_next_open_row(board_copy, opp_col)
                if opp_row is not None:
                    # Make opponent's move
                    opp_board = [r[:] for r in board_copy]
                    drop_piece(opp_board, opp_row, opp_col, opponent_piece)
                    logger.debug(f"{opponent_name} responds with column {opp_col+1}")
                    
                    # Check if we can still force a win
                    next_sequence = find_forced_win_sequence(opp_board, depth + 1, piece, max_depth)
                    
                    if not next_sequence:  # If any opponent move prevents a forced win
                        logger.debug(f"{opponent_name} can prevent forced win by playing column {opp_col+1}")
                        all_opponent_moves_lead_to_win = False
                        break
                    
                    if not winning_sequence or len(next_sequence) < len(winning_sequence):
                        winning_sequence = next_sequence
                        logger.debug(f"Found shorter winning sequence of length {len(next_sequence)}")
            
            if all_opponent_moves_lead_to_win and winning_sequence:
                full_sequence = [(col, row)] + winning_sequence
                logger.debug(f"Forced win found for {player_name} in {len(full_sequence)} moves")
                
                # Keep track of the shortest winning sequence
                if not best_sequence or len(full_sequence) < len(best_sequence):
                    best_sequence = full_sequence
    
    # Return the best (shortest) winning sequence, or empty list if none found
    if best_sequence:
        logger.debug(f"Best forced win sequence for {player_name} is {len(best_sequence)} moves")
        return best_sequence
    else:
        logger.debug(f"No forced win found for {player_name}")
        return []

def score_position(board, piece):
    """Score the position for the given piece."""
    from python.ai import score_position
    return score_position(board, piece)

def get_best_move(board, depth, maximizing_player=True):
    """Get the best move using minimax algorithm with alpha-beta pruning."""
    from python.ai import get_ai_move
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
    logger.info(f"evaluate_board_outcome: max_depth={max_depth}")
    
    # Check if game is already over
    if winning_move(board, PLAYER_PIECE):
        logger.info("Game already won by RED")
        return "Player wins", 0, get_winning_positions(board, PLAYER_PIECE)
    if winning_move(board, AI_PIECE):
        logger.info("Game already won by YELLOW")
        return "AI wins", 0, get_winning_positions(board, AI_PIECE)
    if len(get_valid_locations(board)) == 0:
        logger.info("Board is full - draw")
        return "Draw", 0, set()
    
    # Check for immediate win for either player
    ai_col, ai_row = find_winning_move(board, AI_PIECE)
    player_col, player_row = find_winning_move(board, PLAYER_PIECE)
    
    if player_col is not None:
        # Create a temporary board to show the winning move
        logger.info(f"RED has immediate win in column {player_col+1}")
        temp_board = [r[:] for r in board]
        drop_piece(temp_board, player_row, player_col, PLAYER_PIECE)
        return "Player wins", 1, get_winning_positions(temp_board, PLAYER_PIECE)
    if ai_col is not None:
        # Create a temporary board to show the winning move
        logger.info(f"YELLOW has immediate win in column {ai_col+1}")
        temp_board = [r[:] for r in board]
        drop_piece(temp_board, ai_row, ai_col, AI_PIECE)
        return "AI wins", 1, get_winning_positions(temp_board, AI_PIECE)
    
    # Limit search depth to prevent timeout
    max_depth = min(max_depth, 8)
    logger.info(f"Searching for forced win sequences with max_depth={max_depth}")
    
    # Use evaluate_mate_in_x for complete analysis first
    try:
        from python.evaluator import evaluate_mate_in_x
        logger.info(f"Calling evaluate_mate_in_x with max_depth={max_depth}")
        result, moves, sequence = evaluate_mate_in_x(board, max_depth)
        logger.info(f"Mate finder result: {result}, moves: {moves}, sequence length: {len(sequence)}")
        
        if result == "AI wins" or result == "Player wins":
            # Create a temporary board to calculate winning positions
            temp_board = [r[:] for r in board]
            winning_positions = set()
            
            # Apply the sequence to the temporary board
            if sequence:
                for i, (col, row, piece) in enumerate(sequence):
                    if i >= moves * 2:  # Only include moves up to the mate
                        break
                    if piece == PLAYER_PIECE or piece == AI_PIECE:  # Make sure it's a valid piece
                        drop_piece(temp_board, row, col, piece)
                        winning_positions.add((row, col))
            
            # If we couldn't get winning positions from sequence, try to find them after applying moves
            if not winning_positions and moves > 0:
                # Find a winning move for the player who wins
                winning_piece = PLAYER_PIECE if result == "Player wins" else AI_PIECE
                valid_cols = get_valid_locations(temp_board)
                for col in valid_cols:
                    temp_row = get_next_open_row(temp_board, col)
                    if temp_row is not None:
                        final_board = [r[:] for r in temp_board]
                        drop_piece(final_board, temp_row, col, winning_piece)
                        if winning_move(final_board, winning_piece):
                            winning_positions.update(get_winning_positions(final_board, winning_piece))
                            break
            
            return result, moves, winning_positions
    except Exception as e:
        logger.error(f"Mate finder error: {e}")
    
    # Try to find a forced win sequence if mate finder didn't work
    logger.info("Checking for YELLOW forced win sequence")
    ai_sequence = find_forced_win_sequence(board, 0, AI_PIECE, max_depth // 2)
    logger.info(f"YELLOW forced win sequence result: {len(ai_sequence) > 0}, length: {len(ai_sequence)}")
    
    logger.info("Checking for RED forced win sequence")
    player_sequence = find_forced_win_sequence(board, 0, PLAYER_PIECE, max_depth // 2)
    logger.info(f"RED forced win sequence result: {len(player_sequence) > 0}, length: {len(player_sequence)}")
    
    if ai_sequence:
        winning_positions = set()
        # Create a temporary board to show the winning sequence
        temp_board = [r[:] for r in board]
        logger.info(f"YELLOW has forced win in {len(ai_sequence)} moves")
        for i, (col, row) in enumerate(ai_sequence):
            current_piece = AI_PIECE if i % 2 == 0 else PLAYER_PIECE
            drop_piece(temp_board, row, col, current_piece)
            winning_positions.add((row, col))
            logger.debug(f"Move {i+1}: {'YELLOW' if current_piece == AI_PIECE else 'RED'} at column {col+1}")
        return "AI wins", len(ai_sequence), winning_positions
    
    if player_sequence:
        winning_positions = set()
        # Create a temporary board to show the winning sequence
        temp_board = [r[:] for r in board]
        logger.info(f"RED has forced win in {len(player_sequence)} moves")
        for i, (col, row) in enumerate(player_sequence):
            current_piece = PLAYER_PIECE if i % 2 == 0 else AI_PIECE
            drop_piece(temp_board, row, col, current_piece)
            winning_positions.add((row, col))
            logger.debug(f"Move {i+1}: {'RED' if current_piece == PLAYER_PIECE else 'YELLOW'} at column {col+1}")
        return "Player wins", len(player_sequence), winning_positions
    
    # If no conclusive result, return evaluation based on heuristic
    logger.info("No forced outcome found, using heuristic evaluation")
    ai_score = score_position(board, AI_PIECE)
    player_score = score_position(board, PLAYER_PIECE)
    logger.info(f"Heuristic scores - RED: {player_score}, YELLOW: {ai_score}")
    
    if ai_score > player_score + 20:  # Significant advantage
        logger.info("YELLOW has significant advantage")
        return "AI likely wins", None, set()
    elif player_score > ai_score + 20:
        logger.info("RED has significant advantage")
        return "Player likely wins", None, set()
    else:
        logger.info("Position is roughly equal")
        return "Undetermined", None, set()
