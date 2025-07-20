"""
Connect 4 Position Analyzer
This module provides a dedicated analysis tool for Connect 4 positions.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math
import numpy as np
import logging
from PIL import Image, ImageTk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('connect4_analyzer')

from connect4 import ROWS, COLS, EMPTY, PLAYER_PIECE, AI_PIECE, create_board, is_valid_location, get_next_open_row, drop_piece, winning_move
from ai import score_position, get_ai_move
from game_engine import evaluate_board_outcome, get_valid_locations, get_winning_positions, find_winning_move
from evaluator import evaluate_mate_in_x

# Colors
BLUE = "#0080FF"
BLACK = "#000000"
RED = "#FF0000"
YELLOW = "#FFFF00"
WHITE = "#FFFFFF"
GREEN = "#00FF00"
LIGHT_GRAY = "#DDDDDD"
DARK_GRAY = "#333333"

class Connect4Analyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 Position Analyzer")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        self.root.configure(bg="#1E1E1E")
        
        # Game state
        self.board = create_board()
        self.game_over = False
        self.current_player = PLAYER_PIECE  # Red is default first player
        self.is_analyzing = False
        self.winning_positions = set()
        self.analysis_depth = 7  # Default analysis depth
        self.last_analysis_result = None
        self.mate_sequence = {}  # Dictionary to store mate sequence positions with move numbers
        
        # Create frames
        self.create_frames()
        
        # Setup the UI components
        self.setup_ui()
        
        # Set custom style for widgets
        self.setup_styles()
        
        # Draw the initial board
        self.draw_board()
        
        # Perform initial analysis
        self.analyze_position()
    
    def setup_styles(self):
        """Set up custom styles for Tkinter widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('TButton', 
                       background='#4B4B4B',
                       foreground='white',
                       font=('Arial', 12))
        
        # Configure the Combobox style
        style.configure('TCombobox', 
                       fieldbackground='#333333',
                       background='#4B4B4B',
                       foreground='white',
                       arrowcolor='white')
        
        # Configure the dropdown list style
        style.map('TCombobox',
                 fieldbackground=[('readonly', '#333333')],
                 selectbackground=[('readonly', '#555555')],
                 selectforeground=[('readonly', 'white')])
        
        # Configure the Notebook style
        style.configure('TNotebook', 
                       background='#1E1E1E',
                       tabmargins=[2, 5, 2, 0])
        
        style.configure('TNotebook.Tab', 
                       background='#2D2D2D',
                       foreground='white',
                       padding=[10, 2],
                       font=('Arial', 11))
        
        style.map('TNotebook.Tab',
                 background=[('selected', '#4B4B4B')],
                 foreground=[('selected', 'white')])
    
    def create_frames(self):
        """Create the main UI frames"""
        # Main frame
        self.main_frame = tk.Frame(self.root, bg="#1E1E1E")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for the board
        self.left_panel = tk.Frame(self.main_frame, bg="#1E1E1E")
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Board control frame (above the board)
        self.control_frame = tk.Frame(self.left_panel, bg="#2D2D2D", height=50)
        self.control_frame.pack(fill=tk.X, pady=5)
        
        # Board frame
        self.board_frame = tk.Frame(self.left_panel, bg="#1E1E1E")
        self.board_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Right panel for analysis
        self.right_panel = tk.Frame(self.main_frame, bg="#2D2D2D", width=350)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=5, pady=5)
    
    def setup_ui(self):
        """Set up all UI components"""
        # Set up the control panel
        self.setup_control_panel()
        
        # Set up the board canvas
        self.setup_board_canvas()
        
        # Set up the analysis panel
        self.setup_analysis_panel()
    
    def setup_control_panel(self):
        """Set up the board control panel"""
        # Reset button
        self.reset_btn = ttk.Button(
            self.control_frame, 
            text="Reset Board", 
            command=self.reset_board,
            style='TButton'
        )
        self.reset_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Toggle player button
        self.toggle_player_btn = ttk.Button(
            self.control_frame,
            text="Current Player: RED",
            command=self.toggle_current_player,
            style='TButton'
        )
        self.toggle_player_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Depth selector
        self.depth_label = tk.Label(
            self.control_frame, 
            text="Analysis Depth:", 
            bg="#2D2D2D", 
            fg=WHITE,
            font=("Arial", 12)
        )
        self.depth_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.depth_var = tk.IntVar(value=self.analysis_depth)
        self.depth_dropdown = ttk.Combobox(
            self.control_frame, 
            textvariable=self.depth_var,
            values=[4, 5, 6, 7, 8, 9, 10],
            width=5,
            font=("Arial", 12)
        )
        self.depth_dropdown.pack(side=tk.LEFT, padx=5, pady=10)
        self.depth_dropdown.bind("<<ComboboxSelected>>", lambda e: self.analyze_position())
        
        # Analyze button
        self.analyze_btn = ttk.Button(
            self.control_frame, 
            text="Analyze Position", 
            command=self.analyze_position,
            style='TButton'
        )
        self.analyze_btn.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def setup_board_canvas(self):
        """Set up the game board canvas"""
        self.cell_size = min(600 // COLS, 500 // ROWS)
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
    
    def setup_analysis_panel(self):
        """Set up the analysis panel on the right side"""
        # Analysis panel header
        header_frame = tk.Frame(self.right_panel, bg="#2D2D2D")
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(
            header_frame,
            text="Position Analysis",
            bg="#2D2D2D",
            fg=WHITE,
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=5)
        
        # Create a notebook (tabbed interface)
        self.analysis_notebook = ttk.Notebook(self.right_panel)
        self.analysis_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tab 1: Evaluation
        self.eval_tab = tk.Frame(self.analysis_notebook, bg="#2D2D2D")
        self.analysis_notebook.add(self.eval_tab, text="Evaluation")
        
        # Tab 2: Best Moves
        self.moves_tab = tk.Frame(self.analysis_notebook, bg="#2D2D2D")
        self.analysis_notebook.add(self.moves_tab, text="Best Moves")
        
        # Tab 3: Game Settings
        self.settings_tab = tk.Frame(self.analysis_notebook, bg="#2D2D2D")
        self.analysis_notebook.add(self.settings_tab, text="Game Mode")
        
        # Set up the evaluation tab
        self.setup_evaluation_tab()
        
        # Set up the best moves tab
        self.setup_best_moves_tab()
        
        # Set up the settings tab
        self.setup_settings_tab()
    
    def setup_evaluation_tab(self):
        """Set up the evaluation tab in the analysis panel"""
        # Status label
        self.status_label = tk.Label(
            self.eval_tab,
            text="Current Status: Analyzing...",
            bg="#2D2D2D",
            fg=WHITE,
            font=("Arial", 14, "bold"),
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Evaluation bar container
        eval_bar_frame = tk.Frame(self.eval_tab, bg="#2D2D2D")
        eval_bar_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Red player label
        self.red_label = tk.Label(
            eval_bar_frame,
            text="RED",
            bg="#2D2D2D",
            fg=RED,
            font=("Arial", 12, "bold")
        )
        self.red_label.pack(side=tk.TOP)
        
        # Evaluation bar
        self.eval_canvas = tk.Canvas(
            eval_bar_frame,
            width=300,
            height=30,
            bg="#1E1E1E",
            highlightthickness=1,
            highlightbackground="#4B4B4B"
        )
        self.eval_canvas.pack(pady=5)
        
        # Yellow player label
        self.yellow_label = tk.Label(
            eval_bar_frame,
            text="YELLOW",
            bg="#2D2D2D",
            fg=YELLOW,
            font=("Arial", 12, "bold")
        )
        self.yellow_label.pack(side=tk.BOTTOM)
        
        # Detailed evaluation info
        self.eval_details_frame = tk.Frame(self.eval_tab, bg="#2D2D2D")
        self.eval_details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Evaluation text
        self.evaluation_label = tk.Label(
            self.eval_details_frame,
            text="Evaluation: Analyzing position...",
            bg="#2D2D2D",
            fg=WHITE,
            font=("Arial", 12),
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=320
        )
        self.evaluation_label.pack(fill=tk.X, pady=5, anchor=tk.W)
        
        # Evaluation score
        self.eval_score_label = tk.Label(
            self.eval_details_frame,
            text="Score: 0.0",
            bg="#2D2D2D",
            fg=WHITE,
            font=("Arial", 12),
            anchor=tk.W
        )
        self.eval_score_label.pack(fill=tk.X, pady=5, anchor=tk.W)
        
        # Win probability
        self.win_prob_label = tk.Label(
            self.eval_details_frame,
            text="Win probability: 50%",
            bg="#2D2D2D",
            fg=WHITE,
            font=("Arial", 12),
            anchor=tk.W
        )
        self.win_prob_label.pack(fill=tk.X, pady=5, anchor=tk.W)
        
        # Forced mate info
        self.mate_label = tk.Label(
            self.eval_details_frame,
            text="No forced mate found",
            bg="#2D2D2D",
            fg=WHITE,
            font=("Arial", 12, "bold"),
            anchor=tk.W
        )
        self.mate_label.pack(fill=tk.X, pady=10, anchor=tk.W)
        
        # Analysis time
        self.analysis_time_label = tk.Label(
            self.eval_details_frame,
            text="Analysis time: 0.0s",
            bg="#2D2D2D",
            fg=LIGHT_GRAY,
            font=("Arial", 10),
            anchor=tk.W
        )
        self.analysis_time_label.pack(fill=tk.X, pady=5, anchor=tk.W)
        
        # Show detailed evaluation button
        self.detail_btn = ttk.Button(
            self.eval_details_frame,
            text="Show Detailed Evaluation",
            command=self.show_detailed_evaluation,
            style='TButton'
        )
        self.detail_btn.pack(pady=10)
    
    def setup_best_moves_tab(self):
        """Set up the best moves tab in the analysis panel"""
        # Container for moves
        moves_frame = tk.Frame(self.moves_tab, bg="#2D2D2D")
        moves_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Best move header
        best_move_label = tk.Label(
            moves_frame,
            text="Best Moves (by column):",
            bg="#2D2D2D",
            fg=WHITE,
            font=("Arial", 14, "bold"),
            anchor=tk.W
        )
        best_move_label.pack(fill=tk.X, pady=10)
        
        # Create a frame for the moves list
        moves_list_frame = tk.Frame(moves_frame, bg="#2D2D2D")
        moves_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Best moves list with scrollbar
        scrollbar = tk.Scrollbar(moves_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.moves_listbox = tk.Listbox(
            moves_list_frame,
            bg="#1E1E1E",
            fg=WHITE,
            font=("Arial", 12),
            selectbackground="#4B4B4B",
            highlightthickness=0,
            bd=0,
            height=15
        )
        self.moves_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure the scrollbar
        scrollbar.config(command=self.moves_listbox.yview)
        self.moves_listbox.config(yscrollcommand=scrollbar.set)
        
        # Bind listbox selection to make a move
        self.moves_listbox.bind("<<ListboxSelect>>", self.on_best_move_selected)
    
    def setup_settings_tab(self):
        """Set up the settings tab for game mode"""
        settings_frame = tk.Frame(self.settings_tab, bg="#2D2D2D")
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header for game mode
        game_mode_label = tk.Label(
            settings_frame,
            text="Game Mode Settings",
            bg="#2D2D2D",
            fg=WHITE,
            font=("Arial", 14, "bold"),
            anchor=tk.W
        )
        game_mode_label.pack(fill=tk.X, pady=10)
        
        # Game mode description
        description = tk.Label(
            settings_frame,
            text="Switch to game mode to play against the AI",
            bg="#2D2D2D",
            fg=WHITE,
            font=("Arial", 12),
            anchor=tk.W,
            wraplength=320,
            justify=tk.LEFT
        )
        description.pack(fill=tk.X, pady=10)
        
        # Switch to game mode button
        self.game_mode_btn = ttk.Button(
            settings_frame, 
            text="Switch to Game Mode", 
            command=self.switch_to_game_mode,
            style='TButton'
        )
        self.game_mode_btn.pack(pady=20)
    
    def draw_board(self):
        """Draw the game board on the canvas"""
        self.canvas.delete("all")
        
        # Draw the selection row
        self.draw_selection_row()
        
        # Draw the board and pieces
        for c in range(COLS):
            for r in range(ROWS):
                x = c * self.cell_size + self.cell_size // 2
                # Draw from bottom to top (ROWS-1-r) to match typical Connect 4 orientation
                y = ((ROWS-1-r) + 1) * self.cell_size + self.cell_size // 2  # +1 for selection row
                radius = self.cell_size // 2 - 5
                
                # Draw the empty slot
                self.canvas.create_oval(
                    x - radius, y - radius, 
                    x + radius, y + radius,
                    fill=WHITE,
                    outline=BLACK,
                    width=1
                )
                
                # Draw pieces
                if self.board[r][c] == PLAYER_PIECE:
                    # Check if this piece is part of a winning line
                    color = RED
                    if (r, c) in self.winning_positions:
                        color = GREEN  # Highlight winning pieces
                        # Draw a thicker outline for winning positions
                        self.canvas.create_oval(
                            x - radius - 2, y - radius - 2, 
                            x + radius + 2, y + radius + 2,
                            fill="",
                            outline=GREEN,
                            width=3
                        )
                        
                    # Draw the piece
                    self.canvas.create_oval(
                        x - radius, y - radius, 
                        x + radius, y + radius,
                        fill=color,
                        outline=BLACK,
                        width=1
                    )
                    
                    # Add move number if this is part of a forced win sequence
                    if hasattr(self, 'mate_sequence') and (r, c) in self.mate_sequence:
                        move_num = self.mate_sequence[(r, c)]
                        # Draw a background for the number to make it more visible
                        text_radius = radius // 2
                        self.canvas.create_oval(
                            x - text_radius, y - text_radius, 
                            x + text_radius, y + text_radius,
                            fill=WHITE,
                            outline=BLACK,
                            width=1
                        )
                        self.canvas.create_text(
                            x, y,
                            text=str(move_num),
                            font=("Arial", 12, "bold"),
                            fill=BLACK
                        )
                        
                elif self.board[r][c] == AI_PIECE:
                    # Check if this piece is part of a winning line
                    color = YELLOW
                    if (r, c) in self.winning_positions:
                        color = GREEN  # Highlight winning pieces
                        # Draw a thicker outline for winning positions
                        self.canvas.create_oval(
                            x - radius - 2, y - radius - 2, 
                            x + radius + 2, y + radius + 2,
                            fill="",
                            outline=GREEN,
                            width=3
                        )
                        
                    # Draw the piece
                    self.canvas.create_oval(
                        x - radius, y - radius, 
                        x + radius, y + radius,
                        fill=color,
                        outline=BLACK,
                        width=1
                    )
                    
                    # Add move number if this is part of a forced win sequence
                    if hasattr(self, 'mate_sequence') and (r, c) in self.mate_sequence:
                        move_num = self.mate_sequence[(r, c)]
                        # Draw a background for the number to make it more visible
                        text_radius = radius // 2
                        self.canvas.create_oval(
                            x - text_radius, y - text_radius, 
                            x + text_radius, y + text_radius,
                            fill=WHITE,
                            outline=BLACK,
                            width=1
                        )
                        self.canvas.create_text(
                            x, y,
                            text=str(move_num),
                            font=("Arial", 12, "bold"),
                            fill=BLACK
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
                
            # Draw selection indicator
            if hasattr(self, 'hover_col') and self.hover_col == c:
                if self.current_player == PLAYER_PIECE:
                    color = RED
                else:
                    color = YELLOW
                    
                self.canvas.create_oval(
                    x - radius, y - radius, 
                    x + radius, y + radius,
                    fill=color,
                    outline=BLACK,
                    width=1
                )
            
            # Indicate best move with a small arrow if we have analysis results
            if hasattr(self, 'last_analysis_result') and self.last_analysis_result:
                best_moves = self.last_analysis_result.get('best_moves', [])
                if best_moves and len(best_moves) > 0:
                    try:
                        # Get the column number of the best move (1-indexed)
                        best_col = int(best_moves[0].split(':')[0].strip()) - 1
                        
                        # If this is the best move column, draw an indicator
                        if c == best_col:
                            # Draw a small arrow pointing down
                            arrow_size = radius // 2
                            self.canvas.create_polygon(
                                x, y + radius + 5,  # Point
                                x - arrow_size, y - arrow_size + radius + 5,  # Left corner
                                x + arrow_size, y - arrow_size + radius + 5,  # Right corner
                                fill=GREEN,
                                outline=BLACK,
                                width=1
                            )
                    except (ValueError, IndexError):
                        pass
    
    def draw_evaluation_bar(self, eval_value):
        """Draw the evaluation bar with the given value (0-1 scale)"""
        self.eval_canvas.delete("all")
        
        # Get canvas dimensions
        width = self.eval_canvas.winfo_width() if self.eval_canvas.winfo_width() > 1 else 300
        height = self.eval_canvas.winfo_height() if self.eval_canvas.winfo_height() > 1 else 30
        
        # Calculate the red portion width
        red_width = int(width * eval_value)
        
        # Draw the red part (player advantage)
        self.eval_canvas.create_rectangle(
            0, 0, red_width, height,
            fill=RED, outline=""
        )
        
        # Draw the yellow part (AI advantage)
        self.eval_canvas.create_rectangle(
            red_width, 0, width, height,
            fill=YELLOW, outline=""
        )
        
        # Draw the center line if the evaluation is close to even
        if 0.45 <= eval_value <= 0.55:
            self.eval_canvas.create_line(
                width // 2, 0, width // 2, height,
                fill=WHITE, width=2
            )
    
    def on_mouse_move(self, event):
        """Handle mouse movement over the board"""
        if self.game_over or self.is_analyzing:
            return
            
        # Get the column from the x position
        col = event.x // self.cell_size
        
        # Ensure column is valid
        if 0 <= col < COLS and is_valid_location(self.board, col):
            self.hover_col = col
        else:
            self.hover_col = None
            
        # Redraw the board
        self.draw_board()
    
    def on_canvas_click(self, event):
        """Handle click on the board"""
        if self.game_over or self.is_analyzing:
            return
            
        # Get the column from the x position
        col = event.x // self.cell_size
        
        # Make a move if the column is valid
        if 0 <= col < COLS:
            self.make_move(col)
    
    def on_best_move_selected(self, event):
        """Handle selection of a move from the best moves list"""
        if not self.moves_listbox.curselection():
            return
            
        # Get the selected move
        selected_index = self.moves_listbox.curselection()[0]
        move_text = self.moves_listbox.get(selected_index)
        
        # Extract the column number
        try:
            col = int(move_text.split(":")[0].strip()) - 1  # Convert from 1-based to 0-based
            self.make_move(col)
        except (ValueError, IndexError):
            pass
    
    def make_move(self, col):
        """Make a move in the specified column"""
        if self.game_over or not is_valid_location(self.board, col):
            return
            
        # Get the next open row
        row = get_next_open_row(self.board, col)
        
        # Drop the piece
        drop_piece(self.board, row, col, self.current_player)
        
        # Check for a win
        if winning_move(self.board, self.current_player):
            self.game_over = True
            self.winning_positions = get_winning_positions(self.board, self.current_player)
            winner = "RED" if self.current_player == PLAYER_PIECE else "YELLOW"
            self.status_label.config(text=f"Game Over: {winner} wins!")
        
        # Check for a draw
        elif len(get_valid_locations(self.board)) == 0:
            self.game_over = True
            self.status_label.config(text="Game Over: Draw!")
        
        # Switch players
        else:
            self.current_player = AI_PIECE if self.current_player == PLAYER_PIECE else PLAYER_PIECE
            player_text = "RED" if self.current_player == PLAYER_PIECE else "YELLOW"
            self.toggle_player_btn.config(text=f"Current Player: {player_text}")
        
        # Redraw the board
        self.draw_board()
        
        # Analyze the new position
        self.analyze_position()
    
    def toggle_current_player(self):
        """Toggle the current player"""
        if self.is_analyzing:
            return
            
        self.current_player = AI_PIECE if self.current_player == PLAYER_PIECE else PLAYER_PIECE
        player_text = "RED" if self.current_player == PLAYER_PIECE else "YELLOW"
        self.toggle_player_btn.config(text=f"Current Player: {player_text}")
        
        # Update the UI
        self.draw_board()
        self.analyze_position()
    
    def reset_board(self):
        """Reset the game board"""
        self.board = create_board()
        self.game_over = False
        self.current_player = PLAYER_PIECE
        self.winning_positions = set()
        
        # Update UI elements
        self.toggle_player_btn.config(text="Current Player: RED")
        self.status_label.config(text="Current Status: Analyzing...")
        
        # Redraw the board
        self.draw_board()
        
        # Analyze the new position
        self.analyze_position()
    
    def analyze_position(self):
        """Analyze the current board position"""
        if self.is_analyzing:
            return
            
        self.is_analyzing = True
        self.status_label.config(text="Current Status: Analyzing...")
        self.evaluation_label.config(text="Evaluation: Analyzing position...")
        
        # Clear the moves list
        self.moves_listbox.delete(0, tk.END)
        
        # Start analysis in a separate thread
        threading.Thread(target=self.run_analysis).start()
    
    def run_analysis(self):
        """Run the position analysis in a background thread"""
        start_time = time.time()
        
        # Get the analysis depth
        depth = self.depth_var.get()
        logger.info(f"Starting analysis with depth {depth}")
        
        try:
            # Check for immediate win for either player
            player_col, player_row = find_winning_move(self.board, PLAYER_PIECE)
            ai_col, ai_row = find_winning_move(self.board, AI_PIECE)
            
            logger.info(f"Immediate win check - RED: {player_col is not None}, YELLOW: {ai_col is not None}")
            
            # Use the current player to determine who's turn it is
            current_text = "RED" if self.current_player == PLAYER_PIECE else "YELLOW"
            logger.info(f"Current player: {current_text}")
            
            # Initialize variables
            outcome = None
            moves = None
            winning_positions = set()
            eval_value = 0.5
            eval_text = "Position is even"
            score_text = "Score: 0.0"
            win_prob_text = "Win probability: 50%"
            mate_text = "No forced mate found"
            self.mate_sequence = {}  # Reset mate sequence
            
            # Check for immediate wins first
            if self.current_player == PLAYER_PIECE and player_col is not None:
                temp_board = [r[:] for r in self.board]
                drop_piece(temp_board, player_row, player_col, PLAYER_PIECE)
                winning_positions = get_winning_positions(temp_board, PLAYER_PIECE)
                outcome = "RED wins"
                moves = 1
                eval_value = 0.95
                eval_text = "RED wins in 1 move"
                score_text = "Score: +∞"
                win_prob_text = "Win probability: 100%"
                mate_text = "Mate in 1"
                # Add to mate sequence
                self.mate_sequence[(player_row, player_col)] = 1
                logger.info(f"RED has immediate win in column {player_col+1}")
            elif self.current_player == AI_PIECE and ai_col is not None:
                temp_board = [r[:] for r in self.board]
                drop_piece(temp_board, ai_row, ai_col, AI_PIECE)
                winning_positions = get_winning_positions(temp_board, AI_PIECE)
                outcome = "YELLOW wins"
                moves = 1
                eval_value = 0.05
                eval_text = "YELLOW wins in 1 move"
                score_text = "Score: -∞"
                win_prob_text = "Win probability: 0%"
                mate_text = "Mate in 1"
                # Add to mate sequence
                self.mate_sequence[(ai_row, ai_col)] = 1
                logger.info(f"YELLOW has immediate win in column {ai_col+1}")
            elif self.current_player == PLAYER_PIECE and ai_col is not None:
                # Yellow has a win, but it's Red's turn - need to block
                eval_value = 0.3
                eval_text = "YELLOW threatens to win - RED must block"
                score_text = "Score: -5.0"
                win_prob_text = "Win probability: 30%"
                logger.info(f"YELLOW threatens to win - RED must block in column {ai_col+1}")
            elif self.current_player == AI_PIECE and player_col is not None:
                # Red has a win, but it's Yellow's turn - need to block
                eval_value = 0.7
                eval_text = "RED threatens to win - YELLOW must block"
                score_text = "Score: +5.0"
                win_prob_text = "Win probability: 70%"
                logger.info(f"RED threatens to win - YELLOW must block in column {player_col+1}")
            else:
                # Do deeper analysis
                logger.info("No immediate wins found, performing deeper analysis")
                try:
                    # Use evaluate_mate_in_x for complete analysis
                    logger.info(f"Calling evaluate_mate_in_x with depth {depth}")
                    result, mate_moves, mate_sequence = evaluate_mate_in_x(self.board, max_depth=depth)
                    logger.info(f"evaluate_mate_in_x result: {result}, moves: {mate_moves}, sequence length: {len(mate_sequence)}")
                    
                    if result and mate_moves:
                        outcome = result
                        moves = mate_moves
                        
                        # Process the mate sequence to get winning positions and moves
                        if len(mate_sequence) > 0:
                            logger.info("Processing mate sequence")
                            # Set up a temporary board to follow the sequence
                            temp_board = [r[:] for r in self.board]
                            
                            # Track positions in the winning sequence
                            for move_num, (col, row, piece) in enumerate(mate_sequence):
                                # Skip moves that don't match the current player's turn pattern
                                if (move_num % 2 == 0 and piece != self.current_player) or \
                                   (move_num % 2 == 1 and piece == self.current_player):
                                    continue
                                    
                                # Add to the winning positions and mate sequence
                                if piece == self.current_player:
                                    winning_positions.add((row, col))
                                    self.mate_sequence[(row, col)] = move_num + 1
                                    
                                # Make the move on the temp board
                                drop_piece(temp_board, row, col, piece)
                            
                            logger.info(f"Processed mate sequence, found {len(winning_positions)} winning positions and {len(self.mate_sequence)} mate sequence positions")
                    
                    # If no conclusive result, try evaluate_board_outcome
                    if outcome is None or outcome == "Undetermined":
                        logger.info(f"Calling evaluate_board_outcome with depth {depth}")
                        outcome, moves, positions = evaluate_board_outcome(self.board, max_depth=depth)
                        winning_positions.update(positions)
                        logger.info(f"evaluate_board_outcome result: {outcome}, moves: {moves}, positions: {len(positions)}")
                        
                    # Set evaluation text and value based on outcome
                    if outcome == "AI wins" or outcome == "YELLOW wins":
                        eval_value = 0.1
                        eval_text = f"YELLOW wins in {moves} moves" if moves else "YELLOW wins"
                        score_text = f"Score: -{10 - moves if moves else 10}"
                        win_prob = max(0, 10 - moves * 2) if moves else 0
                        win_prob_text = f"Win probability: {win_prob}%"
                        mate_text = f"Mate in {moves}" if moves else "Checkmate"
                        logger.info(f"YELLOW wins in {moves} moves")
                        
                    elif outcome == "Player wins" or outcome == "RED wins":
                        eval_value = 0.9
                        eval_text = f"RED wins in {moves} moves" if moves else "RED wins"
                        score_text = f"Score: +{10 - moves if moves else 10}"
                        win_prob = min(100, 90 + moves * 1) if moves else 100
                        win_prob_text = f"Win probability: {win_prob}%"
                        mate_text = f"Mate in {moves}" if moves else "Checkmate"
                        logger.info(f"RED wins in {moves} moves")
                        
                    elif outcome == "Draw":
                        eval_value = 0.5
                        eval_text = "Position is drawn"
                        score_text = "Score: 0.0"
                        win_prob_text = "Win probability: 50%"
                        logger.info("Position is drawn")
                    elif outcome == "AI likely wins" or outcome == "YELLOW likely wins":
                        eval_value = 0.3
                        eval_text = "YELLOW has a significant advantage"
                        score_text = "Score: -3.0"
                        win_prob_text = "Win probability: 30%"
                        logger.info("YELLOW has a significant advantage")
                    elif outcome == "Player likely wins" or outcome == "RED likely wins":
                        eval_value = 0.7
                        eval_text = "RED has a significant advantage"
                        score_text = "Score: +3.0"
                        win_prob_text = "Win probability: 70%"
                        logger.info("RED has a significant advantage")
                    else:
                        # Use heuristic scoring
                        logger.info("No definitive outcome, using heuristic scoring")
                        ai_score = score_position(self.board, AI_PIECE)
                        player_score = score_position(self.board, PLAYER_PIECE)
                        score_diff = player_score - ai_score
                        
                        logger.info(f"Heuristic scores - RED: {player_score}, YELLOW: {ai_score}, diff: {score_diff}")
                        
                        # Convert to evaluation scale (0-1)
                        eval_value = 0.5 + score_diff / 100
                        eval_value = max(0.2, min(0.8, eval_value))
                        
                        score_display = f"+{score_diff/10:.1f}" if score_diff > 0 else f"{score_diff/10:.1f}"
                        score_text = f"Score: {score_display}"
                        
                        win_prob = int(eval_value * 100)
                        win_prob_text = f"Win probability: {win_prob}%"
                        
                        if eval_value < 0.4:
                            eval_text = "YELLOW has a slight advantage"
                        elif eval_value > 0.6:
                            eval_text = "RED has a slight advantage"
                        else:
                            eval_text = "Position is approximately equal"
                except Exception as e:
                    logger.error(f"Evaluation error: {e}")
                    # Fallback to simple scoring
                    ai_score = score_position(self.board, AI_PIECE)
                    player_score = score_position(self.board, PLAYER_PIECE)
                    score_diff = player_score - ai_score
                    
                    eval_value = 0.5 + score_diff / 100
                    eval_value = max(0.2, min(0.8, eval_value))
                    
                    score_display = f"+{score_diff/10:.1f}" if score_diff > 0 else f"{score_diff/10:.1f}"
                    score_text = f"Score: {score_display}"
                    
                    if eval_value < 0.4:
                        eval_text = "YELLOW has a slight advantage"
                    elif eval_value > 0.6:
                        eval_text = "RED has a slight advantage"
                    else:
                        eval_text = "Position is approximately equal"
                    
                    win_prob = int(eval_value * 100)
                    win_prob_text = f"Win probability: {win_prob}%"
            
            # Generate best moves list
            best_moves = self.generate_best_moves()
            
            # Calculate analysis time
            analysis_time = time.time() - start_time
            
            # Store the analysis results
            self.last_analysis_result = {
                'eval_value': eval_value,
                'eval_text': eval_text,
                'score_text': score_text,
                'win_prob_text': win_prob_text,
                'mate_text': mate_text,
                'winning_positions': winning_positions,
                'best_moves': best_moves,
                'analysis_time': analysis_time
            }
            
            # Update UI from main thread
            self.root.after(0, self.update_analysis_ui)
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            self.root.after(0, lambda: self.status_label.config(text=f"Analysis error: {str(e)}"))
            self.is_analyzing = False
    
    def generate_best_moves(self):
        """Generate a list of best moves with evaluations"""
        valid_locations = get_valid_locations(self.board)
        moves_evaluations = []
        
        for col in valid_locations:
            row = get_next_open_row(self.board, col)
            if row is not None:
                # Make the move
                temp_board = [r[:] for r in self.board]
                drop_piece(temp_board, row, col, self.current_player)
                
                # Check if this move wins
                if winning_move(temp_board, self.current_player):
                    moves_evaluations.append((col, 1000))  # Winning move gets highest score
                    continue
                
                # Otherwise evaluate the position
                try:
                    score = score_position(temp_board, self.current_player)
                    # Adjust score based on opponent's best response
                    next_player = AI_PIECE if self.current_player == PLAYER_PIECE else PLAYER_PIECE
                    best_col, best_score = get_ai_move(temp_board, 3, -math.inf, math.inf, next_player == AI_PIECE)
                    
                    # Combine scores
                    if self.current_player == PLAYER_PIECE:
                        adjusted_score = score - best_score/2
                    else:
                        adjusted_score = score - best_score/2
                        
                    moves_evaluations.append((col, adjusted_score))
                except Exception:
                    # If evaluation fails, use a basic score
                    moves_evaluations.append((col, score_position(temp_board, self.current_player)))
        
        # Sort moves by score (descending)
        moves_evaluations.sort(key=lambda x: x[1], reverse=True)
        
        # Format move strings
        formatted_moves = []
        for col, score in moves_evaluations:
            display_col = col + 1  # Convert to 1-based for display
            
            # Check if this move is a win
            if score == 1000:
                formatted_moves.append(f"{display_col}: Winning move!")
            else:
                # Format the score as a positive or negative number
                if score > 0:
                    score_str = f"+{score/10:.1f}"
                else:
                    score_str = f"{score/10:.1f}"
                    
                formatted_moves.append(f"{display_col}: {score_str}")
        
        return formatted_moves
    
    def update_analysis_ui(self):
        """Update the UI with analysis results"""
        if not self.last_analysis_result:
            self.is_analyzing = False
            return
            
        # Extract results
        eval_value = self.last_analysis_result['eval_value']
        eval_text = self.last_analysis_result['eval_text']
        score_text = self.last_analysis_result['score_text']
        win_prob_text = self.last_analysis_result['win_prob_text']
        mate_text = self.last_analysis_result['mate_text']
        winning_positions = self.last_analysis_result['winning_positions']
        best_moves = self.last_analysis_result['best_moves']
        analysis_time = self.last_analysis_result['analysis_time']
        
        # Update the evaluation bar
        self.draw_evaluation_bar(eval_value)
        
        # Update status based on current player
        current_text = "RED" if self.current_player == PLAYER_PIECE else "YELLOW"
        if self.game_over:
            if winning_move(self.board, PLAYER_PIECE):
                self.status_label.config(text="Game Over: RED wins!")
            elif winning_move(self.board, AI_PIECE):
                self.status_label.config(text="Game Over: YELLOW wins!")
            else:
                self.status_label.config(text="Game Over: Draw!")
        else:
            self.status_label.config(text=f"Current Player: {current_text}")
        
        # Update evaluation text
        self.evaluation_label.config(text=f"Evaluation: {eval_text}")
        self.eval_score_label.config(text=score_text)
        self.win_prob_label.config(text=win_prob_text)
        self.mate_label.config(text=mate_text)
        
        # Update analysis time
        self.analysis_time_label.config(text=f"Analysis time: {analysis_time:.2f}s")
        
        # Update winning positions
        self.winning_positions = winning_positions
        
        # Update best moves list
        self.moves_listbox.delete(0, tk.END)
        for move in best_moves:
            self.moves_listbox.insert(tk.END, move)
        
        # Redraw the board with any highlighted winning positions
        self.draw_board()
        
        # Mark analysis as complete
        self.is_analyzing = False
    
    def show_detailed_evaluation(self):
        """Display a popup with detailed evaluation information"""
        if not self.last_analysis_result:
            messagebox.showinfo("Detailed Evaluation", "No analysis results available yet.")
            return
            
        # Create a detailed explanation window
        explanation_window = tk.Toplevel(self.root)
        explanation_window.title("Detailed Evaluation")
        explanation_window.geometry("650x550")
        explanation_window.configure(bg="#1E1E1E")
        
        # Add a text widget to show the evaluation details
        explanation_text = tk.Text(
            explanation_window,
            wrap=tk.WORD,
            bg="#1E1E1E",
            fg=WHITE,
            font=("Arial", 12),
            padx=10,
            pady=10
        )
        explanation_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get basic info from last analysis
        eval_text = self.last_analysis_result['eval_text']
        score_text = self.last_analysis_result['score_text']
        win_prob_text = self.last_analysis_result['win_prob_text']
        mate_text = self.last_analysis_result['mate_text']
        
        # Create detailed explanation
        explanation = f"# Detailed Position Analysis\n\n"
        explanation += f"## Current Assessment\n"
        explanation += f"* {eval_text}\n"
        explanation += f"* {score_text}\n"
        explanation += f"* {win_prob_text}\n"
        
        if "mate" in mate_text.lower() and "no" not in mate_text.lower():
            explanation += f"* {mate_text}\n\n"
            explanation += f"## Mate Explanation\n"
            explanation += f"When we say '{mate_text}', this means that with perfect play, "
            explanation += f"{'RED' if 'RED wins' in eval_text else 'YELLOW'} can force a win "
            explanation += f"no matter what the opponent does.\n\n"
            
            # Explain the numbers on the board
            explanation += f"### Reading the Board\n"
            explanation += f"The numbers on the pieces show the forced winning sequence:\n"
            explanation += f"* Pieces with numbers show the optimal move order\n"
            explanation += f"* Green highlighted pieces form the winning line\n"
            explanation += f"* The opponent's best response moves are not numbered\n\n"
            
            explanation += f"This evaluation is based on a minimax search with alpha-beta pruning "
            explanation += f"which analyzed all possible responses to a depth of {self.depth_var.get()} plies.\n\n"
            explanation += f"For a mate to be detected:\n"
            explanation += f"1. Every possible response by the opponent must still lead to mate\n"
            explanation += f"2. The winning side must have a clear forced sequence of moves\n"
            explanation += f"3. The mate must be achievable within the search depth ({self.depth_var.get()} plies)\n\n"
            explanation += f"If the opponent can find any move that prevents the mate, "
            explanation += f"then the position would not be considered a forced win.\n"
        else:
            explanation += f"\n## Position Evaluation\n"
            explanation += f"The evaluation is based on several factors:\n"
            explanation += f"* Center control (pieces in the center columns are more valuable)\n"
            explanation += f"* Connected pieces (adjacent pieces of the same color)\n"
            explanation += f"* Threats (three in a row with open fourth spot)\n"
            explanation += f"* Overall piece positioning and potential winning lines\n\n"
            explanation += f"The depth of analysis was {self.depth_var.get()} plies "
            explanation += f"(a ply is a half-move: one player's turn).\n\n"
            explanation += f"If there is a discrepancy between what you see and the evaluation, "
            explanation += f"it might be because:\n"
            explanation += f"1. The search depth is limited (increase for more accuracy)\n"
            explanation += f"2. The forced win might be more moves ahead than the current search depth\n"
            explanation += f"3. The perfect play sequence is very specific and any deviation allows the opponent to equalize\n"
        
        # Show best moves with more detailed explanations
        explanation += f"\n## Best Moves\n"
        for i, move in enumerate(self.last_analysis_result.get('best_moves', [])[:3]):
            move_info = move.split(":")
            if len(move_info) >= 2:
                col_num = move_info[0].strip()
                score_info = move_info[1].strip()
                
                explanation += f"{i+1}. Column {col_num}: {score_info}\n"
                
                # Add more detailed explanation for the top move
                if i == 0 and "Winning" in score_info:
                    explanation += f"   This move leads to an immediate win.\n"
                elif i == 0 and float(score_info.replace("+", "")) > 3:
                    explanation += f"   This move gives a strong advantage.\n"
                elif i == 0:
                    explanation += f"   This is the best move in the current position.\n"
            else:
                explanation += f"{i+1}. {move}\n"
        
        # Add information about analysis parameters
        explanation += f"\n## Analysis Parameters\n"
        explanation += f"* Search depth: {self.depth_var.get()} plies\n"
        explanation += f"* Analysis time: {self.last_analysis_result['analysis_time']:.2f} seconds\n"
        explanation += f"* Current player: {'RED' if self.current_player == PLAYER_PIECE else 'YELLOW'}\n"
        
        # Insert the explanation into the text widget
        explanation_text.insert(tk.END, explanation)
        explanation_text.config(state=tk.DISABLED)  # Make read-only
        
        # Add a close button
        close_btn = ttk.Button(
            explanation_window,
            text="Close",
            command=explanation_window.destroy,
            style='TButton'
        )
        close_btn.pack(pady=10)
    
    def switch_to_game_mode(self):
        """Switch to game mode"""
        messagebox.showinfo("Game Mode", "Game mode will be implemented soon. Currently, the application is focused on position analysis.")
        # In a full implementation, this would launch the game mode interface

def main():
    root = tk.Tk()
    app = Connect4Analyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
