# ------------------------------------------------------------------------------
# Putts Pars & Ponds Sweepstakes
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

print('---------------------------------------------------------------------------')
print('Putts, Pars & Ponds Sweepstakes')
print('---------------------------------------------------------------------------')
print('Importing required modules...')

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------

import pandas as pd
import requests
import json
import re
from pathlib import Path
import openpyxl
import time
from datetime import date
import sys

print('Done.')

# ------------------------------------------------------------------------------
# FETCH AND REQUEST UPDATES TO PROCESS SETTINGS
# ------------------------------------------------------------------------------

print('---------------------------------------------------------------------------')
print('Importing settings...')

# Import last settings

try:
    # Open active-save data file
    with open('../control/active-save.json', 'rb') as f:
        activeInfo = pd.read_json(f)
    try:
        # Get latest save attributes
        tournLeague = activeInfo.at['tournamentLeague', 'saveLatest']
        tournFullName = activeInfo.at['tournamentFullName', 'saveLatest']
        tournName = activeInfo.at['tournamentName', 'saveLatest']
        tournID = activeInfo.at['tournamentESPN', 'saveLatest']
        tournRound = int(activeInfo.at['lastRound', 'saveLatest'])
        print('Valid latest tournament information found in the active save file!')
    except:
        # Default attributes if no latest save data available
        tournLeague = 'N/A'
        tournFullName = 'N/A'
        tournName = 'N/A'
        tournID = 'N/A'
        tournRound = 0
        print('No valid latest tournament information found in the active save file!')
    try:
        # Get earlier save attributes
        tournLeaguePrev = activeInfo.at['tournamentLeague', 'savePrevious']
        tournFullNamePrev = activeInfo.at['tournamentFullName', 'savePrevious']
        tournNamePrev = activeInfo.at['tournamentName', 'savePrevious']
        tournIDPrev = activeInfo.at['tournamentESPN', 'savePrevious']
        tournRoundPrev = int(activeInfo.at['lastRound', 'savePrevious'])
        print('Valid previous tournament information found in the active save file!')
    except:
        # Default attributes if no earlier save data available
        tournLeaguePrev = 'N/A'
        tournFullNamePrev = 'N/A'
        tournNamePrev = 'N/A'
        tournIDPrev = 'N/A'
        tournRoundPrev = 0
        print('No valid previous tournament information found in the active save file!')
except:
    # Force exit to debug as the save json file should at least exist
    print('Error fetching last settings. Please debug before proceeding. Exiting...')
    print('---------------------------------------------------------------------------')
    sys.exit()

print('Done.')
print('---------------------------------------------------------------------------')

# Function to target the desired league and pull back the latest tournament on their records
# Not required to use the results of this fetch but will speed things up if it pulls back the right tournament!

def latestTourn():
    failMsg = 'Failed to fetch the latest tournament information from the ESPN API. Manual entry will be required, but be aware this may be an issue requiring debugging.'
    try:
        leagueURL = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/' + tournLeague + '/events?lang=en&region=us'
        leagueResponse = requests.get(leagueURL)
        leagueResponse.raise_for_status()  # Raises an error for bad responses
        leagueData = leagueResponse.json()  # Parse JSON response
        tournURLLatest = leagueData['items'][0]['$ref']
        try:
            tournResponseLatest = requests.get(tournURLLatest)
            tournResponseLatest.raise_for_status()  # Raises an error for bad responses
            tournDataLatest = tournResponseLatest.json()  # Parse JSON response
            tournIDLatest = tournDataLatest['id']
            tournFullNameLatest = tournDataLatest['name']
        except:
            return ('fail','')
            print(failMsg)
    except:
        return('fail','')
        print(failMsg)
    return (tournIDLatest, tournFullNameLatest)

# Check for any updates to the active tournament

tournNameUpdate = ''
while tournNameUpdate not in ('Y','YES','N','NO'):
    # If default attributes are set then a new full set of attributes is required
    if tournFullName == 'N/A':
        tournNameUpdate = 'YES'
        print('As no save data was found you will need to enter all details for the desired tournament.')
    # If there's attributes already then ask if an update is desired or not
    else:
        tournNameUpdate = input('Currently active tournament is: ' + tournLeague.upper() + ' - ' + tournFullName + ', would you like to update it? ').upper()
