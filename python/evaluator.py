import math
import copy
import random
import logging
from connect4 import ROWS, COLS, EMPTY, PLAYER_PIECE, AI_PIECE, winning_move, get_next_open_row, drop_piece, is_valid_location

# Configure logging
logger = logging.getLogger('connect4_analyzer')

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

def check_immediate_wins(board):
    """Check and print if there are any immediate winning moves for either player"""
    valid_locations = get_valid_locations(board)
    
    # Check for AI immediate wins
    ai_winning_cols = []
    for col in valid_locations:
        row = get_next_open_row(board, col)
        if row is not None:
            b_copy = [r[:] for r in board]
            drop_piece(b_copy, row, col, AI_PIECE)
            if winning_move(b_copy, AI_PIECE):
                ai_winning_cols.append(col)
    
    # Check for Player immediate wins
    player_winning_cols = []
    for col in valid_locations:
        row = get_next_open_row(board, col)
        if row is not None:
            b_copy = [r[:] for r in board]
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            if winning_move(b_copy, PLAYER_PIECE):
                player_winning_cols.append(col)
    
    if ai_winning_cols:
        print(f"AI can win immediately by playing in columns: {ai_winning_cols}")
    if player_winning_cols:
        print(f"Player can win immediately by playing in columns: {player_winning_cols}")
    if not ai_winning_cols and not player_winning_cols:
        print("No immediate winning moves for either player")

def minimax_mate_finder(board, depth, alpha, beta, maximizing_player, current_depth=0):
    """
    Minimax algorithm that specifically looks for forced mates.
    Returns tuple: (column, score, mate_in) where mate_in is the number of moves to mate (None if no mate found)
    """
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    
    # Current player's piece
    piece = AI_PIECE if maximizing_player else PLAYER_PIECE
    
    if is_terminal:
        if winning_move(board, AI_PIECE):
            # AI has won
            return None, 1000000, current_depth
        elif winning_move(board, PLAYER_PIECE):
            # Player has won
            return None, -1000000, current_depth
        else:
            # Draw - no mate
            return None, 0, None
    
    if depth == 0:
        # Reached depth limit without finding a forced mate
        return None, 0, None
    
    # For maximizing player (AI)
    if maximizing_player:
        value = -math.inf
        column = random.choice(valid_locations) if valid_locations else None
        mate_in = None
        all_moves_lead_to_mate = len(valid_locations) > 0  # Start assuming all moves lead to mate
        
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row is not None:
                b_copy = [r[:] for r in board]  # Proper deep copy of the board
                drop_piece(b_copy, row, col, AI_PIECE)
                
                _, new_score, new_mate_in = minimax_mate_finder(
                    b_copy, depth - 1, alpha, beta, False, current_depth + 1
                )
            
            # For the AI to have a forced win, *all* of the player's responses must lead to a mate
            if new_mate_in is None:
                all_moves_lead_to_mate = False
            
            # If we found a mate, track the shortest path to mate
            if new_mate_in is not None:
                if mate_in is None or new_mate_in < mate_in:
                    mate_in = new_mate_in
                    value = new_score
                    column = col
            # Otherwise use regular minimax scoring
            elif new_score > value:
                value = new_score
                column = col
            
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        
        # If not all moves lead to mate, then there's no forced win
        if not all_moves_lead_to_mate:
            mate_in = None
                
        return column, value, mate_in
    
    # For minimizing player (human)
    else:
        value = math.inf
        column = random.choice(valid_locations) if valid_locations else None
        mate_in = None
        any_move_avoids_mate = False
        
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row is not None:
                b_copy = [r[:] for r in board]  # Proper deep copy of the board
                drop_piece(b_copy, row, col, PLAYER_PIECE)
                
                _, new_score, new_mate_in = minimax_mate_finder(
                    b_copy, depth - 1, alpha, beta, True, current_depth + 1
                )
            
            # If any move by the player can avoid mate, then there's no forced win for AI
            if new_mate_in is None:
                any_move_avoids_mate = True
            
            # If we found a mate, track the shortest path to mate
            if new_mate_in is not None:
                if mate_in is None or new_mate_in < mate_in:
                    mate_in = new_mate_in
                    value = new_score
                    column = col
            # Otherwise use regular minimax scoring
            elif new_score < value:
                value = new_score
                column = col
                
            beta = min(beta, value)
            if alpha >= beta:
                break
        
        # If any move avoids mate, there's no forced win
        if any_move_avoids_mate:
            mate_in = None
                
        return column, value, mate_in

