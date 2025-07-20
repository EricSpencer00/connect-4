# Connect 4 Solved Mode

Connect 4 is a mathematically solved game, meaning that with perfect play, the outcome of the game is known from any position. This document explains how the "Solved Mode" works in our Connect 4 implementation.

## What is Solved Mode?

The "Solved Mode" in our Connect 4 implementation uses a pre-computed dataset of optimal moves to ensure the AI plays perfectly. When this mode is enabled, the AI will:

1. Always win if a winning sequence is available
2. Always choose the best defensive move if it's in a losing position
3. Always play for a draw if it can't win

## The Connect 4 Dataset

The Connect 4 dataset used by our implementation was created by John Tromp and contains:

- 67,557 unique, legal 8-ply positions (4 moves by each player)
- Each position is labeled with the game-theoretic outcome (win, loss, or draw) with perfect play
- Dataset distribution: 44,473 wins (65.83%), 16,635 losses (24.62%), 6,449 draws (9.55%)

This dataset represents positions where neither player has won yet and the next move is not forced.

## How Solved Mode Works

When the "Solved Mode" is enabled, the AI decision-making process works as follows:

1. **Immediate Win Detection**: First check if there's an immediate winning move
2. **Blocking**: Check if the opponent has an immediate winning move that needs to be blocked
3. **Dataset Consultation**: Search the dataset for positions similar to the current board state
4. **Move Evaluation**: Evaluate potential moves based on the outcomes in the dataset
5. **Move Selection**: Choose the move with the highest probability of leading to a win or draw

## Technical Implementation

The dataset-based AI is implemented in the `dataset_ai.py` module. Key functions include:

- `map_board_to_dataset_format()`: Converts the internal board representation to the dataset format
- `find_matching_positions()`: Finds positions in the dataset similar to the current board
- `get_best_move_from_dataset()`: Determines the optimal move based on dataset analysis

For performance reasons, the implementation uses a subset of the dataset and optimized similarity calculations.

## Limitations

While the "Solved Mode" aims to play perfect Connect 4, there are some limitations:

1. The dataset covers 8-ply positions, so very deep positions might not be found exactly in the dataset
2. The implementation uses similarity matching, which may not always find the exact optimal move
3. Performance optimizations mean we use a subset of the dataset for quicker response times

Despite these limitations, the "Solved Mode" plays at a very high level and should provide a strong challenge for most players.

## Using Solved Mode

To enable "Solved Mode":

1. Check the "Solved Mode" checkbox in the game interface
2. Or launch the game with solved mode enabled by default:
   ```
   python play_solved_connect4.py
   ```

When playing with "Solved Mode" enabled, the game interface will display "Solved Mode Active" in the status bar to remind you that you're playing against the dataset-based AI.

## Can You Beat Perfect Play?

Connect 4 is a first-player win with perfect play, which means if you go first and play perfectly, you should win. However, finding the perfect moves is extremely difficult for humans. If the AI goes first in "Solved Mode", it should never lose with perfect play.

Challenge yourself to see if you can beat the perfect AI!