if tournNameUpdate in ('Y','YES'):
    # If updating, store the last values and prompt for replacement
    tournLeaguePrev = tournLeague
    tournFullNamePrev = tournFullName
    tournNamePrev = tournName
    tournIDPrev = tournID
    tournRoundPrev = tournRound
    tournFullName = ''
    tournID = ''
    tournLeague = ''
    tournRound = 1
    while tournLeague not in ('pga','liv'):
        tournLeague = input('Which league is the new tournament running in, PGA or LIV? ').lower()
    # Check for the latest tournament available on ESPN for the chosen league
    latestTournData = latestTourn()
    if latestTournData[0] != 'fail':
        autoSelect = ''
        while autoSelect not in ('Y','YES','N','NO'):
            autoSelect = input('Auto-fetched the information for ' + latestTournData[1] + ' from ESPN - would you like to use these details? ').upper()
    if autoSelect in ('Y','YES'):
        tournID = latestTournData[0]
        tournFullName = latestTournData[1]
        tournName = tournFullName.replace(' ','')
        print('Auto selected ' + tournFullName + ' (' + tournID + ').')
    else:
        while tournFullName == '':
            tournFullName = input('Please provide the name of the new tournament to be run for:').title()
        tournName = tournFullName.replace(' ','')
        print('Tournament updated from ' + tournLeaguePrev.upper() + ': ' + tournFullNamePrev + ' (' + tournNamePrev + ') to ' + tournLeague.upper() + ': ' + tournFullName + ' (' + tournName + ').')
        while tournID == '':
            tournID = str(input('Please provide the new tournament ID for this event to connect to the ESPN API with:'))
        print('Tournament ID updated from ' + tournIDPrev + ' to ' + tournID + '.')
        print('Validating against the ESPN API')
        # Validate the manually selected data (we already know if the auto fetch worked at this point)
        try:
            tournURL = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/' + tournLeague + '/events/' + tournID + '/competitions/' + tournID + '?lang=en&region=us'
            tournResponse = requests.get(tournURL)
            tournResponse.raise_for_status()  # Raises an error for bad responses
            tournValidate = True
        except:
            tournValidate = False
            print('Bad or no response from the ESPN API for the chosen tournament name and ID combination. Please try again.')
    print('Setting update complete.')
else:
    # Otherwise confirm no changes made and proceed
    print('Continuing with the last used settings for ' + tournLeague.upper() + ' - ' + tournFullName + '.')
print('---------------------------------------------------------------------------')

# Check for any updates to the active round

tournRoundUpdate = ''
if tournRound == 4:
    # If the last round ran was the last one then prompt for possible reruns of any past rounds
    while tournRoundUpdate not in ('Y','YES','N','NO'):
        tournRoundUpdate = input('The last round processed was R' + str(tournRound) + '. Looks like the tournament is over! Would you like to rerun for one of the rounds? ').upper()
    if tournRoundUpdate in ('Y','YES'):
        tournRound = 0
        while tournRound not in (1,2,3,4):
            tournRound = int(input('Enter the round number to rerun for:'))
        print('Rerunning for R' + str(tournRound) + '.')
    else:
        print('All rounds for ' + tournFullName + ' have been completed. Exiting...')
        sys.exit()
else:
    while tournRoundUpdate not in ('Y','YES','N','NO'):
        # If the round number is the default then no rounds have happened yet, so prompt to confirm round 1 is the right thing
        if tournNameUpdate in ('Y','YES'):
            tournRoundUpdate = input('No rounds have been processed yet, would you like to proceed with R' + str(tournRound) + '? ').upper()
        else:
            tournRoundUpdate = input('The last round processed was R' + str(tournRound) + ', would you like to proceed to R' + str(tournRound + 1) + '? ').upper()
    if tournRoundUpdate in ('Y','YES'):
        # If a round update was requested then increment the round number and inform the user
        tournRound = tournRound + 1
        if tournRound == 1:
            print('The process will be run for R' + str(tournRound) + ' of the tournament.')
        else:
            print('Incrementing round from R' + str(tournRoundPrev) + ' to R' + str(tournRound) + '.')
    else:
        # Otherwise prompt for a rerun of a previous round
        tournRoundRerun = ''
        while tournRoundRerun not in ('Y','YES','N','NO'):
            tournRoundRerun = input('Would you like to run for a specific round? ').upper()
        # If rerunning then prompt for a round number
        if tournRoundRerun in ('Y','YES'):
            tournRound = 0
            while tournRound not in (1,2,3,4):
                tournRound = int(input('Enter the round number to rerun for:'))
            print('Rerunning for R' + str(tournRound) + '.')
        # Otherwise gracefully exit
        else:
            print('No round has been selected for either a first time or a repeat run - the process will now exit. If you have updated a new tournament, that information has not been saved. Exiting...')
            print('---------------------------------------------------------------------------')
            sys.exit()

