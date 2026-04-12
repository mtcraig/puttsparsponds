# ------------------------------------------------------------------------------
# SWEEPSTAKES MAIN APPLICATION
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------

import tkinter as tk
from utils.gui.styling import *
from utils.gui import pages

# ------------------------------------------------------------------------------
# APPLICATION
# ------------------------------------------------------------------------------

class GolfSweepstakesApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Par-Perfect Sweepstakes Manager")
        self.geometry("1100x975")
        self.configure(bg=BG_MAIN)

        # SET APPLICATION ICON (Taskbar/Window Header)
        try:
            self.iconbitmap("app_icon.ico") 
        except:
            pass # Skips if file doesn't exist yet

        # --- Shared Data Variables ---
        self.tournament_name = tk.StringVar(value="")
        self.current_round = tk.StringVar(value="")
        self.tournament_league = tk.StringVar(value="")
        self.tournament_id = tk.StringVar(value="")
        self.api = tk.StringVar(value="ESPN")
        self.search_id = tk.StringVar(value="")
        
        # --- Main Layout ---
        # 1. Top Header Area (Logo Space)
        self.header_frame = tk.Frame(self, bg=ACCENT_GREEN, height=100)
        self.header_frame.pack(side="top", fill="x")
        
        # LOGO PLACEHOLDER
        self.logo_label = tk.Label(self.header_frame, text="Putts, Pars & Ponds", 
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

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        self.frames[page_name].tkraise()

if __name__ == "__main__":
    app = GolfSweepstakesApp()
    app.mainloop()