- add box next to the API for tournament id
    ✅ empty to start and when data is loaded
    ✅ allow user entry
    - use this value in fetch_tournament to get tournament data, see api-full
    - message box containing the available tournaments or just the top latest available gets dumped into the info panel?

- round data
    - default new tournament to 0
    - check for available round data and set the value to +1 of that or 4 max

- add save functionality
    - pop any value from the save df matching the id
    - append the active entry vals
    - save out using existing logic from api-full

- integrate odds-api
    - build out test run of odds api for a single player
    - loop for all in a tournament
    - progress bar to show once the total # is known
    - save to a new odds folder
        - don't need to load these every time the app starts...
            - if picks pools for a tournament don't exist (create this additional save file) then
                - load odds and generate picks pools
                - save data and load to the screen to print
            - if they do exist just load those
                - have a recalc button if there's an oddity (allows debug of the player names most likely)
    - add share button to export the pick pools

- get players
    - have this call my code from api-full to get the athlete data and save it to the folder
    - progress bar to show once the total # is known
    - confirm when loaded

- run round
    - have this call my code from api-full to get the athlete data and save it to the folder
    - progress bar to show once the total # is known
    - confirm when loaded
    - calculate the scoring and save that as well to a scoring file

- manage players
    - improve form layout
    - pull player selections for each group from the pick pools
    - add the methods to pull values into the form again on selection
    - add the way to remove a record
    - add a save button or have it auto save when either submit is pressed or delete is pressed. or maybe both?

- available picks
    - result of pick pools in a table w/ odds
    - see comments under odds-api integration

- results
    - load scoring files to all rounds

- player scores
    - load player score file
        - if not created calc available rounds by
            - load player save w picks
            - load score save
            - calc player scores
            - save (1 file for all rounds, simple json)
        - if created check for update and calc if required else pass through
    - show player scores by round and cut
    - order by total score desc

- scoreboard
    - score tower with results (scrollable, highlight p1/p2/p3)
    - chart showing score for players by round/cut

- admin mode
    - access admin settings such as
        - the api key for the odds-api
        - data storage path (tbd, won't need anything like this until i understand the .exe packaging logic)
    - scoring options for new sweeps
        - will want to save scoring used in a save file

- restructure with packaging in mind
    - utils
        - code blocks
    - settings
        - core/admin
    - data
        - change from athletes/ + rounds/ to tournid/ containing all info
            - players
                - give players a uid
            - scoring system
            - golfers
            - rounds
            - r/r scoring w/ uid to connect to players
    - log
        - to print session activity to (replace print steps w/ write to ends)
