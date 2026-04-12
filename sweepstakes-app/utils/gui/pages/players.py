import tkinter as tk
from tkinter import ttk, messagebox

from utils.gui.styling import *

class ManagePlayersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_CARD, highlightbackground=ACCENT_GREEN, highlightthickness=2)
        tk.Label(self, text="Manage Participants", font=("Segoe UI", 18, "bold"), bg=BG_CARD, fg=ACCENT_GREEN).pack(pady=20)

        form_frame = tk.Frame(self, bg=BG_CARD)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Player Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1, columnspan=5, pady=5)

        tk.Label(form_frame, text="Prize Pool Group:").grid(row=1, column=0, sticky="w")
        prize_options = ["PPP", "External"]
        self.prize_combo = ttk.Combobox(form_frame, width=37, values=prize_options, state="readonly")
        self.prize_combo.grid(row=1, column=1, columnspan=5, pady=5)
        self.prize_combo.current(0)

        self.dropdowns = []
        options = ["Golfer A", "Golfer B", "Golfer C", "Golfer D"]

        tk.Label(form_frame, text="Selections:").grid(row=2, column=0, sticky="w")
        for i in range(5):
            cb = ttk.Combobox(form_frame, values=options, width=12)
            cb.grid(row=2, column=i+1, padx=2, pady=10)
            self.dropdowns.append(cb)

        tk.Button(self, text="Add Player to List", bg="#2ecc71", command=self.add_player).pack(pady=5)

        self.tree = ttk.Treeview(self, columns=("Name", "Group", "P1", "P2", "P3", "P4", "P5"), show="headings", height=8)
        headers = ("Name", "Group", "P1", "P2", "P3", "P4", "P5")
        for col in headers:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)
        self.tree.pack(pady=10, padx=20, fill="both")

        StyledButton(self, "BACK", ACCENT_GREEN, lambda: controller.show_frame("HomePage")).pack(side="bottom", pady=20)

    def add_player(self):
        name = self.name_entry.get()
        group = self.prize_combo.get()
        picks = [cb.get() for cb in self.dropdowns]
        
        if name and group and all(picks):
            self.tree.insert("", "end", values=(name, group, *picks))
            self.name_entry.delete(0, tk.END)
            self.prize_combo.delete(0, tk.END)
            for cb in self.dropdowns: cb.set('')
        else:
            messagebox.showwarning("Input Error", "Please enter a name, group, and all 5 picks.")