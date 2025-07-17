#!/usr/bin/env python3
"""
Connect 4 Analysis Tool Launcher
This script launches the Connect 4 Analysis GUI.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import numpy
        import PIL
        from PIL import Image, ImageTk
        return True
    except ImportError as e:
        return False, str(e)

def install_dependencies():
    """Attempt to install missing dependencies"""
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy", "pillow"])
        return True
    except Exception as e:
        return False, str(e)

def launch_app():
    """Launch the Connect 4 GUI application"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_dir = os.path.join(script_dir, "python")
    
    # Add the python directory to the path
    sys.path.insert(0, python_dir)
    
    try:
        from python.gui_app import Connect4GUI
        
        root = tk.Tk()
        app = Connect4GUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch application: {str(e)}")
        raise

if __name__ == "__main__":
    # Check for dependencies
    deps_result = check_dependencies()
    if deps_result is not True:
        print(f"Missing dependencies: {deps_result[1]}")
        print("Attempting to install required packages...")
        
        install_result = install_dependencies()
        if install_result is not True:
            print(f"Failed to install dependencies: {install_result[1]}")
            print("Please install manually with: pip install numpy pillow")
            sys.exit(1)
        else:
            print("Dependencies installed successfully!")
    
    # Launch the application
    launch_app()
