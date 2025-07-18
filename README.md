# Connect 4 Analysis Tool

This is a comprehensive Connect 4 game and analysis tool that can determine the winner from any position in a Connect 4 game. The application includes:

1. **Connect 4 Game Engine**: A powerful engine that can predict the outcome of any Connect 4 position with perfect play.
2. **Position Analysis**: Ability to analyze positions and determine forced wins.
3. **Graphical User Interface**: An interactive GUI for playing against the AI and analyzing positions.

## Mathematical Complexity

Connect 4 is a solved game with first-player win (with perfect play). Some key metrics:
- Standard board: 7 columns × 6 rows
- Total possible positions: ~4.5 trillion
- Legal positions reachable in gameplay: ~4.5 billion
- First solved by Victor Allis (1988) and independently by John Tromp (1995)

## Features

- Play against an AI with adjustable difficulty
- Analyze any position to determine the expected outcome with perfect play
- Visual representation of winning lines and forced sequences
- Evaluation bar showing the advantage for either player
- Detection of "mate in X" sequences

## Structure

- `python/` - Python implementation of the Connect 4 game and AI
  - `connect4.py` - Core game logic and rules
  - `ai.py` - AI implementation using minimax with alpha-beta pruning
  - `evaluator.py` - Position evaluation and mate detection
  - `game_engine.py` - Enhanced engine for position analysis
  - `gui_app.py` - Graphical user interface

- Additional theoretical implementations:
  - `Connect4.tla` - TLA+ specification for formal verification
  - `Connect4.v` - Coq implementation for theorem proving

## Getting Started

1. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

2. Install tkinter (if not included with your Python installation):
   - On macOS: `brew install python-tk@3.11`
   - On Ubuntu/Debian: `sudo apt-get install python3-tk`
   - On Windows: Tkinter comes with the standard Python installation

3. Run the GUI application:
   ```
   cd python
   python gui_app.py
   ```

## Mathematical Approach

The tool uses several computational approaches:
1. Minimax algorithm with alpha-beta pruning
2. Enhanced evaluation function
3. Mate detection
4. Forced sequence detection

## License

MIT License