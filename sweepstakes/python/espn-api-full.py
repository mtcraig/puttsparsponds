# ------------------------------------------------------------------------------
# Putts Pars and Ponds Sweepstakes
# Lead Dev: Michael Craig
# ------------------------------------------------------------------------------
# Description:
# Performs the API fetches to drive the PPP Sweepstakes Excel
# ------------------------------------------------------------------------------
# Steps:
# 1 - Modules
# 2 - Fetch and request updates to process settings
# 3 - Restore or update athlete data
# 4 - Fetch scoring data for the requested round
# ------------------------------------------------------------------------------
#---|----1----|----2----|----3----|----4----|----5----|----6----|----7----|----8

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------

import pandas as pd
import requests
import json
import re
from pathlib import Path
import openpyxl

# ------------------------------------------------------------------------------
# FETCH AND REQUEST UPDATES TO PROCESS SETTINGS
# ------------------------------------------------------------------------------

# Import last settings

try:
    with open('../control/active-save.json', 'rb') as f:
        activeInfo = pd.read_json(f)
    tournFullName = activeInfo.at['tournamentFullName', 'lastSave']
    tournName = activeInfo.at['tournamentName', 'lastSave']
    tournID = activeInfo.at['tournamentESPN', 'lastSave']
    tournRound = int(activeInfo.at['lastRound', 'lastSave'])
    print('Last settings used: ' + tournFullName + ' (' + tournName + ') with ESPN API ID ' + tournID + '.')
except:
    print('Error fetching last settings. Please debug before proceeding. Exiting...')
    exit()

# Check for any updates to the active tournament

tournNameUpdate = ''
while tournNameUpdate not in ('Y','YES','N','NO'):
    tournNameUpdate = input('Currently active tournament is: ' + tournFullName + ', would you like to update it?').upper()
if tournNameUpdate in ('Y','YES'):
    tournFullNamePrev = tournFullName
    tournNamePrev = tournName
    tournFullName = ''
    while tournFullName == '':
        tournFullName = input('Please provide the name of the new tournament to be run for:').title()
    tournName = tournFullName.replace(' ','')
    print('Tournament updated from ' + tournFullNamePrev + ' (' + tournNamePrev + ') to ' + tournFullName + ' (' + tournName + ').')
    tournIDPrev = tournID
    tournID = ''
    while tournID == '':
        tournID = str(input('Please provide the new tournament ID for this event to connect to the ESPN API with:'))
    print('Tournament ID updated from ' + tournIDPrev + ' to ' + tournID + '.')
    print('Setting update complete.')
else:
    print('Continuing with the last used settings for ' + tournFullName + '.')

# Check for any updates to the active round

tournRoundUpdate = ''
if tournRound == 4:
    while tournRoundUpdate.upper() not in ('Y','YES','N','NO'):
        tournRoundUpdate = input('The last round processed was R' + str(tournRound) + '. Looks like the tournament is over! Would you like to rerun for one of the rounds?').upper()
    if tournRoundUpdate in ('Y','YES'):
        tournRound = 0
        while tournRound not in (1,2,3,4):
            tournRound = int(input('Enter the round number to rerun for:'))
        print('Rerunning for R' + str(tournRound) + '.')
    else:
        print('All rounds for ' + tournFullName + ' have been completed. Exiting...')
        exit()
else:
    while tournRoundUpdate.upper() not in ('Y','YES','N','NO'):
        tournRoundUpdate = input('The last round processed was R' + str(tournRound) + ', would you like to proceed to R' + str(tournRound + 1) + '?').upper()
    if tournRoundUpdate in ('Y','YES'):
        tournRoundPrev = tournRound
        tournRound + 1
        print('Incrementing round from R' + str(tournRoundPrev) + ' to R' + str(tournRound) + '.')
    else:
        tournRoundRerun = ''
        while tournRoundRerun.upper() not in ('Y','YES','N','NO'):
            tournRoundRerun = input('Would you like to run again for R' + str(tournRound) + '?').upper()
        if tournRoundRerun in ('Y','YES'):
            tournRoundUpdate = 'YES'
            print('Rerunning for R' + str(tournRound) + '.')
        else:
            print('No round has been selected for either a first time or a repeat run. Exiting...')
            exit()

# Save the updated settings to the active save file

tournSave = {
                'lastSave': {
                                'tournamentFullName': tournFullName,
                                'tournamentName': tournName,
                                'tournamentESPN': tournID,
                                'lastRound': tournRound
                            }
            }

