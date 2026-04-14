import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd
import json
from pathlib import Path

from utils.gui.styling import *
from utils.data.tourns import load_tournaments, use_tournament, search_tournament, latest_tournament, fetch_athlete_data
from utils.data.log import new_session

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        new_session()
        super().__init__(parent, bg=BG_CARD, highlightbackground=ACCENT_GREEN, highlightthickness=2)
        self.controller = controller

        # 0. LOAD DATA FROM FILE (Replacing Mock Database)
        self.all_tournaments_df = pd.DataFrame()
        load_tournaments(self)

        tk.Label(self, text="🏆 Sweepstakes Manager", font=("Segoe UI", 22, "bold"), 
                 bg=BG_CARD, fg=ACCENT_GREEN).pack(pady=20)

        # 0. LOAD SECTION
        load_frame = tk.LabelFrame(self, text=" Saved Tournaments ", font=("Segoe UI", 10, "bold"),
                                   bg=BG_CARD, padx=20, pady=15, fg=ACCENT_GREEN)
        load_frame.pack(pady=10, fill="x", padx=40)

        self.load_var = tk.StringVar()
        dropdown = ttk.Combobox(load_frame, textvariable=self.load_var, state="readonly", width=40)
        dropdown['values'] = list(self.saved_tournaments)
        dropdown.pack(side="left", padx=10)

        StyledButton(load_frame, "⬆ LOAD DATA", "#43a047", lambda: use_tournament(self), width=15).pack(side="right", padx=10)

        # 1. FETCH SECTION
        fetch_frame = tk.LabelFrame(self, text=" ESPN Tournament Search ", font=("Segoe UI", 10, "bold"),
                                    bg=BG_CARD, padx=20, pady=15, fg=ACCENT_RED)
        fetch_frame.pack(pady=10, fill="x", padx=40)

        tk.Label(fetch_frame, text="Tournament League::", bg=BG_CARD, font=("Segoe UI", 9)).pack(side="left", padx=10)
        src_combo = ttk.Combobox(fetch_frame, textvariable=self.controller.tournament_league, state="readonly", width=25)
        src_combo['values'] = ["PGA", "LIV"]
        src_combo.pack(side="left", padx=10)

        tk.Label(fetch_frame, text="Tournament ID:", bg=BG_CARD, font=("Segoe UI", 9)).pack(side="left", padx=10)
        search_entry = tk.Entry(fetch_frame, textvariable=self.controller.tournament_id, width=25, relief="solid", bd=1)
        search_entry.value = ""
        search_entry.pack(side="left", padx=10)
        
        StyledButton(fetch_frame, "⭐ GET LATEST", "#fb8c00", lambda: latest_tournament(self), width=15).pack(side="right", padx=10)

        StyledButton(fetch_frame, "🔎 SEARCH", "#fb8c00", lambda: search_tournament(self), width=15).pack(side="right", padx=10)

        settings_frame = tk.LabelFrame(self, text=" Current Tournament Settings", font=("Segoe UI", 10, "bold"),
                                    bg=BG_CARD, padx=20, pady=15, fg=ACCENT_BLUE)
        settings_frame.pack(pady=20, fill="x", padx=40)

        fields = [
            ("Tournament Name:", controller.tournament_name, 0, 0),
            ("League:", controller.tournament_league, 0, 2),
            ("Round:", controller.current_round, 1, 0),
            ("Tournament ID:", controller.tournament_id, 1, 2)
        ]

        for (label, var, r, c) in fields:
            tk.Label(settings_frame, text=label, bg=BG_CARD, font=("Segoe UI", 9)).grid(row=r, column=c, sticky="w", pady=8)
            tk.Entry(settings_frame, textvariable=var, width=40, relief="solid", bd=1).grid(row=r, column=c+1, padx=10)

        # 3. CORE OPS
        ops_frame = tk.LabelFrame(self, text=" API Calls ", font=("Segoe UI", 10, "bold"),
                                    bg=BG_CARD, padx=20, pady=15, fg=ACCENT_BLUE)
        ops_frame.pack(pady=20, fill="x", padx=40)
        StyledButton(ops_frame, "⛳ GET ODDS", ACCENT_BLUE, None).grid(row=0, column=0, sticky="ew", padx=10)
        StyledButton(ops_frame, "👥 GET ENTRANTS", ACCENT_BLUE, lambda: fetch_athlete_data(self.controller.tournament_league.get().lower(),self.controller.tournament_id.get(),self.controller.tournament_name.get())).grid(row=0, column=1, sticky="ew", padx=10)
        StyledButton(ops_frame, "⛳ RUN ROUND", ACCENT_GREEN, None).grid(row=0, column=2, sticky="ew", padx=10)

        # 2. Tell the frame to give equal weight to all three columns
        # This forces them to expand and fill the entire width of ops_frame
        ops_frame.grid_columnconfigure(0, weight=1)
        ops_frame.grid_columnconfigure(1, weight=1)
        ops_frame.grid_columnconfigure(2, weight=1)

        # 3. Ensure the ops_frame itself is stretching across the page
        ops_frame.pack(pady=10, fill="x", padx=40)

        # 4. NAVIGATION
        nav_frame = tk.LabelFrame(self, text=" Navigation", font=("Segoe UI", 10, 
                                                                 "bold"),
                                    bg=BG_CARD, padx=20, pady=15, fg=ACCENT_BLUE)
        nav_frame.pack(pady=20, fill="x", padx=40)
        
        nav_btns = [
            ("Manage Players", "ManagePlayersPage", 0, 0),
            ("Available Picks", "PicksPage", 0, 1),
            ("Result Data", "ResultsPage", 0, 2),
            ("Player Scores", "ScoresPage", 1, 0),
            ("Scoreboard", "ScoreboardPage", 1, 1),
            ("Settings", "SettingsPage", 1, 2)
        ]

        for (txt, pg, r, c) in nav_btns:
            StyledButton(nav_frame, txt, "#546e7a", lambda p=pg: controller.show_frame(p)).grid(row=r, column=c, sticky="ew", padx=10, pady=5)
            nav_frame.grid_columnconfigure(c, weight=1)

        # EXIT
        StyledButton(self, "✖ EXIT", "#b71c1c", controller.quit, width=30).pack(pady=20)