print('---------------------------------------------------------------------------')

# Save the updated settings to the active save file

if tournNameUpdate in ('Y','YES') or tournRoundUpdate in ('Y','YES') or tournRoundRerun in ('Y','YES'):
    print('Updates accepted, saving...')
    tournSave = {
                    'saveLatest': {
                                    'tournamentLeague': tournLeague,
                                    'tournamentFullName': tournFullName,
                                    'tournamentName': tournName,
                                    'tournamentESPN': tournID,
                                    'lastRound': tournRound
                                },
                    'savePrevious': {
                                    'tournamentLeague': tournLeaguePrev,
                                    'tournamentFullName': tournFullNamePrev,
                                    'tournamentName': tournNamePrev,
                                    'tournamentESPN': tournIDPrev,
                                    'lastRound': tournRoundPrev
                                }
                }
    try:
        with open('../control/active-save.json', 'w') as f:
            json.dump(tournSave, f)
        print('Tournament settings have been updated successfully! Moving onto the active API calls...')
    except:
        print('Failed to write out save data. Please debug before proceeding. Exiting...')
        print('---------------------------------------------------------------------------')
        sys.exit()
else:
    print('Proceeding to athlete data review...')
print('---------------------------------------------------------------------------')

# ------------------------------------------------------------------------------
# RESTORE OR UPDATE ATHLETE DATA
# ------------------------------------------------------------------------------

# Check for existing athlete data and ask if a request is desired

athleteUpdate = ''
try:
    athleteFileStr = '../data/athletes/athletes-' + tournID + '.json'
    athleteFile = Path(athleteFileStr)
    if athleteFile.is_file():
        print('Found existing athletes file for ' + tournFullName + '.')
        while athleteUpdate not in ('Y','YES','N','NO'):
            athleteUpdate = input('Would you like to update the athletes data for this tournament? ').upper()
        if athleteUpdate in ('Y','YES'):
            print('The process will now query the ESPN API for active competitors in ' + tournFullName + '.')
        else:
            print('Will now attempt to use the existing athletes data file...')
    else:
        athleteUpdate = 'YES'
        print('No existing file found for this tournament. The process will now query the ESPN API for active competitors in ' + tournFullName + '.')
except:
    while athleteUpdate not in ('Y','YES','N','NO'):
        athleteUpdate = input('There was an error accessing the athletes data for ' + tournFullName + '. Would you like to rerun the data fetch? If no, the process will exit for you to debug.').upper()
    if athleteUpdate in ('Y','YES'):
        print('The process will now query the ESPN API for active competitors in ' + tournFullName + '.')
    else:
        print('Please debug the athletes data file before proceeding. Exiting...')
        print('---------------------------------------------------------------------------')
        sys.exit()
print('---------------------------------------------------------------------------')

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
        sys.exit()
else:
    print('Fetching athlete data for ' + tournFullName + '.')
    print('---------------------------------------------------------------------------')
    # Perform API Call
    tournURL = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/' + tournLeague + '/events/' + tournID + '/competitions/' + tournID + '?lang=en&region=us'
    tournResponse = requests.get(tournURL)
    tournResponse.raise_for_status()  # Raises an error for bad responses

    tournData = tournResponse.json()  # Parse JSON response

    # Loop through for all competitors to fetch their order number and athlete ID required to fetch individual score details
    i = 0
    athleteDict = []
    while i < len(tournData['competitors']):
        athleteOrder = tournData['competitors'][i]['order']
        athleteID = int(tournData['competitors'][i]['id'])

        # Fetch Athlete Name
        athleteURL = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/' + tournLeague + '/seasons/' + str(date.today().year) + '/athletes/' + str(athleteID) + '?lang=en&region=us'
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
        print('Competitor fetch loop ' + str(i) + ' completed for ' + athleteName + '.')
        i = i + 1
print('---------------------------------------------------------------------------')

# Save down the athlete data and perform integrity checks

