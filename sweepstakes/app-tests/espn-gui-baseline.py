# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------

# GUI --------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk, messagebox

# CORE -------------------------------------------------------------------------
import pandas as pd
import requests
import json
import re
from pathlib import Path
import openpyxl
import time
from datetime import date
import sys

# ------------------------------------------------------------------------------
# STYLING
# ------------------------------------------------------------------------------

BG_MAIN = "#e8f5e9"      # Very light green
BG_CARD = "#ffffff"      # White for frames
ACCENT_GREEN = "#2e7d32" # Dark Golf Green
ACCENT_BLUE = "#1565c0"  # Professional Blue
TEXT_COLOR = "#212121"
BTN_FONT = ("Segoe UI", 10, "bold")

# ------------------------------------------------------------------------------
# APPLICATION
# ------------------------------------------------------------------------------

class GolfSweepstakesApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Par-Perfect Sweepstakes Manager")
        self.geometry("1100x950")
        self.configure(bg=BG_MAIN)

        # SET APPLICATION ICON (Taskbar/Window Header)
        try:
            self.iconbitmap("app_icon.ico") 
        except:
            pass # Skips if file doesn't exist yet

        # --- Shared Data Variables ---
        self.tournament_name = tk.StringVar(value="The Masters")
        self.current_round = tk.StringVar(value="1")
        self.tournament_league = tk.StringVar(value="PGA Tour")
        self.tournament_id = tk.StringVar(value="12345")
        
        # --- Main Layout ---
        # 1. Top Header Area (Logo Space)
        self.header_frame = tk.Frame(self, bg=ACCENT_GREEN, height=100)
        self.header_frame.pack(side="top", fill="x")
        
        # LOGO PLACEHOLDER
        self.logo_label = tk.Label(self.header_frame, text="YOUR GOLF SOCIETY LOGO HERE", 
                                   fg="white", bg=ACCENT_GREEN, font=("Helvetica", 20, "italic bold"))
        self.logo_label.pack(pady=20)
        # To use a real image: 
        # self.logo_img = tk.PhotoImage(file="society_logo.png")
        # tk.Label(self.header_frame, image=self.logo_img, bg=ACCENT_GREEN).pack()

        # 2. Page Container
        self.container = tk.Frame(self, bg=BG_MAIN)
        self.container.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        page_list = (MainSettingsPage, ManagePlayersPage, AvailablePicksPage, 
                     ResultsPage, ScoresPage, ChartsPage)

        for F in page_list:
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainSettingsPage")

    def show_frame(self, page_name):
        self.frames[page_name].tkraise()

# --- CUSTOM BUTTON HELPER ---
def StyledButton(master, text, color, command, width=20):
    """Creates a consistent styled button"""
    return tk.Button(master, text=text, bg=color, fg="white", font=BTN_FONT,
                     activebackground=BG_MAIN, relief="flat", cursor="hand2",
                     width=width, command=command, padx=10, pady=5)