try:
    with open('../control/active-save.json', 'w') as f:
        json.dump(tournSave, f)
    print('Successful')
except:
    print('Failed to write out save data. Please debug before proceeding. Exiting...')

# ------------------------------------------------------------------------------
# RESTORE OR UPDATE ATHLETE DATA
# ------------------------------------------------------------------------------

# Check for existing athlete data and ask if a request is desired

athleteUpdate = ''
try:
    athleteFile = Path('../data/athletes/athletes-' + tournID + '.json')
    if athleteFile.is_file():
        print('Found existing athletes file for ' + tournFullName + '.')
        while athleteUpdate.upper() not in ('Y','YES','N','NO'):
            athleteUpdate = input('Would you like to update the athletes data for this tournament?').upper()
        if athleteUpdate in ('Y','YES'):
            print('The process will now query the ESPN API for active competitors in ' + tournFullName + '.')
        else:
            print('Will now attempt to use the existing athletes data file...')
    else:
        athleteUpdate = 'YES'
        print('No existing file found for this tournament. The process will now query the ESPN API for active competitors in ' + tournFullName + '.')
except:
    while athleteUpdate.upper() not in ('Y','YES','N','NO'):
        athleteUpdate = input('There was an error accessing the athletes data for ' + tournFullName + '. Would you like to rerun the data fetch? If no, the process will exit for you to debug.').upper()
    if athleteUpdate in ('Y','YES'):
        print('The process will now query the ESPN API for active competitors in ' + tournFullName + '.')
    else:
        print('Please debug the athletes data file before proceeding. Exiting...')
        exit()

# Restore saved athlete data or do a new refresh for the active tournament

if athleteUpdate in ('N','NO'):
    try:
        with open(athleteFile, 'rb') as f:
            athleteDf = pd.read_json(f)
        athleteDict = athleteDf.to_dict('records')
        print('Athlete data successfully fetched for ' + tournFullName + ' (' + str(len(athleteDict)) + ' competitors).')
    except:
        print('Error fetching athletes in ' + athleteFile + '.')
        print('Please debug the athletes data file before proceeding. Exiting...')
        exit()
else:
    # Perform API Call
    tournURL = "http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/" + tournID + "/competitions/" + tournID + "?lang=en&region=us"
    tournResponse = requests.get(tournURL)
    tournResponse.raise_for_status()  # Raises an error for bad responses

    tournData = tournResponse.json()  # Parse JSON response

    # Loop through for all competitors to fetch their order number and athlete ID required to fetch individual score details
    i = 0
    athleteDict = []
    while i < len(tournData["competitors"]):
        athleteOrder = tournData["competitors"][i]["order"]
        athleteURL = tournData["competitors"][i]["athlete"]
        athleteID = list(athleteURL.values())[0].rstrip('/').split('/')[-1].split('?')[0]

        # Fetch Athlete Name
        athleteURL = "http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/seasons/2025/athletes/" + athleteID + "?lang=en&region=us"
        athleteResponse = requests.get(athleteURL)
        athleteResponse.raise_for_status()  # Raises an error for bad responses
        athleteData = athleteResponse.json()  # Parse JSON response
        athleteName = athleteData["displayName"]

        athleteDict = {
            "order": athleteOrder,
            "id": athleteID,
            "name": athleteName
        }
        athleteDict.append(athleteDict)
        print("Competitor fetch loop " + str(i) + " completed for " + athleteName + '.')
        i = i + 1

# print(athleteDict)

# If an update has occurred...

if athleteUpdate in ('Y','YES'):

    # Write out to storage

    try:
        with open(athleteFile, 'w') as f:
            json.dump(athleteDict, f)
        print('Athlete data for ' + tournFullName + ' has been successfully saved.')
    except:
        print('Failed to write out athlete data for ' + tournFullName + '. Please debug before proceeding. Exiting...')

    # Validate that the new athlete data matches between the pre and post save states

    print('Validating athlete data integrity following update...')
    try:
        with open(athleteFile, 'rb') as f:
            athleteDf = pd.read_json(f)
        athleteDictValidate = athleteDf.to_dict('records')
        if athleteDict == athleteDictValidate:
            print('Athlete data successfully fetched for ' + tournFullName + ' (' + str(len(athleteDictValidate)) + ' competitors).')
        else:
            print('Athlete data integrity violation detected. Please debug before proceeding. Exiting...')
            exit()
    except:
        print('Error fetching athletes in ' + athleteFile + '.')
        print('Please debug the athletes data file before proceeding. Exiting...')
        exit()

