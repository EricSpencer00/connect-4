"""
Connect 4 GUI Application
This module provides a graphical user interface for the Connect 4 game.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import numpy as np
import math
from PIL import Image, ImageTk

from connect4 import ROWS, COLS, EMPTY, PLAYER_PIECE, AI_PIECE, create_board, is_valid_location, get_next_open_row, drop_piece, winning_move
from ai import get_ai_move
from game_engine import evaluate_board_outcome, get_valid_locations, get_winning_positions

# Colors
BLUE = "#0080FF"
BLACK = "#000000"
RED = "#FF0000"
YELLOW = "#FFFF00"
WHITE = "#FFFFFF"
GREEN = "#00FF00"

class Connect4GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 Analysis")
        self.root.geometry("800x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#1E1E1E")
        
        # Game state
        self.board = create_board()
        self.game_over = False
        self.current_player = PLAYER_PIECE  # Player starts
        self.ai_thinking = False
        self.winning_positions = set()
        
        # Create frames
        self.create_frames()
        
        # Setup the UI components
        self.setup_ui()
        
        # Draw the initial board
        self.draw_board()
        
        # Start with evaluation
        self.evaluate_position()
    
    def create_frames(self):
        """Create the main UI frames"""
        # Top frame for controls
        self.control_frame = tk.Frame(self.root, bg="#2D2D2D", height=50)
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Center frame for the game board
        self.board_frame = tk.Frame(self.root, bg="#1E1E1E")
        self.board_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Bottom frame for evaluation and info
        self.info_frame = tk.Frame(self.root, bg="#2D2D2D", height=150)
        self.info_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def setup_ui(self):
        """Set up all the UI components"""
        # Control frame components
        self.setup_control_frame()
        
        # Board canvas
        self.setup_board_canvas()
        
        # Info frame components
        self.setup_info_frame()
    
    def setup_control_frame(self):
        """Set up the controls in the top frame"""
        # New Game button
        self.new_game_btn = tk.Button(
            self.control_frame, 
            text="New Game", 
            command=self.new_game,
            bg="#4B4B4B", 
            fg=WHITE,
            padx=10,
            font=("Arial", 12)
        )
        self.new_game_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Reset button
        self.reset_btn = tk.Button(
            self.control_frame, 
            text="Reset", 
            command=self.reset_board,
            bg="#4B4B4B", 
            fg=WHITE,
            padx=10,
            font=("Arial", 12)
        )
        self.reset_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # AI Move button
        self.ai_move_btn = tk.Button(
            self.control_frame, 
            text="AI Move", 
            command=self.make_ai_move,
            bg="#4B4B4B", 
            fg=WHITE,
            padx=10,
            font=("Arial", 12)
        )
        self.ai_move_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Depth selector
        self.depth_label = tk.Label(
            self.control_frame, 
            text="AI Depth:", 
            bg="#2D2D2D", 
            fg=WHITE,
            font=("Arial", 12)
        )
        self.depth_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.depth_var = tk.IntVar(value=5)
        self.depth_dropdown = ttk.Combobox(
            self.control_frame, 
            textvariable=self.depth_var,
            values=[3, 5, 7, 9],
            width=5,
            font=("Arial", 12)
        )
        self.depth_dropdown.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Evaluate button
        self.evaluate_btn = tk.Button(
            self.control_frame, 
            text="Analyze Position", 
            command=self.evaluate_position,
            bg="#4B4B4B", 
            fg=WHITE,
            padx=10,
            font=("Arial", 12)
        )
        self.evaluate_btn.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def setup_board_canvas(self):
        """Set up the game board canvas"""
        self.cell_size = min(700 // COLS, 500 // ROWS)
        canvas_width = COLS * self.cell_size
        canvas_height = (ROWS + 1) * self.cell_size  # Extra row for selection
        
        self.canvas = tk.Canvas(
            self.board_frame, 
            width=canvas_width, 
            height=canvas_height,
            bg=BLUE,
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)
        
        # Bind mouse events
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
    
    def setup_info_frame(self):
        """Set up the information panel"""
        # Left side - Text information
        self.info_left = tk.Frame(self.info_frame, bg="#2D2D2D")
        self.info_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.status_label = tk.Label(
            self.info_left,
            text="Current Status: Player's Turn",
            bg="#2D2D2D",
            fg=WHITE,
            font=("Arial", 14, "bold"),
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, pady=5)
        
        self.evaluation_label = tk.Label(
            self.info_left,
            text="Evaluation: Analyzing...",
            bg="#2D2D2D",
            fg=WHITE,
            font=("Arial", 12),
            anchor=tk.W
        )
        self.evaluation_label.pack(fill=tk.X, pady=5)
        
        self.move_label = tk.Label(
            self.info_left,
            text="Best Move: None",
            bg="#2D2D2D",
            fg=WHITE,
            font=("Arial", 12),
            anchor=tk.W
        )
        self.move_label.pack(fill=tk.X, pady=5)
        
        # Right side - Evaluation bar
        self.info_right = tk.Frame(self.info_frame, bg="#2D2D2D", width=200)
        self.info_right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        self.eval_canvas = tk.Canvas(
            self.info_right,
            width=200,
            height=100,
            bg="#1E1E1E",
            highlightthickness=0
        )
        self.eval_canvas.pack(pady=5)
        
        # Draw initial evaluation bar
        self.draw_evaluation_bar(0.5)  # Neutral position
    
    def draw_board(self):
        """Draw the game board on the canvas"""
        self.canvas.delete("all")
        
        # Draw the selection row
        self.draw_selection_row()
        
        # Draw the board and pieces
        for c in range(COLS):
            for r in range(ROWS):
                x = c * self.cell_size + self.cell_size // 2
                y = (r + 1) * self.cell_size + self.cell_size // 2  # +1 for selection row
                radius = self.cell_size // 2 - 5
                
                # Draw the empty slot
                self.canvas.create_oval(
                    x - radius, y - radius, 
                    x + radius, y + radius,
                    fill=WHITE,
                    outline=BLACK
                )
                
                # Draw pieces
                if self.board[r][c] == PLAYER_PIECE:
                    color = RED
                    if (r, c) in self.winning_positions:
                        color = GREEN  # Highlight winning pieces
                    self.canvas.create_oval(
                        x - radius, y - radius, 
                        x + radius, y + radius,
                        fill=color,
                        outline=BLACK
                    )
                elif self.board[r][c] == AI_PIECE:
                    color = YELLOW
                    if (r, c) in self.winning_positions:
                        color = GREEN  # Highlight winning pieces
                    self.canvas.create_oval(
                        x - radius, y - radius, 
                        x + radius, y + radius,
                        fill=color,
                        outline=BLACK
                    )
    
    def draw_selection_row(self):
        """Draw the top selection row"""
        radius = self.cell_size // 2 - 5
        
        for c in range(COLS):
            x = c * self.cell_size + self.cell_size // 2
            y = self.cell_size // 2
            
            # Skip if column is full
            if not is_valid_location(self.board, c):
                continue
                
            # Check if this is the column the mouse is over
            if hasattr(self, 'hover_col') and self.hover_col == c:
                if self.current_player == PLAYER_PIECE:
                    color = RED
                else:
                    color = YELLOW
                self.canvas.create_oval(
                    x - radius, y - radius, 
                    x + radius, y + radius,
                    fill=color,
                    outline=BLACK
                )
    
    def draw_evaluation_bar(self, position):
        """Draw the evaluation bar showing the current position assessment
        position: float from 0 to 1, where 0.5 is even, < 0.5 favors AI, > 0.5 favors player
        """
        self.eval_canvas.delete("all")
        
        width = 200
        height = 30
        
        # Draw background
        self.eval_canvas.create_rectangle(
            0, 0, width, height,
            fill="#1E1E1E",
            outline=""
        )
        
        # Determine bar position
        bar_width = int(position * width)
        
        # Draw AI side (yellow)
        self.eval_canvas.create_rectangle(
            0, 0, bar_width, height,
            fill=YELLOW,
            outline=""
        )
        
        # Draw Player side (red)
        self.eval_canvas.create_rectangle(
            bar_width, 0, width, height,
            fill=RED,
            outline=""
        )
        
        # Draw center line
        self.eval_canvas.create_line(
            width // 2, 0, width // 2, height,
            fill=WHITE,
            width=2
        )
        
        # Add labels
        self.eval_canvas.create_text(
            30, height + 15,
            text="AI",
            fill=YELLOW,
            font=("Arial", 12, "bold")
        )
        
        self.eval_canvas.create_text(
            width - 30, height + 15,
            text="Player",
            fill=RED,
            font=("Arial", 12, "bold")
        )
    
    def on_mouse_move(self, event):
        """Handle mouse movement over the canvas"""
        if self.game_over or self.ai_thinking:
            return
            
        col = event.x // self.cell_size
        if 0 <= col < COLS and is_valid_location(self.board, col):
            self.hover_col = col
            self.draw_board()
    
    def on_canvas_click(self, event):
        """Handle click on the canvas"""
        if self.game_over or self.ai_thinking:
            return
            
        col = event.x // self.cell_size
        if 0 <= col < COLS and is_valid_location(self.board, col):
            self.make_move(col)
    
    def make_move(self, col):
        """Make a move in the specified column"""
        if not is_valid_location(self.board, col):
            return
            
        # Get the next open row
        row = get_next_open_row(self.board, col)
        
        # Drop the piece
        drop_piece(self.board, row, col, self.current_player)
        
        # Clear winning positions if we're continuing the game
        self.winning_positions = set()
        
        # Update the board
        self.draw_board()
        
        # Check if the move is a winning move
        if winning_move(self.board, self.current_player):
            self.game_over = True
            winner = "Player" if self.current_player == PLAYER_PIECE else "AI"
            self.status_label.config(text=f"Game Over: {winner} wins!")
            self.winning_positions = get_winning_positions(self.board, self.current_player)
            self.draw_board()  # Redraw to highlight winning pieces
        elif len(get_valid_locations(self.board)) == 0:
            self.game_over = True
            self.status_label.config(text="Game Over: Draw!")
        else:
            # Switch player
            self.current_player = PLAYER_PIECE if self.current_player == AI_PIECE else AI_PIECE
            player_name = "Player" if self.current_player == PLAYER_PIECE else "AI"
            self.status_label.config(text=f"Current Status: {player_name}'s Turn")
            
            # If AI's turn, make a move
            if self.current_player == AI_PIECE and not self.game_over:
                self.root.after(500, self.make_ai_move)
        
        # Re-evaluate the position
        self.evaluate_position()
    
    def make_ai_move(self):
        """Make a move for the AI"""
        if self.game_over or self.ai_thinking:
            return
            
        self.ai_thinking = True
        self.status_label.config(text="AI is thinking...")
        
        # Start AI calculation in a separate thread
        def ai_thread_func():
            depth = self.depth_var.get()
            col, _ = get_ai_move(self.board, depth, -math.inf, math.inf, True)
            
            # Update the UI from the main thread
            self.root.after(0, lambda: self.complete_ai_move(col))
        
        threading.Thread(target=ai_thread_func).start()
    
    def complete_ai_move(self, col):
        """Complete the AI move with the chosen column"""
        self.ai_thinking = False
        
        if col is not None and is_valid_location(self.board, col):
            self.current_player = AI_PIECE
            self.make_move(col)
    
    def evaluate_position(self):
        """Evaluate the current board position"""
        if self.ai_thinking:
            return
            
        self.evaluation_label.config(text="Evaluation: Analyzing...")
        
        # Start evaluation in a separate thread
        def eval_thread_func():
            start_time = time.time()
            outcome, moves, winning_positions = evaluate_board_outcome(self.board, max_depth=self.depth_var.get())
            
            # Store winning positions for visualization
            self.winning_positions = winning_positions
            
            # Calculate evaluation value (0-1 scale)
            if outcome == "AI wins":
                eval_value = 0.1  # Strong advantage to AI
                eval_text = f"AI wins in {moves} moves" if moves else "AI wins"
            elif outcome == "Player wins":
                eval_value = 0.9  # Strong advantage to Player
                eval_text = f"Player wins in {moves} moves" if moves else "Player wins"
            elif outcome == "Draw":
                eval_value = 0.5  # Even
                eval_text = "Draw"
            elif outcome == "AI likely wins":
                eval_value = 0.3  # Advantage to AI
                eval_text = "AI has advantage"
            elif outcome == "Player likely wins":
                eval_value = 0.7  # Advantage to Player
                eval_text = "Player has advantage"
            else:
                # Use AI scoring as fallback
                from ai import score_position
                ai_score = score_position(self.board, AI_PIECE)
                player_score = score_position(self.board, PLAYER_PIECE)
                
                # Convert scores to evaluation percentage (0-1)
                total_score = max(1, abs(ai_score) + abs(player_score))
                eval_value = 0.5 + (ai_score - player_score) / (total_score * 4)  # Scale down the effect
                eval_value = max(0.2, min(0.8, eval_value))  # Limit range to avoid extremes
                
                if eval_value < 0.45:
                    eval_text = "AI has slight advantage"
                elif eval_value > 0.55:
                    eval_text = "Player has slight advantage"
                else:
                    eval_text = "Position is even"
            
            # Find best move recommendation
            if not self.game_over:
                best_col, _ = get_ai_move(self.board, self.depth_var.get(), -math.inf, math.inf, self.current_player == AI_PIECE)
                best_move_text = f"Best move: Column {best_col + 1}" if best_col is not None else "No good moves available"
            else:
                best_move_text = "Game over"
                
            analysis_time = time.time() - start_time
            
            # Update UI from main thread
            self.root.after(0, lambda: self.update_evaluation_ui(eval_value, eval_text, best_move_text, analysis_time))
        
        threading.Thread(target=eval_thread_func).start()
    
    def update_evaluation_ui(self, eval_value, eval_text, best_move_text, analysis_time):
        """Update the UI with evaluation results"""
        self.draw_evaluation_bar(eval_value)
        self.evaluation_label.config(text=f"Evaluation: {eval_text} (analysis: {analysis_time:.1f}s)")
        self.move_label.config(text=best_move_text)
        
        # Redraw board to show winning positions
        self.draw_board()
    
    def new_game(self):
        """Start a new game"""
        self.reset_board()
        self.current_player = PLAYER_PIECE  # Player starts
        self.status_label.config(text="Current Status: Player's Turn")
    
    def reset_board(self):
        """Reset the game board"""
        self.board = create_board()
        self.game_over = False
        self.winning_positions = set()
        self.draw_board()
        self.evaluate_position()
        self.status_label.config(text="Current Status: Player's Turn")


if __name__ == "__main__":
    root = tk.Tk()
    app = Connect4GUI(root)
    root.mainloop()
