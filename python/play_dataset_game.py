"""
Connect 4 Game with Dataset-based AI
This script demonstrates the Connect 4 game using the dataset-based AI.
"""

import time
import random
import math
from python.connect4 import ROWS, COLS, EMPTY, PLAYER_PIECE, AI_PIECE, create_board, drop_piece, is_valid_location, get_next_open_row, winning_move, print_board
from python.ai import get_ai_move
from python.dataset_ai import get_dataset_ai_move

def play_connect4():
    """Play a game of Connect 4 against the dataset-based AI."""
    board = create_board()
    game_over = False
    turn = random.choice([0, 1])  # 0 for Player, 1 for AI
    
    print("Welcome to Connect 4 with Dataset-based AI!")
    print("The AI is using a dataset of optimal Connect 4 positions.")
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
            
            # Use the dataset-based AI
            try:
                col, score = get_dataset_ai_move(board)
            except Exception as e:
                print(f"Error using dataset AI: {e}. Falling back to minimax.")
                col, score = get_ai_move(board, 5, -math.inf, math.inf, True)
                
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

if __name__ == "__main__":
    play_connect4()