else:
    print('No update performed, skipping athlete data integrity check.')

# ------------------------------------------------------------------------------
# FETCH SCORING DATA FOR THE REQUESTED ROUND
# ------------------------------------------------------------------------------

print('Fetching scoring data for ' + tournFullName + ' R' + str(tournRound) + '.')

# Write Out Path
writeOutPath = Path('../data/rounds/round' + str(tournRound) + '-' + tournID + '.xlsx')

# FETCH SCORES AND STATS

# Loop through for all competitors to fetch their statistics
roundArray = [];
i = 0
while i < len(athleteDict):   
    # Generate athlete API URL
    scoreURL = "http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/" + tournID + "/competitions/" + tournID + "/competitors/" + athleteDict[i]["id"] + "/linescores?lang=en&region=us"
    # Perform API Call
    compResponse = requests.get(scoreURL)
    compResponse.raise_for_status()  # Raises an error for bad responses
    compData = compResponse.json()
    
    # ScoreCard Processing
    # Moved this up as this will always work

    athleteCurr = athleteDict[i]["name"]

    # If past the cut the round values are messed up for golfers out of the competition
    # - Try the score value and if that succeeds continue with the rest
    # Otherwise write 0 values out for all the relevant categories in the final dictionary
    try:

        # Added this here in case no linescores available
        tournRoundDetail = compData["items"][tournRound - 1]["linescores"]
        # print(tournRoundDetail)
        
        tournRoundNormal = pd.json_normalize(tournRoundDetail)
        # print(tournRoundNormal)

        # Parse out desired statistics
        tournRoundScore = compData["items"][tournRound - 1]["displayValue"]
        if tournRoundScore[0] == '+':
            tournRoundScoreInvert = -int(re.sub('[+-]','',tournRoundScore))
        elif tournRoundScore[0] == '-':
            tournRoundScoreInvert = int(re.sub('[+-]','',tournRoundScore))
        else:
            tournRoundScoreInvert = 0
        # print(tournRoundScoreInvert)

        # Find shot variants
        scoreTypes = tournRoundNormal["scoreType.name"].value_counts()
        scoreDict = scoreTypes.to_dict()
        # print(scoreDict)

        ## Eagles
        try:
            tournRoundEagles = scoreDict['EAGLE']
        except:
            tournRoundEagles = 0

        ## Bogeys
        try:
            tournRoundBogeys = scoreDict['BOGEY']
        except:
            tournRoundBogeys = 0

        ## Doubles
        try:
            tournRoundDoubles = scoreDict['DOUBLE_BOGEY']
        except:
            tournRoundDoubles = 0

        ## Holes In One (HIO)
        strokes = tournRoundNormal["displayValue"].value_counts()
        strokeDict = strokes.to_dict()
        try:
            tournRoundHIO = strokeDict['1']
        except KeyError:
            tournRoundHIO = 0

        # Bogey Free?
        if tournRoundBogeys == 0 and tournRoundDoubles == 0:
            tournRoundBFree = 'Yes'
        else:
            tournRoundBFree = 'No'
    
    except:
        tournRoundScoreInvert = 0
        tournRoundEagles = 0
        tournRoundBogeys = 0
        tournRoundDoubles = 0
        tournRoundBFree = 'Cut'
        tournRoundHIO = 0

    compDict = {
        "name": athleteCurr,
        "score": tournRoundScoreInvert,
        "eagles": tournRoundEagles,
        "bogeys": tournRoundBogeys,
        "doubles": tournRoundDoubles,
        "bogeyfree": tournRoundBFree,
        "holesinone": tournRoundHIO
    }
    roundArray.append(compDict)
    print("Scorecard fetch loop " + str(i) + " completed fetch for " + athleteCurr)
    i = i + 1

# Convert round output into an dataframe for export

roundDF = pd.DataFrame(roundArray)
# print(roundDF)

# Write out to storage

try:
    roundDF.to_excel(writeOutPath,
                    sheet_name="R" + str(tournRound))
    print('Successfully written out round data to ' + writeOutPath + '.')
except:
    print('There was an error writing round data to ' + writeOutPath + '.')


print('Run completed for ' + tournFullName + ' R' + str(tournRound) + '. Exiting...')
exit()

# END