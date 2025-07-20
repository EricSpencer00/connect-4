#!/usr/bin/env python3
"""
Connect 4 Solved Game Launcher
This script launches the Connect 4 game with the dataset-based AI (solved mode) enabled by default.
"""

import os
import sys
import tkinter as tk

# First check if the dataset is available
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(current_dir, 'c4-dataset', 'connect-4.data.Z')
if not os.path.exists(dataset_path):
    print(f"Error: Dataset file not found at {dataset_path}")
    print("Please ensure the dataset is properly installed.")
    sys.exit(1)

# Import the GUI
try:
    from python.gui_app import Connect4GUI, DATASET_AI_AVAILABLE
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you have all dependencies installed by running:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def main():
    """Main function to launch the Connect 4 game with solved mode."""
    # Create the root window
    root = tk.Tk()
    
    # Create the game interface
    app = Connect4GUI(root)
    
    # Enable solved mode by default if available
    if hasattr(app, 'solved_mode_var'):
        if DATASET_AI_AVAILABLE:
            app.solved_mode_var.set(True)
            app.on_solved_mode_toggle()  # Trigger the toggle handler
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
