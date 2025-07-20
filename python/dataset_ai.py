"""
Connect 4 Dataset-based AI
This module provides AI decision making based on the Connect-4 dataset.
"""

import os
import gzip
import numpy as np
from connect4 import ROWS, COLS, EMPTY, PLAYER_PIECE, AI_PIECE, winning_move, get_next_open_row, drop_piece

# Constants for dataset mapping
X_MARKER = 'x'
O_MARKER = 'o'
BLANK_MARKER = 'b'
WIN_CLASS = 'win'
LOSS_CLASS = 'loss'
DRAW_CLASS = 'draw'

# Constants for dataset positioning
BOARD_POSITIONS = 42  # 7 columns x 6 rows
CLASS_INDEX = 42  # The index of the class (win/loss/draw) in the dataset entries

# Global variable to store the dataset
dataset = None

def load_dataset(dataset_path):
    """
    Load the Connect-4 dataset from the compressed file.
    
    Args:
        dataset_path: Path to the connect-4.data.Z file
    
    Returns:
        A list of tuples (board_state, outcome) where board_state is a list of
        cell values and outcome is the expected result (win/loss/draw)
    """
    global dataset
    
    if dataset is not None:
        return dataset
    
    dataset = []
    
    # Handle the compressed file
    try:
        # Create a temporary file to store the uncompressed data
        import tempfile
        import subprocess
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Uncompress the file using system command
        subprocess.run(['uncompress', '-c', dataset_path], stdout=open(temp_path, 'wb'))
        
        # Read the uncompressed data
        with open(temp_path, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == BOARD_POSITIONS + 1:  # Board positions + class
                    board_state = parts[:BOARD_POSITIONS]
                    outcome = parts[CLASS_INDEX]
                    dataset.append((board_state, outcome))
        
        # Clean up temporary file
        os.remove(temp_path)
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return []
    
    print(f"Loaded {len(dataset)} positions from dataset")
    return dataset

def map_board_to_dataset_format(board):
    """
    Convert our internal board representation to the dataset format.
    
    Args:
        board: 2D list representing the Connect 4 board (ROWS x COLS)
    
    Returns:
        A list of length 42 with 'x', 'o', or 'b' values representing the board state
    """
    # Initialize with blanks
    dataset_board = [BLANK_MARKER] * (ROWS * COLS)
    
    # The dataset uses the following naming convention:
    # a1, a2, a3, a4, a5, a6, b1, b2, ... for columns a-g and rows 1-6
    # where a1 is the bottom-left corner
    
    # Map each position from our board to the dataset format
    for row in range(ROWS):
        for col in range(COLS):
            # Calculate the index in the dataset format
            # Our board has (0,0) at bottom left, dataset is a1, a2, a3, etc.
            # Column index is 0-6, maps to a-g (7 columns)
            # Row index is 0-5, maps to 1-6 (6 rows)
            
            # Calculate position in the flat list:
            # Column 0 (a) starts at index 0, column 1 (b) starts at index 6, etc.
            # Within each column, row 0 (1) is at offset 0, row 1 (2) is at offset 1, etc.
            dataset_index = col * ROWS + row
            
            # Map the piece values
            if board[row][col] == PLAYER_PIECE:
                dataset_board[dataset_index] = X_MARKER
            elif board[row][col] == AI_PIECE:
                dataset_board[dataset_index] = O_MARKER
            else:
                dataset_board[dataset_index] = BLANK_MARKER
    
    return dataset_board

def find_matching_positions(board, dataset_data=None):
    """
    Find positions in the dataset that match or are similar to the current board.
    
    Args:
        board: 2D list representing the Connect 4 board
        dataset_data: Optional dataset to use instead of the global one
    
    Returns:
        A list of tuples (similarity_score, board_state, outcome)
        where similarity_score is higher for more similar positions
    """
    if dataset_data is None:
        global dataset
        if dataset is None:
            dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       'c4-dataset', 'connect-4.data.Z')
            dataset = load_dataset(dataset_path)
        dataset_data = dataset
    
    current_board = map_board_to_dataset_format(board)
    matches = []
    
    for board_state, outcome in dataset_data:
        # Calculate similarity score (number of matching positions)
        similarity = sum(1 for a, b in zip(current_board, board_state) if a == b)
        matches.append((similarity, board_state, outcome))
    
    # Sort by similarity (highest first)
    matches.sort(reverse=True, key=lambda x: x[0])
    
    return matches

