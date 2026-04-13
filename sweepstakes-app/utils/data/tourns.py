import tkinter as tk
from tkinter import messagebox
import pandas as pd
import json
from pathlib import Path
import requests
import datetime
from datetime import date

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
        tournURL = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/' + self.controller.tournament_league.get().lower() + '/events/' + self.controller.tournament_id.get() + '?lang=en&region=us'
        tournResponse = requests.get(tournURL)
        tournResponse.raise_for_status()  # Raises an error for bad responses
        tournData = tournResponse.json()  # Parse JSON response
        tournID = tournData['id']
        tournFullName = tournData['name']
    except Exception as e:
        failMsg = "ESPN API error: Search using provided ID failed." + f" Details: {e}"
        add_session_entry(failMsg)
        messagebox.showwarning("Error", failMsg)
        
    # Update the global controller variables
    self.controller.tournament_name.set(tournFullName)
    self.controller.current_round.set(0) # Default to round 0 for latest

def latest_tournament(self):
    try:
        leagueURL = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/' + self.controller.tournament_league.get().lower() + '/events?lang=en&region=us'
        leagueResponse = requests.get(leagueURL)
        leagueResponse.raise_for_status()  # Raises an error for bad responses
        leagueData = leagueResponse.json()  # Parse JSON response
        tournURLLatest = leagueData['items'][0]['$ref']
        try:
            tournResponse = requests.get(tournURLLatest)
            tournResponse.raise_for_status()  # Raises an error for bad responses
            tournData = tournResponse.json()  # Parse JSON response
            tournID = tournData['id']
            tournFullName = tournData['name']
        except Exception as e:
            failMsg = "ESPN API error: Latest tournament fetch failed." + f" Details: {e}"
            add_session_entry(failMsg)
            messagebox.showwarning("Error", failMsg)
    except Exception as e:
        failMsg = "ESPN API error: League search failed." + f" Details: {e}"
        add_session_entry(failMsg)
        messagebox.showwarning("Error", failMsg)
        
    # Update the global controller variables
    self.controller.tournament_name.set(tournFullName)
    self.controller.tournament_id.set(tournID)
    self.controller.current_round.set(0) # Default to round 0 for latest

def fetch_athlete_data(self):
    # Perform API Call to ESPN to get tournament details including competitors and their IDs
    try:
        tournURL = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/' + self.controller.tournament_league.get().lower() + '/events/' + self.controller.tournament_id.get() + '/competitions/' + self.controller.tournament_id.get() + '?lang=en&region=us'
        tournResponse = requests.get(tournURL)
        tournResponse.raise_for_status()  # Raises an error for bad responses
    except Exception as e:
        failMsg = f"ESPN API error: Athlete data call  at {tournURL} failed. Details: {e}"
        add_session_entry(failMsg)
        messagebox.showwarning("Error", failMsg)
    tournData = tournResponse.json()  # Parse JSON response
    add_session_entry(f"Successfully called ESPN API at {tournURL} for athlete data.")

    # Loop through for all competitors to fetch their order number and athlete ID required to fetch individual score details
    i = 0
    athleteDict = []
    try:
        while i < len(tournData['competitors']):
            athleteOrder = tournData['competitors'][i]['order']
            athleteID = int(tournData['competitors'][i]['id'])

            # Fetch Athlete Name
            athleteURL = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/' + self.controller.tournament_league.get().lower() + '/seasons/' + str(date.today().year) + '/athletes/' + str(athleteID) + '?lang=en&region=us'
            athleteResponse = requests.get(athleteURL)
            athleteResponse.raise_for_status()  # Raises an error for bad responses
            athleteData = athleteResponse.json()  # Parse JSON response
            athleteName = athleteData['displayName']

            athleteInfo = {
                'order': athleteOrder,
                'id': athleteID,
                'name': athleteName
            }
            athleteDict.append(athleteInfo)
            # print('Competitor fetch loop ' + str(i+1) + ' completed for ' + athleteName + '.')
            i = i + 1
        add_session_entry(f"Successfully parsed athlete data for {len(athleteDict)} competitors.")
    except Exception as e:
        failMsg = f"ESPN API error: Athlete data parsing failed after {i} loops Details: {e}"
        add_session_entry(failMsg)
        messagebox.showwarning("Error", failMsg)
    
    # Write out to storage
    try:
        # Loads tournament data from tourns.json into a Pandas DataFrame and updates the dropdown list
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent.parent
        tourn_dir = project_root / "data" /self.controller.tournament_id.get()
        tourn_dir.mkdir(exist_ok=True) # Ensure logs directory exists
        athlete_file = tourn_dir / "athletes.json"
        with open(athlete_file, 'w') as f:
            json.dump(athleteDict, f)
        # Sleep just to give a buffer between the write and read actions
        # time.sleep(2)
        add_session_entry(f"Successfully wrote athlete data to file for tournament {self.controller.tournament_name.get()}.")
        messagebox.showinfo("Success", f"Successfully fetched and stored athlete data for {len(athleteDict)} competitors in the {self.controller.tournament_league.get()} {self.controller.tournament_name.get()}.")
    except Exception as e:
        add_session_entry(f"Error writing athlete data to file for tournament {self.controller.tournament_name.get()}. Details: {e}")
