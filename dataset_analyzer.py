"""
Connect 4 Dataset Analysis Tool
This script analyzes positions using the Connect 4 dataset.
"""

import os
import sys
import argparse
import numpy as np
from python.connect4 import create_board, drop_piece, print_board, EMPTY, PLAYER_PIECE, AI_PIECE
from python.dataset_ai import map_board_to_dataset_format, find_matching_positions, load_dataset

def analyze_position(board, dataset_path):
    """Analyze a Connect 4 position using the dataset."""
    # Load the dataset
    dataset = load_dataset(dataset_path)
    if not dataset:
        print("Error: Could not load dataset.")
        return
    
    # Map the board to dataset format
    board_format = map_board_to_dataset_format(board)
    
    # Find matching positions
    matches = find_matching_positions(board, dataset)
    
    # Display the top matches
    print(f"Found {len(matches)} matching positions.")
    print("\nTop 10 matching positions:")
    print("Similarity | Outcome")
    print("-" * 30)
    
    for i, (similarity, board_state, outcome) in enumerate(matches[:10]):
        print(f"{similarity:9d} | {outcome}")
    
    # Analyze potential moves
    print("\nMove analysis:")
    print("Column | Win % | Draw % | Loss %")
    print("-" * 40)
    
    valid_columns = [col for col in range(7) if board[5][col] == EMPTY]
    for col in valid_columns:
        # Create a new board with this move for AI
        new_board = [row[:] for row in board]
        for row in range(6):
            if new_board[row][col] == EMPTY:
                drop_piece(new_board, row, col, AI_PIECE)
                break
                
        new_matches = find_matching_positions(new_board, matches[:100])
        
        # Calculate win/draw/loss percentages
        total = len(new_matches) if new_matches else 1
        win_count = sum(1 for _, _, outcome in new_matches if outcome == "win")
        draw_count = sum(1 for _, _, outcome in new_matches if outcome == "draw")
        loss_count = sum(1 for _, _, outcome in new_matches if outcome == "loss")
        
        win_pct = (win_count / total) * 100
        draw_pct = (draw_count / total) * 100
        loss_pct = (loss_count / total) * 100
        
        print(f"{col:6d} | {win_pct:5.1f}% | {draw_pct:5.1f}% | {loss_pct:5.1f}%")

def main():
    parser = argparse.ArgumentParser(description="Connect 4 Dataset Analysis Tool")
    parser.add_argument("--position", type=str, help="Position to analyze (e.g., '...x.o.x.o...')")
    args = parser.parse_args()
    
    # Create a default empty board
    board = create_board()
    
    # Get the dataset path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(script_dir, "c4-dataset", "connect-4.data.Z")
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return
    
    # If a position was specified, parse it
    if args.position:
        # TODO: Implement position parsing
        pass
    
    # Use an interactive loop if no position was specified
    if not args.position:
        print("Interactive Connect 4 Dataset Analysis Tool")
        print("------------------------------------------")
        print("Enter moves in format 'column player' (e.g., '3 1' for player 1 in column 3)")
        print("Players: 1=Red, 2=Yellow")
        print("Commands: 'print' to view board, 'analyze' to analyze position, 'reset' to clear board, 'quit' to exit")
        
        while True:
            command = input("\nEnter move or command: ").strip().lower()
            
            if command == "quit" or command == "exit":
                break
            elif command == "print":
                print_board(board)
            elif command == "analyze":
                print_board(board)
                analyze_position(board, dataset_path)
            elif command == "reset":
                board = create_board()
                print("Board reset.")
            else:
                try:
                    parts = command.split()
                    if len(parts) == 2:
                        col = int(parts[0])
                        player = int(parts[1])
                        
                        if 0 <= col < 7 and player in [1, 2]:
                            # Find the first empty row in this column
                            row = None
                            for r in range(6):
                                if board[r][col] == EMPTY:
                                    row = r
                                    break
                            
                            if row is not None:
                                piece = PLAYER_PIECE if player == 1 else AI_PIECE
                                drop_piece(board, row, col, piece)
                                print_board(board)
                            else:
                                print("Column is full. Try another column.")
                        else:
                            print("Invalid input. Column must be 0-6, player must be 1 or 2.")
                    else:
                        print("Invalid format. Use 'column player' (e.g., '3 1').")
                except ValueError:
                    print("Invalid input. Column and player must be numbers.")

if __name__ == "__main__":
    main()
