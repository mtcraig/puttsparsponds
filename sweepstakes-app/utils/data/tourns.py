import tkinter as tk
from tkinter import messagebox
import pandas as pd
import json
from pathlib import Path
import requests

from utils.data.log import add_session_entry

def load_tournaments(self):
    # Loads tournament data from tourns.json into a Pandas DataFrame and updates the dropdown list
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
        add_session_entry(f"Loaded {len(df)} tournaments from file.")
        
    except Exception as e:
        self.saved_tournaments = ["No Tournaments Found"]
        add_session_entry(f"Error in load_active_save: {e}")

def use_tournament(self):
    # Uses the selected tournament from the dropdown to update the main controller variables
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
            self.controller.current_round.set(str(data.get('lastRound', "0")))
            self.controller.api.set(str(data.get('api', "ESPN")))
            
            # messagebox.showinfo("Success", f"Loaded: {data.get('tournamentFullName')}")
        except Exception as e:
            add_session_entry(f"Error in use_tournament: {e}")
            messagebox.showerror("Error", f"Could not find tournament details: {e}")
    else:
        messagebox.showwarning("Error", "Select a valid tournament from the dropdown.")

def search_tournament(self):
    try:
        t_inf = {"t_league": self.controller.tournament_league.get().lower(), "t_id": self.controller.tournament_id.get()}
        t_url = f"http://sports.core.api.espn.com/v2/sports/golf/leagues/{t_inf['t_league']}/events/{t_inf['t_id']}?lang=en&region=us"
        t_resp = requests.get(t_url)
        t_resp.raise_for_status()  # Raises an error for bad responses
        t_dat = t_resp.json()  # Parse JSON response
        t_id = t_dat['id']
        t_name = t_dat['name']
    except Exception as e:
        failMsg = "ESPN API error: Search using provided ID failed." + f" Details: {e}"
        add_session_entry(failMsg)
        messagebox.showwarning("Error", failMsg)
        
    # Update the global controller variables
    self.controller.tournament_name.set(t_name)
    self.controller.current_round.set(0) # Default to round 0 for latest

def latest_tournament(self):
    try:
        tourn_league = self.controller.tournament_league.get().lower()
        l_url = f"http://sports.core.api.espn.com/v2/sports/golf/leagues/{tourn_league}/events?lang=en&region=us"
        l_resp = requests.get(l_url)
        l_resp.raise_for_status()  # Raises an error for bad responses
        l_dat = l_resp.json()  # Parse JSON response
        t_url = l_dat['items'][0]['$ref']
        add_session_entry(f"Successfully fetched latest tournament URL using ESPN API.")
        try:
            t_resp = requests.get(t_url)
            t_resp.raise_for_status()  # Raises an error for bad responses
            t_dat = t_resp.json()  # Parse JSON response
            t_id = t_dat['id']
            t_name = t_dat['name']
            add_session_entry(f"Successfully fetched latest tournament data for {t_id}: {t_name} using ESPN API.")
        except Exception as e:
            failMsg = "ESPN API error: Latest tournament fetch failed." + f" Details: {e}"
            add_session_entry(failMsg)
            messagebox.showwarning("Error", failMsg)
    except Exception as e:
        failMsg = "ESPN API error: League search failed." + f" Details: {e}"
        add_session_entry(failMsg)
        messagebox.showwarning("Error", failMsg)
        
    # Update the global controller variables
    self.controller.tournament_name.set(t_name)
    self.controller.tournament_id.set(t_id)
    self.controller.current_round.set(0) # Default to round 0 for latest

def fetch_athlete_data(t_league, t_id, t_name):
    # Perform API Call to ESPN to get tournament details including competitors and their IDs
    try:
        t_url = f"http://sports.core.api.espn.com/v2/sports/golf/leagues/{t_league}/events/{t_id}/competitions/{t_id}?lang=en&region=us"
        t_resp = requests.get(t_url)
        t_resp.raise_for_status()  # Raises an error for bad responses
        t_dat = t_resp.json()  # Parse JSON response
        t_year = t_dat["date"][:4] # Grabs the year from the tournament date field
        add_session_entry(f"Successfully called ESPN API at {t_url} for athlete data.")

    except Exception as e:
        failMsg = f"ESPN API error: Athlete data call  at {t_url} failed. Details: {e}"
        add_session_entry(failMsg)
        messagebox.showwarning("Error", failMsg)

    # Loop through for all competitors to fetch their order number and athlete ID required to fetch individual score details
    # t_year = str(date.today().year)
    # swap the above for a date parse - field in t_url json response date
    a_dict = []
    for competitor in t_dat['competitors']:
        a_id = int(competitor['id'])
        a_url = f"http://sports.core.api.espn.com/v2/sports/golf/leagues/{t_league}/seasons/{t_year}/athletes/{a_id}?lang=en&region=us"

        try:
            a_resp = requests.get(a_url)
            a_resp.raise_for_status()  # Raises an error for bad responses
            a_dat = a_resp.json()  # Parse JSON response

            a_dict.append({
                'order': competitor['order'],
                'id': a_id,
                'name': a_dat['displayName']
            })

            add_session_entry(f"Successfully fetched athlete data for {a_dat['displayName']} at {a_url}.")
        except Exception as e:
            failMsg = f"ESPN API error: Athlete data call at {a_url} failed. Details: {e}"
            add_session_entry(failMsg)
            messagebox.showwarning("Error", failMsg)
    
    # Write out to storage
    try:
        # Loads tournament data from tourns.json into a Pandas DataFrame and updates the dropdown list
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent.parent
        t_dir = project_root / "data" / t_id
        t_dir.mkdir(exist_ok=True) # Ensure logs directory exists
        a_file = t_dir / "athletes.json"
        with open(a_file, 'w') as f:
            json.dump(a_dict, f)
        # Sleep just to give a buffer between the write and read actions
        # time.sleep(2)
        add_session_entry(f"Successfully wrote athlete data to file for tournament {t_name}.")
        messagebox.showinfo("Success", f"Successfully fetched and stored athlete data for {len(a_dict)} competitors in {t_league.upper()}: {t_name}.")
    except Exception as e:
        add_session_entry(f"Error writing athlete data to file for tournament {t_name}. Details: {e}")
