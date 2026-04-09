import tkinter as tk
from tkinter import messagebox
import pandas as pd
import json
from pathlib import Path

def load_tournaments(self):
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent.parent
        file_path = project_root / "data" / "tourns.json"
        try:
            with open(file_path, 'r') as f:
                raw_data = json.load(f)
            
            df = pd.DataFrame.from_dict(raw_data, orient='index')
            df.index = df.index.map(str) # Lock IDs as strings
            
            self.saved_tournaments = []
            for tourn_id, row in df.iterrows():
                full_name = row.get('tournamentFullName', 'Unknown Tournament')
                self.saved_tournaments.append(f"{full_name} ({tourn_id})")
            
            self.all_tournaments_df = df
            print(f"Successfully loaded {len(self.saved_tournaments)} tournaments.")
            
        except Exception as e:
            self.saved_tournaments = ["No Tournaments Found"]
            print(f"Error in load_active_save: {e}")

def use_tournament(self):
    """Extracts ID from dropdown selection and updates controller variables"""
    selection = self.load_var.get()
    
    if selection and "(" in selection:
        # 1. Parse the ID from the string "Name (ID)"
        selected_id = selection.split('(')[-1].strip(')')
        
        try:
            # 2. Get the specific row from our cleaned Pandas DataFrame
            data = self.all_tournaments_df.loc[selected_id]
            
            # 3. Update the global controller variables
            self.controller.tournament_name.set(data.get('tournamentFullName', ''))
            self.controller.tournament_league.set(data.get('tournamentLeague', ''))
            self.controller.tournament_id.set(selected_id)
            self.controller.current_round.set(str(data.get('lastRound', '0')))
            self.controller.api.set(str(data.get('api', '')))
            
            # messagebox.showinfo("Success", f"Loaded: {data.get('tournamentFullName')}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not find tournament details: {e}")
    else:
        messagebox.showwarning("Error", "Select a valid tournament from the dropdown.")

def search_tournament(self):
    if messagebox.askyesno("Sync", "Confirm data overwrite?"):
        self.controller.tournament_name.set("The Open")