def get_best_move_from_dataset(board, player_piece):
    """
    Determine the best move using the dataset.
    
    Args:
        board: 2D list representing the Connect 4 board
        player_piece: The piece of the player making the move (PLAYER_PIECE or AI_PIECE)
    
    Returns:
        The column to play (0-6)
    """
    # First check for immediate win
    for col in range(COLS):
        if board[ROWS-1][col] == EMPTY:  # If column has space
            row = get_next_open_row(board, col)
            if row is not None:
                # Try this move
                board_copy = [r[:] for r in board]
                drop_piece(board_copy, row, col, player_piece)
                if winning_move(board_copy, player_piece):
                    return col
    
    # Then check to block opponent's immediate win
    opponent_piece = PLAYER_PIECE if player_piece == AI_PIECE else AI_PIECE
    for col in range(COLS):
        if board[ROWS-1][col] == EMPTY:  # If column has space
            row = get_next_open_row(board, col)
            if row is not None:
                # Try this move for opponent
                board_copy = [r[:] for r in board]
                drop_piece(board_copy, row, col, opponent_piece)
                if winning_move(board_copy, opponent_piece):
                    return col
    
    # Find matching positions in dataset
    matches = find_matching_positions(board)
    
    if not matches:
        # Fallback to center or random move if no matches
        valid_moves = [col for col in range(COLS) if board[ROWS-1][col] == EMPTY]
        # Prefer center column if available
        if COLS // 2 in valid_moves:
            return COLS // 2
        return np.random.choice(valid_moves) if valid_moves else None
    
    # Analyze potential moves
    move_scores = {col: 0 for col in range(COLS) if board[ROWS-1][col] == EMPTY}
    
    # Use the top matches (more weight to closer matches)
    match_weight_factor = 0.9  # Decay factor for match importance
    match_weight = 1.0
    
    # Focus on the top 10% of matches to avoid noise
    top_matches = matches[:max(10, len(matches) // 10)]
    
    for similarity, board_state, outcome in top_matches:
        # Look at each possible move
        for col in move_scores.keys():
            row = get_next_open_row(board, col)
            if row is not None:
                # Create a new board with this move
                new_board = [r[:] for r in board]
                drop_piece(new_board, row, col, player_piece)
                
                # Find how similar this new board is to positions in the dataset
                new_matches = find_matching_positions(new_board)
                
                # Score based on outcomes of similar positions - only check if we have matches
                if new_matches and len(new_matches) > 0:
                    for i in range(min(5, len(new_matches))):  # Look at top 5 matches (safely)
                        new_similarity, _, new_outcome = new_matches[i]
                        # Score based on outcome and similarity
                        if player_piece == AI_PIECE:  # AI wants to win
                            if new_outcome == WIN_CLASS:
                                move_scores[col] += new_similarity * match_weight
                            elif new_outcome == DRAW_CLASS:
                                move_scores[col] += (new_similarity * match_weight) / 2
                        else:  # Player wants to win
                            if new_outcome == LOSS_CLASS:  # Loss for AI means win for player
                                move_scores[col] += new_similarity * match_weight
                            elif new_outcome == DRAW_CLASS:
                                move_scores[col] += (new_similarity * match_weight) / 2
        
        # Reduce weight for next match
        match_weight *= match_weight_factor
    
    # If we have valid scores, choose the best one
    if move_scores:
        return max(move_scores.items(), key=lambda x: x[1])[0]
    
    # Fallback to valid random move if no scores
    valid_moves = [col for col in range(COLS) if board[ROWS-1][col] == EMPTY]
    return np.random.choice(valid_moves) if valid_moves else None

def get_dataset_ai_move(board):
    """
    Public function to get the AI's move using the dataset approach.
    
    Args:
        board: 2D list representing the Connect 4 board
    
    Returns:
        The column to play (0-6) and a score (for compatibility with the existing AI)
    """
    # Ensure dataset is loaded
    global dataset
    if dataset is None:
        dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'c4-dataset', 'connect-4.data.Z')
        dataset = load_dataset(dataset_path)
    
    best_col = get_best_move_from_dataset(board, AI_PIECE)
    
    # Calculate a score for compatibility with the existing AI interface
    score = 0
    if best_col is not None:
        row = get_next_open_row(board, best_col)
        if row is not None:
            board_copy = [r[:] for r in board]
            drop_piece(board_copy, row, best_col, AI_PIECE)
            
            # Check if this is a winning move
            if winning_move(board_copy, AI_PIECE):
                score = 1000000  # High score for winning move
            else:
                # Use number of matching winning positions as score
                matches = find_matching_positions(board_copy)
                win_matches = sum(1 for _, _, outcome in matches[:10] if outcome == WIN_CLASS)
                score = win_matches * 100
    
    return best_col, score

# Pre-load the dataset when module is imported
if __name__ != "__main__":
    try:
        dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'c4-dataset', 'connect-4.data.Z')
        dataset = load_dataset(dataset_path)
    except Exception as e:
        print(f"Warning: Could not pre-load dataset: {e}")
