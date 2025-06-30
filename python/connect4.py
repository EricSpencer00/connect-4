import math
import random

ROWS = 6
COLS = 7
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

def create_board():
    """Creates a new game board."""
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def drop_piece(board, row, col, piece):
    """Drops a piece onto the board."""
    board[row][col] = piece

def is_valid_location(board, col):
    """Checks if a column is a valid location to drop a piece."""
    return board[ROWS - 1][col] == EMPTY

def get_next_open_row(board, col):
    """Gets the next open row in a column."""
    for r in range(ROWS):
        if board[r][col] == EMPTY:
            return r
    return None

def winning_move(board, piece):
    """Checks if a player has a winning move."""
    # Check horizontal locations
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    # Check vertical locations
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    # Check positively sloped diagonals
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    # Check negatively sloped diagonals
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
    return False

def print_board(board):
    """Prints the game board."""
    for row in reversed(board):
        print(" ".join(map(str, row)))
    print("-" * (COLS * 2 - 1))

if __name__ == '__main__':
    from ai import get_ai_move

    board = create_board()
    game_over = False
    turn = random.choice([0, 1]) # 0 for Player, 1 for AI

    while not game_over:
        if turn == 0: # Player's turn
            print_board(board)
            try:
                col = int(input(f"Player 1, choose a column (0-{COLS - 1}): "))
                if 0 <= col < COLS and is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        print("Player 1 wins!")
                        game_over = True

                    turn = 1
                else:
                    print("Invalid move. Try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        else: # AI's turn
            col, _ = get_ai_move(board, 5, -math.inf, math.inf, True)
            if col is not None and is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)
                print(f"AI chose column {col}")

                if winning_move(board, AI_PIECE):
                    print_board(board)
                    print("AI wins!")
                    game_over = True

                turn = 0
            else: # No valid moves for AI
                game_over = True


        if all(board[ROWS-1][c] != EMPTY for c in range(COLS)):
            print("It's a draw!")
            game_over = True

    print_board(board)