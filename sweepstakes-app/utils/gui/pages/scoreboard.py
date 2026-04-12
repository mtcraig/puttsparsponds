import tkinter as tk

from utils.gui.styling import *

class ScoreboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_CARD, highlightbackground=ACCENT_GREEN, highlightthickness=2)
        tk.Label(self, text="Scoreboard & Analysis", font=("Segoe UI", 18, "bold"), bg=BG_CARD, fg=ACCENT_GREEN).pack(pady=20)
        StyledButton(self, "BACK", ACCENT_GREEN, lambda: controller.show_frame("HomePage")).pack(side="bottom", pady=20)
