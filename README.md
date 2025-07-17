# puttsparsponds
Development for the Putts Pars and Ponds golf society including proposed Masters Sweepstakes and Web platforms

## Website

This is currently on hold until after I've stood up the basic API Sweepstakes tools for the July Open. In the future I'll migrate that implementation into the planned Sweepstakes section in the Members Lounge.

## Sweepstakes

### API

Provisionally I've selected the SlashGolf API for this - $0 upfront for 20 calls per day to the scorecard and leaderboard, up to 250 calls to all per month. $20 if exceeding but unlikely for our use case.

### Front-End

Layout adapted from Ben Plimley's original as used for The Masters.

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

Using the public ESPN API to fetch player information and daily scorecards. Technically these APIs are live data but I'm not querying that frequently to avoid getting red-flagged for abuse - 300 calls per day is more than enough!

1) Run Players Update once per tournament
2) Run Round Update once per day after end of play

Copy data from the Round Update excel outputs into the associated Round tabs in the Sweepstakes spreadsheet. Everything should then calculate scores for members accordingly.

##### espn-api-players-update.py

- When running:
    - Set the tournament ID (see the URL for the active tournament leaderboard on ESPN)
    - Update the athletePath to write out to a tournament file

- What it does:
    - For a given tournament, query the competition leaderboard API to gather competitors Athlete IDs
    - From these Athlete IDs, query the athlete API to gather competitor names
    - Append all competitors into an array, convert to a dataframe, and write out to a CSV to remove the need for future API calls for the same tournament

##### espn-api-round-update.py

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