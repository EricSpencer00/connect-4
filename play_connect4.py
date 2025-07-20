#!/usr/bin/env python3
"""
Connect 4 Game with Switchable AI
This script allows playing Connect 4 with a choice between minimax AI or dataset-based AI.
"""

import time
import random
import math
import argparse
from python.connect4 import ROWS, COLS, EMPTY, PLAYER_PIECE, AI_PIECE, create_board, drop_piece, is_valid_location, get_next_open_row, winning_move, print_board
from python.ai import get_ai_move, DATASET_AI_AVAILABLE

# Import necessary modules
try:
    from python.dataset_ai import get_dataset_ai_move
    DATASET_AI_AVAILABLE = True
except ImportError:
    DATASET_AI_AVAILABLE = False

def get_best_move(board, ai_type, depth=5):
    """Get the best move using the specified AI type."""
    if ai_type == 'dataset' and DATASET_AI_AVAILABLE:
        return get_dataset_ai_move(board)
    else:
        # Fall back to minimax
        return get_ai_move(board, depth, -math.inf, math.inf, True)

def play_connect4(ai_type='auto', depth=5):
    """
    Play a game of Connect 4 against the selected AI.
    
    Args:
        ai_type: Type of AI to use ('minimax', 'dataset', or 'auto')
        depth: Depth for minimax search (ignored for dataset AI)
    """
    # Determine AI type
    if ai_type == 'auto':
        if DATASET_AI_AVAILABLE:
            ai_type = 'dataset'
            print("Using dataset-based AI (automatic selection)")
        else:
            ai_type = 'minimax'
            print("Using minimax AI (dataset AI not available)")
    else:
        if ai_type == 'dataset' and not DATASET_AI_AVAILABLE:
            print("Warning: Dataset AI not available. Falling back to minimax.")
            ai_type = 'minimax'
        print(f"Using {ai_type} AI")
    
    board = create_board()
    game_over = False
    turn = random.choice([0, 1])  # 0 for Player, 1 for AI
    
    print("Welcome to Connect 4!")
    print("Columns are numbered 0-6 from left to right.")
    print()
    
    while not game_over:
        if turn == 0:  # Player's turn
            print_board(board)
            try:
                col = int(input(f"Player 1, choose a column (0-{COLS - 1}): "))
                if 0 <= col < COLS and is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        print_board(board)
                        print("Player 1 wins!")
                        game_over = True

                    turn = 1
                else:
                    print("Invalid move. Try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        else:  # AI's turn
            print("AI is thinking...")
            start_time = time.time()
            col, score = get_best_move(board, ai_type, depth)
            end_time = time.time()
            
            if col is not None and is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)
                print(f"AI chose column {col} (took {end_time - start_time:.2f} seconds)")

                if winning_move(board, AI_PIECE):
                    print_board(board)
                    print("AI wins!")
                    game_over = True

                turn = 0
            else:  # No valid moves for AI
                print("AI could not find a valid move. Game over.")
                game_over = True

        if all(board[ROWS-1][c] != EMPTY for c in range(COLS)) and not game_over:
            print_board(board)
            print("It's a draw!")
            game_over = True

    print_board(board)
    print("Game over. Thanks for playing!")

def main():
    parser = argparse.ArgumentParser(description="Play Connect 4 with configurable AI")
    parser.add_argument('--ai', choices=['minimax', 'dataset', 'auto'], default='auto',
                       help='Type of AI to use (minimax, dataset, or auto)')
    parser.add_argument('--depth', type=int, default=5,
                       help='Depth for minimax search (ignored for dataset AI)')
    args = parser.parse_args()
    
    play_connect4(ai_type=args.ai, depth=args.depth)

if __name__ == "__main__":
    main()
