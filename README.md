# puttsparsponds
Development for the Putts Pars and Ponds golf society including proposed Masters Sweepstakes and Web platforms

## Website

This is currently on hold until after I've stood up the basic API Sweepstakes tools for the July Open. In the future I'll migrate that implementation into the planned Sweepstakes section in the Members Lounge.

## Sweepstakes

### API

Provisionally I've selected the SlashGolf API for this - $0 upfront for 20 calls per day to the scorecard and leaderboard, up to 250 calls to all per month. $20 if exceeding but unlikely for our use case.

### Front-End

Basing this initially off Ben Plimley's spreadsheet.

### Integration

Planned actions:

- Python call to the schedule endpoint to fetch the tournament id
    - Write out and store
- Python call to the leaderboard endpoint once at end of day to fetch update for player e/o/r strokes
    - Write out and store
- Python call to the scorecard endpoint minimum of once at end of day to fetch hole by hole scores
    - Write out and store
    - Calculate for all players the +/- per hole
    - Tally +2+/+1/0/-1/-2/-2+
    - Write out to results field
- Calculate member scores based on selections
- Package and send daily

Optional:

- Could skip the leaderboard and generate it off the scorecard, saves 1 call daily plus development calls
- Do have the potential capacity to call the scorecard endpoint throughout the day, up to 20 times but maybe better to limit to 10 (one per hour?) to allow for room if issues and i need to debug and rerun endpoint calls