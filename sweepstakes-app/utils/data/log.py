import pandas as pd
import json
from pathlib import Path
import logging

def new_session():
    # Generates a new log file for the current session
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True) # Ensure logs directory exists
    # Setup configuration
    logging.basicConfig(
        filename=logs_dir / 'session.log', 
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def add_session_entry(message):
    logging.info(message)

def get_session_history():
    try:
        with open('session.log', 'r') as f:
            return f.readlines() # Returns logs as a list of lines
    except FileNotFoundError:
        return []

# Example Usage:
# add_session_entry("Session started.")
# history = get_session_history()
# for line in history:
#     print(line.strip())