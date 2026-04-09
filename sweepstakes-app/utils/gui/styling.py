# Imports ----------------------------------------------------------------------

import tkinter as tk

# Constants --------------------------------------------------------------------

BG_MAIN = "#e8f5e9"      # Very light green
BG_CARD = "#ffffff"      # White for frames
ACCENT_GREEN = "#2e7d32" # Dark Golf Green
ACCENT_BLUE = "#1565c0"  # Professional Blue
ACCENT_RED = "#c01515"  # Professional Red
TEXT_COLOR = "#212121"
BTN_FONT = ("Segoe UI", 10, "bold")

# Buttons ----------------------------------------------------------------------

def StyledButton(master, text, color, command, width=20):
    # Creates a consistent styled button
    return tk.Button(master, text=text, bg=color, fg="white", font=BTN_FONT,
                     activebackground=BG_MAIN, relief="flat", cursor="hand2",
                     width=width, command=command, padx=10, pady=5)

# End --------------------------------------------------------------------------