# --- MAIN CONTROL PANEL ---
class MainSettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_CARD, highlightbackground=ACCENT_GREEN, highlightthickness=2)
        self.controller = controller

        # Mock Database
        self.saved_tournaments = {
            "The Masters 2026": {"id": "AUG-26", "league": "PGA Tour", "round": "1"},
            "US Open 2026": {"id": "USO-26", "league": "USGA", "round": "1"}
        }

        tk.Label(self, text="🏆 Tournament Command Center", font=("Segoe UI", 22, "bold"), 
                 bg=BG_CARD, fg=ACCENT_GREEN).pack(pady=20)

        # 0. LOAD SECTION
        load_frame = tk.LabelFrame(self, text="Active Tournament", font=("Segoe UI", 10, "bold"),
                                   bg=BG_CARD, padx=20, pady=15, fg=ACCENT_GREEN)
        load_frame.pack(pady=10, fill="x", padx=40)

        self.load_var = tk.StringVar()
        dropdown = ttk.Combobox(load_frame, textvariable=self.load_var, state="readonly", width=40)
        dropdown['values'] = list(self.saved_tournaments.keys())
        dropdown.grid(row=0, column=0, padx=10)

        StyledButton(load_frame, "LOAD DATA", "#43a047", self.use_tournament, width=15).grid(row=0, column=1)

        # 1. FETCH SECTION
        fetch_frame = tk.LabelFrame(self, text=" Live Data Sync ", font=("Segoe UI", 10, "bold"),
                                    bg=BG_CARD, padx=20, pady=15, fg=ACCENT_BLUE)
        fetch_frame.pack(pady=10, fill="x", padx=40)

        self.source_var = tk.StringVar()
        src_drop = ttk.Combobox(fetch_frame, textvariable=self.source_var, state="readonly")
        src_drop['values'] = ("ESPN API")
        src_drop.current(0)
        src_drop.grid(row=0, column=0, padx=10)

        StyledButton(fetch_frame, "FETCH & PREVIEW", "#fb8c00", self.fetch_tournament_data, width=15).grid(row=0, column=1)

        # 2. SETTINGS GRID
        settings_frame = tk.Frame(self, bg=BG_CARD)
        settings_frame.pack(pady=20, fill="x", padx=40)

        fields = [
            ("Tournament Name:", controller.tournament_name, 0, 0),
            ("League:", controller.tournament_league, 0, 2),
            ("Round:", controller.current_round, 1, 0),
            ("Tournament ID:", controller.tournament_id, 1, 2)
        ]

        for (label, var, r, c) in fields:
            tk.Label(settings_frame, text=label, bg=BG_CARD, font=("Segoe UI", 9)).grid(row=r, column=c, sticky="w", pady=8)
            tk.Entry(settings_frame, textvariable=var, width=25, relief="solid", bd=1).grid(row=r, column=c+1, padx=10)

        # 3. CORE OPS
        ops_frame = tk.Frame(self, bg=BG_CARD)
        ops_frame.pack(pady=10)
        StyledButton(ops_frame, "⛳ GET ODDS", ACCENT_BLUE, None).grid(row=0, column=0, padx=10)
        StyledButton(ops_frame, "👥 GET PLAYERS", ACCENT_BLUE, None).grid(row=0, column=1, padx=10)
        StyledButton(ops_frame, "⛳ RUN ROUND", ACCENT_GREEN, None).grid(row=0, column=2, padx=10)

        # 4. NAVIGATION
        nav_frame = tk.LabelFrame(self, text=" Dashboards ", bg=BG_CARD, padx=10, pady=15)
        nav_frame.pack(pady=20, fill="x", padx=40)
        
        nav_btns = [
            ("Manage Players", "ManagePlayersPage", 0, 0),
            ("Available Picks", "AvailablePicksPage", 0, 1),
            ("Result Data", "ResultsPage", 0, 2),
            ("Player Scores", "ScoresPage", 1, 0),
            ("Scoreboard", "ChartsPage", 1, 1)
        ]

        for (txt, pg, r, c) in nav_btns:
            StyledButton(nav_frame, txt, "#546e7a", lambda p=pg: controller.show_frame(p)).grid(row=r, column=c, padx=10, pady=5)

        # EXIT
        StyledButton(self, "✖ EXIT SYSTEM", "#b71c1c", controller.quit, width=30).pack(pady=20)

    def use_tournament(self):
        selection = self.load_var.get()
        if selection in self.saved_tournaments:
            data = self.saved_tournaments[selection]
            self.controller.tournament_name.set(selection)
            self.controller.tournament_id.set(data['id'])
            self.controller.tournament_league.set(data['league'])
            self.controller.current_round.set(data['round'])
        else:
            messagebox.showwarning("Error", "Select a tournament first.")

    def fetch_tournament_data(self):
        if messagebox.askyesno("Sync", "Confirm data overwrite?"):
            self.controller.tournament_name.set("The Open")


class ManagePlayersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_CARD)
        tk.Label(self, text="Manage Participants", font=("Segoe UI", 18, "bold"), bg=BG_CARD, fg=ACCENT_GREEN).pack(pady=20)

        form_frame = tk.Frame(self, bg=BG_CARD)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Player Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1, columnspan=5, pady=5)

        tk.Label(form_frame, text="Prize Pool Group:").grid(row=1, column=0, sticky="w")
        self.prize_entry = tk.Entry(form_frame, width=40)
        self.prize_entry.grid(row=1, column=1, columnspan=5, pady=5)

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

        tk.Button(self, text="Back to Control Panel", command=lambda: controller.show_frame("MainSettingsPage")).pack(pady=10)

    def add_player(self):
        name = self.name_entry.get()
        group = self.prize_entry.get()
        picks = [cb.get() for cb in self.dropdowns]
        
        if name and group and all(picks):
            self.tree.insert("", "end", values=(name, group, *picks))
            self.name_entry.delete(0, tk.END)
            self.prize_entry.delete(0, tk.END)
            for cb in self.dropdowns: cb.set('')
        else:
            messagebox.showwarning("Input Error", "Please enter a name, group, and all 5 picks.")


class AvailablePicksPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_CARD)
        tk.Label(self, text="Field & Picks", font=("Segoe UI", 18, "bold"), bg=BG_CARD).pack(pady=20)
        StyledButton(self, "BACK", ACCENT_GREEN, lambda: controller.show_frame("MainSettingsPage")).pack(side="bottom", pady=20)

class ResultsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_CARD)
        tk.Label(self, text="Tournament Results", font=("Segoe UI", 18, "bold"), bg=BG_CARD).pack(pady=20)
        StyledButton(self, "BACK", ACCENT_GREEN, lambda: controller.show_frame("MainSettingsPage")).pack(side="bottom", pady=20)

class ScoresPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_CARD)
        tk.Label(self, text="Live Scores", font=("Segoe UI", 18, "bold"), bg=BG_CARD).pack(pady=20)
        StyledButton(self, "BACK", ACCENT_GREEN, lambda: controller.show_frame("MainSettingsPage")).pack(side="bottom", pady=20)

class ChartsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_CARD)
        tk.Label(self, text="Scoreboard & Analysis", font=("Segoe UI", 18, "bold"), bg=BG_CARD).pack(pady=20)
        StyledButton(self, "BACK", ACCENT_GREEN, lambda: controller.show_frame("MainSettingsPage")).pack(side="bottom", pady=20)

if __name__ == "__main__":
    app = GolfSweepstakesApp()
    app.mainloop()