# If an update has occurred...
if athleteUpdate in ('Y','YES'):

    # Write out to storage
    try:
        with open(athleteFile, 'w') as f:
            json.dump(athleteDict, f)
        print('Athlete data for ' + tournFullName + ' has been successfully saved.')
        # Sleep just to give a buffer between the write and read actions
        time.sleep(2)
    except:
        print('Failed to write out athlete data for ' + tournFullName + '. Please debug before proceeding. Exiting...')
        print('---------------------------------------------------------------------------')
        sys.exit()

    # Validate that the new athlete data matches between the pre and post save states
    print('Validating athlete data integrity following update...')
    try:
        with open(athleteFile, 'rb') as f:
            athleteDf = pd.read_json(f)
        athleteDictValidate = athleteDf.to_dict('records')
    except:
        print('Error fetching athletes in ' + athleteFileStr + '.')
        print('Please debug the athletes data file before proceeding. Exiting...')
        print('---------------------------------------------------------------------------')
        sys.exit()
    # If the pre-save and post-read dictionaries match exactly then integrity is confirmed...
    if athleteDict == athleteDictValidate:
        print('Athlete data integrity verified for ' + tournFullName + ' (' + str(len(athleteDictValidate)) + ' competitors).')
    # Otherwise there's an issue, writing the dictionaries to the log here to perform manual verification
    else:
        print('Athlete data integrity violation detected for ' + tournFullName + '. Please debug before proceeding. Exiting...')
        print('athleteDict:')
        print('-------------------------------')
        print(athleteDict)
        print('athleteDictValidate:')
        print('-------------------------------')
        print(athleteDictValidate)
        print('---------------------------------------------------------------------------')
        sys.exit()
# If no updates then can safely skip as it'll have passed this checkpoint before
else:
    print('No update performed, skipping athlete data integrity check.')
print('---------------------------------------------------------------------------')

# ------------------------------------------------------------------------------
# FETCH SCORING DATA FOR THE REQUESTED ROUND
# ------------------------------------------------------------------------------

print('Fetching scoring data for ' + tournFullName + ' R' + str(tournRound) + '.')
print('---------------------------------------------------------------------------')

# Write Out Path
writeOutPathStr = '../data/rounds/tourn-' + tournID + '-round' + str(tournRound) + '.xlsx'
writeOutPath = Path(writeOutPathStr)

# FETCH SCORES AND STATS

# Loop through for all competitors to fetch their statistics
roundArray = [];
i = 0
while i < len(athleteDict):

    # Generate athlete API URL
    scoreURL = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/' + tournLeague + '/events/' + tournID + '/competitions/' + tournID + '/competitors/' + str(athleteDict[i]['id']) + '/linescores?lang=en&region=us'

    # Perform API Call
    compResponse = requests.get(scoreURL)
    compResponse.raise_for_status()  # Raises an error for bad responses
    compData = compResponse.json()
    
    # ScoreCard Processing

    athleteCurr = athleteDict[i]['name']

    # If past the cut the round values are messed up for golfers out of the competition
    # - Try the score value and if that succeeds continue with the rest
    # Otherwise write 0 values out for all the relevant categories in the final dictionary
    try:

        # Added this here in case no linescores available
        tournRoundDetail = compData['items'][tournRound - 1]['linescores']
        # print(tournRoundDetail)
        
        tournRoundNormal = pd.json_normalize(tournRoundDetail)
        # print(tournRoundNormal)

        # Parse out desired statistics
        tournRoundScore = compData['items'][tournRound - 1]['displayValue']
        if tournRoundScore[0] == '+':
            tournRoundScoreInvert = -int(re.sub('[+-]','',tournRoundScore))
        elif tournRoundScore[0] == '-':
            tournRoundScoreInvert = int(re.sub('[+-]','',tournRoundScore))
        else:
            tournRoundScoreInvert = 0

        # Find shot variants
        scoreTypes = tournRoundNormal['scoreType.name'].value_counts()
        scoreDict = scoreTypes.to_dict()

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
        strokes = tournRoundNormal['displayValue'].value_counts()
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
        'name': athleteCurr,
        'score': tournRoundScoreInvert,
        'eagles': tournRoundEagles,
        'bogeys': tournRoundBogeys,
        'doubles': tournRoundDoubles,
        'bogeyfree': tournRoundBFree,
        'holesinone': tournRoundHIO
    }
    roundArray.append(compDict)
    print('Scorecard fetch loop ' + str(i) + ' completed fetch for ' + athleteCurr)
    i = i + 1

# Convert round output into an dataframe for export

roundDF = pd.DataFrame(roundArray)

# Write out to storage

print('---------------------------------------------------------------------------')
print('Saving scorecard data...')
print('---------------------------------------------------------------------------')

try:
    roundDF.to_excel(writeOutPath,
                    sheet_name='R' + str(tournRound))
    print('Successfully written out round data to ' + writeOutPathStr + '.')
except:
    print('There was an error writing round data to ' + writeOutPathStr + '.')

print('---------------------------------------------------------------------------')
print('Run completed for ' + tournFullName + ' R' + str(tournRound) + '. Exiting...')
print('---------------------------------------------------------------------------')
sys.exit()

# ------------------------------------------------------------------------------
# END
# ------------------------------------------------------------------------------