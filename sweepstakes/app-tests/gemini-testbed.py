import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd # Ensure pandas is installed: pip install pandas

class GolfSweepstakesApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Par-Perfect Sweepstakes Manager")
        self.geometry("1100x950")
        self.configure(bg="#e8f5e9")

        # --- Shared Data Variables (Linked to GUI) ---
        self.tournament_name = tk.StringVar()
        self.current_round = tk.StringVar()
        self.tournament_league = tk.StringVar()
        self.tournament_id = tk.StringVar()
        
        # Internal placeholders for "Previous" save data
        self.prev_tournament_name = tk.StringVar()
        self.prev_round = tk.StringVar()

        # 1. RUN THE INITIAL LOAD FROM FILE
        self.load_active_save()

        # --- Layout Setup ---
        self.header_frame = tk.Frame(self, bg="#2e7d32", height=100)
        self.header_frame.pack(side="top", fill="x")
        tk.Label(self.header_frame, text="YOUR GOLF SOCIETY LOGO", 
                 fg="white", bg="#2e7d32", font=("Helvetica", 20, "bold")).pack(pady=20)

        self.container = tk.Frame(self, bg="#e8f5e9")
        self.container.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainSettingsPage, ManagePlayersPage, AvailablePicksPage, 
                  ResultsPage, ScoresPage, ChartsPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainSettingsPage")

    def show_frame(self, page_name):
        self.frames[page_name].tkraise()

    def load_active_save(self):
        """Your Pandas logic integrated into the App instance"""
        try:
            # Attempt to open the specific active-save file
            with open('../control/active-save.json', 'rb') as f:
                activeInfo = pd.read_json(f)
            
            try:
                # Update LATEST attributes into GUI Variables
                self.tournament_league.set(activeInfo.at['tournamentLeague', 'saveLatest'])
                self.tournament_name.set(activeInfo.at['tournamentName', 'saveLatest'])
                self.tournament_id.set(activeInfo.at['tournamentESPN', 'saveLatest'])
                self.current_round.set(str(activeInfo.at['lastRound', 'saveLatest']))
                print('Success: Latest tournament info synced from active-save.json')
            except Exception as e:
                self.tournament_league.set('N/A')
                self.tournament_name.set('N/A')
                self.tournament_id.set('N/A')
                self.current_round.set('0')
                print(f'Warning: Active-save file found but columns missing: {e}')

            try:
                # Update PREVIOUS attributes for background tracking
                self.prev_tournament_name.set(activeInfo.at['tournamentName', 'savePrevious'])
                self.prev_round.set(str(activeInfo.at['lastRound', 'savePrevious']))
            except:
                pass

        except FileNotFoundError:
            print("Error: active-save.json not found at ../control/")
        except Exception as e:
            print(f"Critical error loading save file: {e}")

# --- MAIN CONTROL PANEL ---
class MainSettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white", highlightbackground="#2e7d32", highlightthickness=2)
        self.controller = controller

        tk.Label(self, text="🏆 Tournament Command Center", font=("Segoe UI", 22, "bold"), 
                 bg="white", fg="#2e7d32").pack(pady=15)

        # 0. LOAD / RELOAD SECTION
        load_frame = tk.LabelFrame(self, text=" Tournament History & Files ", font=("Segoe UI", 10, "bold"),
                                   bg="white", padx=20, pady=15, fg="#2e7d32")
        load_frame.pack(pady=10, fill="x", padx=40)

        tk.Label(load_frame, text="Saved:", bg="white").grid(row=0, column=0)
        self.load_dropdown = ttk.Combobox(load_frame, state="readonly", width=30)
        self.load_dropdown['values'] = ["History Placeholder 1", "History Placeholder 2"]
        self.load_dropdown.grid(row=0, column=1, padx=10)

        # RELOAD BUTTON - Triggers the Pandas function in the controller
        tk.Button(load_frame, text="🔄 RELOAD ACTIVE-SAVE", bg="#1565c0", fg="white", 
                  font=("Segoe UI", 9, "bold"), padx=10,
                  command=self.refresh_active_data).grid(row=0, column=2, padx=5)

        # 1. FETCH SECTION (API/Web)
        fetch_frame = tk.LabelFrame(self, text=" Live Data Sync ", font=("Segoe UI", 10, "bold"),
                                    bg="white", padx=20, pady=15, fg="#1565c0")
        fetch_frame.pack(pady=10, fill="x", padx=40)

        tk.Button(fetch_frame, text="FETCH NEW TOURNAMENT", bg="#fb8c00", fg="white", 
                  font=("Segoe UI", 9, "bold"), width=25).pack()

        # 2. CURRENT SETTINGS (The Pandas data flows into these)
        settings_frame = tk.Frame(self, bg="white")
        settings_frame.pack(pady=20, fill="x", padx=40)

        fields = [
            ("Tournament Name:", controller.tournament_name, 0, 0),
            ("League:", controller.tournament_league, 0, 2),
            ("Round:", controller.current_round, 1, 0),
            ("Tournament ID:", controller.tournament_id, 1, 2)
        ]

        for (label, var, r, c) in fields:
            tk.Label(settings_frame, text=label, bg="white").grid(row=r, column=c, sticky="w", pady=5)
            tk.Entry(settings_frame, textvariable=var, width=25, relief="solid", bd=1).grid(row=r, column=c+1, padx=10)

        # 3. OPS & NAV (Shortened for brevity)
        ops_frame = tk.Frame(self, bg="white")
        ops_frame.pack(pady=10)
        tk.Button(ops_frame, text="RUN ROUND", bg="#2e7d32", fg="white", width=15, font=("Segoe UI", 10, "bold")).pack()

        tk.Button(self, text="RETURN TO NAV", bg="#546e7a", fg="white", 
                  command=lambda: controller.show_frame("ManagePlayersPage")).pack(pady=10)

    def refresh_active_data(self):
        """Bridge function to call the controller's load logic and notify the user"""
        self.controller.load_active_save()
        messagebox.showinfo("File Reloaded", "Successfully refreshed data from active-save.json")

# --- STUBS FOR OTHER PAGES ---
class ManagePlayersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        tk.Label(self, text="Manage Players", font=("Segoe UI", 18)).pack(pady=20)
        tk.Button(self, text="Back", command=lambda: controller.show_frame("MainSettingsPage")).pack()

class AvailablePicksPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
class ResultsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
class ScoresPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
class ChartsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

if __name__ == "__main__":
    app = GolfSweepstakesApp()
    app.mainloop()