def evaluate_mate_in_x(board, max_depth=10):
    """
    Evaluates if there's a forced win and how many moves it will take.
    Returns a tuple (result, moves) where:
    - result: "Player wins", "AI wins", or None for no forced win found
    - moves: number of moves to reach that result with perfect play
    """
    # Check if game is already over
    if winning_move(board, PLAYER_PIECE):
        return "Player wins", 0
    if winning_move(board, AI_PIECE):
        return "AI wins", 0
    if len(get_valid_locations(board)) == 0:
        return "Draw", 0
    
    # Check if next move is winning for AI
    valid_locations = get_valid_locations(board)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        if row is not None:
            b_copy = [r[:] for r in board]  # Proper deep copy
            drop_piece(b_copy, row, col, AI_PIECE)
            if winning_move(b_copy, AI_PIECE):
                # Check if player can prevent by playing first
                player_can_win_first = False
                for player_col in valid_locations:
                    player_row = get_next_open_row(board, player_col)
                    if player_row is not None:
                        player_copy = [r[:] for r in board]  # Proper deep copy
                        drop_piece(player_copy, player_row, player_col, PLAYER_PIECE)
                        if winning_move(player_copy, PLAYER_PIECE):
                            player_can_win_first = True
                            break
                if not player_can_win_first:
                    return "AI wins", 1
    
    # Check if next move is winning for player
    for col in valid_locations:
        row = get_next_open_row(board, col)
        if row is not None:
            b_copy = [r[:] for r in board]  # Proper deep copy
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            if winning_move(b_copy, PLAYER_PIECE):
                return "Player wins", 1
    
    # Try increasing depths for deeper analysis
    for depth in range(4, max_depth + 1, 2):  # Use even depths for complete move sequences
        # Check for AI win (maximizing player)
        _, score, mate_in = minimax_mate_finder(board, depth, -math.inf, math.inf, True)
        if mate_in is not None:
            return "AI wins", (mate_in + 1) // 2  # Convert half-moves to full moves
        
        # Check for Player win (minimizing player)
        _, score, mate_in = minimax_mate_finder(board, depth, -math.inf, math.inf, False)
        if mate_in is not None:
            return "Player wins", (mate_in + 1) // 2  # Convert half-moves to full moves
    
    return None, None  # No forced mate found within depth

def print_evaluation_bar(board, current_player=None):
    """
    Prints an evaluation bar for the current Connect 4 position.
    Shows "mate in x" if a forced win is found.
    """
    import time
    
    start_time = time.time()
    print("Analyzing position...")
    
    # Print current board for debugging
    print("Current board state:")
    for r in range(ROWS-1, -1, -1):
        print(" ".join(str(board[r][c]) for c in range(COLS)))
    
    # Check for immediate wins
    check_immediate_wins(board)
    
    result, moves = evaluate_mate_in_x(board, max_depth=8)  # Increased depth to find mates earlier
    print(f"Evaluation result: {result}, moves: {moves}")
    
    if result == "AI wins":
        print(f"Evaluation: AI has mate in {moves}")
        bar = "█" * 20 + " " * 20
    elif result == "Player wins":
        print(f"Evaluation: Player has mate in {moves}")
        bar = " " * 20 + "█" * 20
    elif result == "Draw":
        print("Evaluation: Draw")
        bar = "█" * 10 + " " * 20 + "█" * 10
    else:
        print("Evaluation: Position is unclear")
        # Use a simpler evaluation for positions without a forced mate
        from ai import score_position
        ai_score = score_position(board, AI_PIECE)
        player_score = score_position(board, PLAYER_PIECE)
        relative_score = (ai_score - player_score) / 100  # Normalize
        position = max(0, min(40, int(20 + relative_score * 10)))  # Scale to 0-40 range
        bar = "█" * position + " " * (40 - position)
    
    print("[AI]" + bar + "[Player]")
    print(f"Analysis took {time.time() - start_time:.2f} seconds")
