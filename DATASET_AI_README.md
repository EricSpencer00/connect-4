# Connect 4 with Dataset-based AI

This project implements a Connect 4 game with an AI opponent that uses a pre-solved dataset to make optimal moves.

## About the Dataset

The Connect 4 dataset contains all legal 8-ply positions in the game of Connect 4 in which neither player has won yet, and in which the next move is not forced. This dataset was originally compiled by John Tromp.

The dataset contains 67,557 positions with their outcomes (win, loss, or draw).

## Running the Game

You can play against the dataset-based AI by running:

```bash
cd python
python play_dataset_game.py
```

The AI will make decisions based on the Connect 4 dataset, which contains optimal moves for various board positions.

## Technical Details

### AI Implementation

The AI implements two approaches:

1. **Dataset-based AI**: Uses the Connect 4 dataset to find similar positions and determine the best move based on known outcomes.
2. **Minimax with Alpha-Beta Pruning**: Used as a fallback if the dataset-based approach encounters any issues.

The dataset-based AI:
- Checks for immediate winning moves
- Checks for blocking opponent's winning moves
- Searches the dataset for similar positions
- Evaluates potential moves based on known outcomes
- Selects the move with the highest probability of winning

For performance reasons, the AI uses a subset of the full dataset (10,000 positions out of 67,557).

### Dataset Format

The dataset represents board positions as a list of 42 cells (6 rows × 7 columns), where:
- 'x' represents player's pieces
- 'o' represents AI's pieces
- 'b' represents empty spaces

Each position has an associated outcome:
- 'win' indicates the first player can force a win
- 'loss' indicates the first player will lose with optimal play
- 'draw' indicates the game will end in a draw with optimal play

## Future Improvements

Potential future improvements:
- Precompute and cache common opening moves
- Use machine learning to improve position evaluation
- Optimize dataset searching for faster move selection

Enjoy playing against the dataset-based AI!
