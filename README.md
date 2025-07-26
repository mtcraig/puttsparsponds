<img src="/site/public/brand/ppp-logo.jpg" alt="Putts Pars & Ponds Logo" width="300"/>

# Welcome to Putts, Pars & Ponds!

This repository contains all development for the Putts Pars & Ponds golf society including proposed Masters Sweepstakes and Web platforms

## Website

This is currently on hold until after I've stood up the basic API Sweepstakes tools for the July Open. In the future I'll migrate that implementation into the planned Sweepstakes section in the Members Lounge. Fundamental architecture has been set up with a view to building a first draft in Node.JS / Express JS / EJS, but I anticipate eventually moving things into React once I've had the chance to go through that end to end process with my personal website first.

## Sweepstakes

### API

Using the ESPN Open APIs for this. Right now I'm not seeing any limitations, and obviously don't anticipate it changing, but it's also not locked down and could change at any time.

### Front-End

Layout adapted from Ben Plimley's original as used for The Masters 2025.

#### Tabs

- Results
    - Locked
    - All players from the picks sheet, showing their picks, round by round totals, and rankings
    - Chart to track day by day movement

- Picks
    - Partially locked
    - Enter player names and picks here using the drop downs
    - Picks remaining are shown, and an errors field will state if there's any gaps in picks
    - Pots are displayed below the player board, and the pots 1-4 and 5 (wildcards) are derived from the Scores sheet (see below), where players are ordered by odds from best to worst, as taken directly from ESPN
    - Select rates for all golfers are shown for information purposes

- Scores
    - Locked during sweepstakes activity
    - Player list and odds are fetched from the Odds sheets
    - Formulas calculate points awarded and lost best on the R1/R2/R3/R4 and cut states

- Odds
    - Full player odds ordered from best to worst copied here directly from ESPN
    - Pools are generated based on position top to bottom for the Picks sheet, with Pools 1/2/3/4/5 marked on this sheet accordingly

- Rounds (R1/R2/R3/R4)
    - Round data to be pasted in here from the python script output at the end of each game day
    - Data processed in the Scores sheet

### Back-End

#### Python

Note: Re-engineered 2025-07-26 post The Open 2025 tournament to provide an easier experience for updating and running for future tournaments and rounds.

The sweepstakes logic uses the public ESPN API to fetch player information and daily scorecards. Technically these APIs are live data but I'm not going to be querying that frequently to avoid getting red-flagged for abuse.
Initial code performed around 300 calls per day, having to refresh both the athletes and their scorecards every time - as of the latest release, this has been reduced so that the first round will perform those 300, but future rounds should only perform around 150 for scorecards only (unless an athlete refresh is actively requested by the user).

A process call will therefore generally:
1) Run a Player Update once per tournament
2) Run a Round Update once per day after end of play

After completion, just copy data from the Round Update excel outputs into the associated Round tabs in the Sweepstakes spreadsheet. Everything should then calculate scores for members and their picks accordingly.

##### Active Codebase

###### espn-api-full.py

This script was used for The Open 2025 throughout (see version as of that tournament date) and has been updated to support user prompts to make future tournaments hassle free in translating between events and rounds. Steps for the script are as follows:

1) Import modules
2) Fetch and request updates to process settings
    - Import last settings
    - Check for any updates to the active tournament
    - Check for any updates to the active round
    - Save the updated settings to the active save file
3) Restore or update athlete data
    - Check for existing athlete data and ask if a request is desired
    - Restore saved athlete data or do a new refresh for the active tournament
        - If refreshing:
            - Perform API Call
            - Loop through for all competitors to fetch their order number and athlete ID required to fetch individual score details
            - Write out to storage
            - Validate that the new athlete data matches between the pre and post save states
4) Fetch scoring data for the requested round
    - Loop through for all competitors to fetch their statistics
        - For each competitor, query the competitors tournament API to get all tournament data for them
        - ScoreCard Processing
            - Invert the round score (displayValue) so that +1 loses 1 point (-1) and -1 gains you a point (+1)
            - Access the linescores and calculate the number of shot types for Eagles, Bogeys and Doubles
            - Calculate Holes in One by checking the number of holes where the number of shots was 1
            - Calculate Bogey Free by checking the results of the Bogeys and Doubles calculation above
            - Store all stats in a dictionary with the player name, and append into an array (then dataframe)
    - Convert round output into an dataframe for export
    - Write out to storage

###### To Do:

- I'd like to expand the codebase to perform the full array of scoring updates including aggregation up to member level to migrate the platform away from Excel and make it possible to compile the python scripting into a single codebase, but this will absolutely require further refactoring to first introduce a proper GUI and then build out proper inputs, tables and charting, so this is a really big job!

##### Archived Codebase

These legacy scripts were initially developed for The Open 2025. These were replaced by a combined script due to issues with the save/restore logic on Day 1. That combined script has evolved into espn-api-full.py and as such the rest of the commit logs can be found under that script. Steps for these original Python scripts were defined as follows:

###### espn-api-players-update.py

- When running:
    - Set the tournament ID (see the URL for the active tournament leaderboard on ESPN)
    - Update the athletePath to write out to a tournament file

- What it does:
    - For a given tournament, query the competition leaderboard API to gather competitors Athlete IDs
    - From these Athlete IDs, query the athlete API to gather competitor names
    - Append all competitors into an array, convert to a dataframe, and write out to a CSV to remove the need for future API calls for the same tournament

###### espn-api-round-update.py

- When running:
    - Set the tournament ID (see the URL for the active tournament leaderboard on ESPN)
    - Update the round we're after, e.g. 1, 2, 3 or 4
    - Update the athletePath to write out to a tournament file
- What it does:
    - Reads in the saved athlete data file
    - For each competitor, query the competitors tournament API to get all tournament data for them
    - Invert the round score (displayValue) so that +1 loses 1 point (-1) and -1 gains you a point (+1)
    - Access the linescores and calculate the number of shot types for Eagles, Bogeys and Doubles
    - Calculate Holes in One by checking the number of holes where the number of shots was 1
    - Calculate Bogey Free by checking the results of the Bogeys and Doubles calculation above
    - Store all stats in a dictionary with the player name, and append into an array (then dataframe)
    - Export to excel sheet