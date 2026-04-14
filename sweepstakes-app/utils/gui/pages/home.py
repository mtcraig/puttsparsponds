#----|----1----|----2----|----3----|----4----|----5----|----6----|----7----|----8

import tkinter as tk
from tkinter import ttk
import pandas as pd
from utils.gui.styling import *
from utils.data.tourns import (load_tournaments,
                               use_tournament,
                               search_tournament,
                               latest_tournament,
                               fetch_athlete_data)
from utils.data.log import new_session

class HomePage(tk.Frame):

    def __init__(self, parent, controller):

        # Session Logging - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        new_session()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        super().__init__(parent, bg=BG_CARD,
                         highlightbackground=ACCENT_GREEN, highlightthickness=2)
        self.controller = controller

        # Initial load of saved tournaments - - - - - - - - - - - - - - - - - - -
        self.all_tournaments_df = pd.DataFrame()
        load_tournaments(self)

        tk.Label(self, text="🏆 Sweepstakes Manager",
                       font=("Segoe UI", 22, "bold"), 
                       bg=BG_CARD, fg=ACCENT_GREEN
                       ).pack(pady=20)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Saved Tournaments - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - Header
        load_frame = StyledFrame(self,"Saved Tournaments",ACCENT_GREEN)
        load_frame.pack(pady=20, fill="x", padx=40)

        # - Choose from saved tournaments
        self.load_var = tk.StringVar()
        dropdown = ttk.Combobox(load_frame, textvariable=self.load_var,
                                            state="readonly", width=40)
        dropdown['values'] = list(self.saved_tournaments)
        dropdown.pack(side="left", padx=10)

        StyledButton(load_frame, "⬆ LOAD DATA", "#43a047",
                     lambda: use_tournament(self),
                     width=15).pack(side="right", padx=10)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Tournament Search - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - Header
        fetch_frame = StyledFrame(self,"ESPN Tournament Search",ACCENT_RED)
        fetch_frame.pack(pady=20, fill="x", padx=40)

        # - League Dropdown
        tk.Label(fetch_frame, text="League:",
                 bg=BG_CARD, font=("Segoe UI", 9)
                 ).pack(side="left", padx=10)
        src_combo = ttk.Combobox(fetch_frame,
                                 textvariable=self.controller.tournament_league,
                                 state="readonly", width=25)
        src_combo.pack(side="left", padx=10)
        src_combo['values'] = ["PGA", "LIV"]
        src_combo.current(0)

        # - ID Entry
        tk.Label(fetch_frame, text="ID:",
                 bg=BG_CARD, font=("Segoe UI", 9)
                 ).pack(side="left", padx=10)
        search_entry = tk.Entry(fetch_frame,
                                textvariable=self.controller.tournament_id,
                                width=25, relief="solid", bd=1)
        search_entry.pack(side="left", padx=10)
        search_entry.value = ""
        
        # - Buttons
        StyledButton(fetch_frame, "⭐ GET LATEST", "#fb8c00",
                     lambda: latest_tournament(self),
                     width=15).pack(side="right", padx=10)

        StyledButton(fetch_frame, "🔎 SEARCH", "#fb8c00",
                     lambda: search_tournament(self),
                     width=15).pack(side="right", padx=10)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Tournament Settings - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - Header
        settings_frame = StyledFrame(self,"Current Tournament Settings",ACCENT_BLUE)
        settings_frame.pack(pady=20, fill="x", padx=40)

        # - Current Session Fields
        fields = [
            ("Tournament Name:", controller.tournament_name, 0, 0),
            ("League:", controller.tournament_league, 0, 2),
            ("Round:", controller.current_round, 1, 0),
            ("Tournament ID:", controller.tournament_id, 1, 2)
        ]

        # - Apply layout
        for (label, var, r, c) in fields:
            tk.Label(settings_frame, text=label,
                     bg=BG_CARD, font=("Segoe UI", 9)).grid(row=r, column=c, sticky="w", pady=8)
            tk.Entry(settings_frame, textvariable=var,
                     width=40, relief="solid", bd=1).grid(row=r, column=c+1, padx=10)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Core Operations - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - Header
        ops_frame = StyledFrame(self,"API Calls",ACCENT_BLUE)
        ops_frame.pack(pady=20, fill="x", padx=40)

        # - Buttons
        StyledButton(ops_frame, "⛳ GET ODDS", ACCENT_BLUE,
                     None # Replace with lambda function to Odds API call
                     ).grid(row=0, column=0, sticky="ew", padx=10)
        StyledButton(ops_frame, "👥 GET ENTRANTS", ACCENT_BLUE,
                     lambda: fetch_athlete_data(self.controller.tournament_league.get().lower(), # League
                                                self.controller.tournament_id.get(), # ID
                                                self.controller.tournament_name.get()) # Name
                     ).grid(row=0, column=1, sticky="ew", padx=10)
        StyledButton(ops_frame, "⛳ RUN ROUND", ACCENT_GREEN,
                     None # Replace with page nav to a round screen?
                          # or have a four block of round #s below this row?
                          # Highlight available rounds based on data saves,
                          # click a round to run it or click next to run next
                     ).grid(row=0, column=2, sticky="ew", padx=10)

        # Layout config
        for c in range(1, 3):
            ops_frame.grid_columnconfigure(c, weight=1)
        ops_frame.pack(pady=10, fill="x", padx=40)

        # Page Navigation - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - Header
        nav_frame = StyledFrame(self,"Navigation",ACCENT_BLUE)
        nav_frame.pack(pady=20, fill="x", padx=40)
        
        # - Buttons
        nav_btns = [
            ("Manage Players", "ManagePlayersPage", 0, 0),
            ("Available Picks", "PicksPage", 0, 1),
            ("Result Data", "ResultsPage", 0, 2),
            ("Player Scores", "ScoresPage", 1, 0),
            ("Scoreboard", "ScoreboardPage", 1, 1),
            ("Settings", "SettingsPage", 1, 2)
        ]

        # - Apply layout
        for (txt, pg, r, c) in nav_btns:
            StyledButton(nav_frame, txt, "#546e7a",
                         lambda p=pg: controller.show_frame(p)
                         ).grid(row=r, column=c, sticky="ew", padx=10, pady=5)
            nav_frame.grid_columnconfigure(c, weight=1)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Exit  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        StyledButton(self, "✖ EXIT", "#b71c1c",
                     controller.quit,
                     width=30).pack(pady=20)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -