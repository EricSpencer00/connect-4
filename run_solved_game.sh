#!/bin/bash
# Run Connect 4 in Solved Mode

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python is not installed. Please install Python 3.x"
    exit 1
fi

# Check if the dataset file exists
if [ ! -f "c4-dataset/connect-4.data.Z" ]; then
    echo "Dataset file not found. Please ensure the dataset is properly installed."
    echo "It should be located at: c4-dataset/connect-4.data.Z"
    exit 1
fi

# Run the game
echo "Starting Connect 4 with Solved Mode..."
python play_solved_connect4.py

# Exit with the same code as the Python process
exit $?
