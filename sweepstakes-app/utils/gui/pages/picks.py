import tkinter as tk

from utils.gui.styling import *

class PicksPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_CARD)
        tk.Label(self, text="Field & Picks", font=("Segoe UI", 18, "bold"), bg=BG_CARD).pack(pady=20)
        StyledButton(self, "BACK", ACCENT_GREEN, lambda: controller.show_frame("HomePage")).pack(side="bottom", pady=20)
