#----|----1----|----2----|----3----|----4----|----5----|----6----|----7----|----8
# -------------------------------------------------------------------------------
# PPP Sweepstakes Manager - Version 0.1 Alpha
# Developed by: Michael Craig
# First Created: April 2026
# -------------------------------------------------------------------------------

# Modules - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import tkinter as tk
from utils.gui.styling import *
from utils.gui import pages
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Application - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class GolfSweepstakesApp(tk.Tk):

    def __init__(self):
        super().__init__()

        # Window Config - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.title("PPP Sweepstakes Manager - 0.1 Alpha")
        self.geometry("1100x975")
        self.configure(bg=BG_MAIN)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Window Header - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            self.iconbitmap("app_icon.ico") 
        except:
            pass # Skips if file doesn't exist yet
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Shared Data Variables - - - - - - - - - - - - - - - - - - - - - - - - -
        self.tournament_name = tk.StringVar(value="")
        self.tournament_league = tk.StringVar(value="")
        self.tournament_id = tk.StringVar(value="")
        self.current_round = tk.StringVar(value="")
        self.api = tk.StringVar(value="ESPN")
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        # Main Layout - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - Header
        self.header_frame = tk.Frame(self, bg=ACCENT_GREEN, height=100)
        self.header_frame.pack(side="top", fill="x")
        
        # - Logo Placeholder
        self.logo_label = tk.Label(self.header_frame, text="Putts, Pars & Ponds",
                                   fg="white", bg=ACCENT_GREEN,
                                   font=("Helvetica", 20, "italic bold"))
        self.logo_label.pack(pady=20)
        # To use a real image: 
        # self.logo_img = tk.PhotoImage(file="society_logo.png")
        # tk.Label(self.header_frame, image=self.logo_img, bg=ACCENT_GREEN).pack()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Pages Setup - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.container = tk.Frame(self, bg=BG_MAIN)
        self.container.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        page_list = (pages.HomePage,
                     pages.ManagePlayersPage,
                     pages.PicksPage,
                     pages.ResultsPage,
                     pages.ScoresPage,
                     pages.ScoreboardPage,
                     pages.SettingsPage)

        for F in page_list:
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.show_frame("HomePage")

    # Page Navigation Method
    def show_frame(self, page_name):
        self.frames[page_name].tkraise()
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# App Execution - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__":
    app = GolfSweepstakesApp()
    app.mainloop()
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -