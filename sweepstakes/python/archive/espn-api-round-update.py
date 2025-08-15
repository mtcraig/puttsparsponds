import pandas as pd
import requests
import json
import re
from pathlib import Path
import openpyxl

# FETCH COMPETITORS

# Tournament
tournID = str(401703521)
tournName = "TheOpen"
# Round to fetch:
rnd = 1

# Write Out Path
writeOutPath = Path("C:/Users/zz1/OneDrive/Documents/PPP/Sweepstakes/" + tournName + "-R" + str(rnd) + ".xlsx")

# Fetch the saved athlete information to save performing more API calls
athletePath = Path("C:/Users/zz1/OneDrive/Documents/PPP/Sweepstakes/" + tournName + "-athletes.csv")
athleteArray = pd.read_csv(athletePath).to_numpy()
print(athleteArray)

# FETCH SCORES AND STATS

# Loop through for all competitors to fetch their statistics
roundArray = [];
i = 0
while i < len(athleteArray):   
    # Generate athlete API URL
    scoreURL = "http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/" + tournID + "/competitions/" + tournID + "/competitors/" + athleteArray[i]["id"] + "/linescores?lang=en&region=us"
    # Perform API Call
    compResponse = requests.get(scoreURL)
    compResponse.raise_for_status()  # Raises an error for bad responses
    compData = compResponse.json()
    # Parse out desired statistics
    
    rndScore = compData["items"][rnd - 1]["displayValue"]
    if rndScore[0] == '+':
        rndScoreInvert = -int(re.sub('[+-]','',rndScore))
    elif rndScore[0] == '-':
        rndScoreInvert = int(re.sub('[+-]','',rndScore))
    else:
        rndScoreInvert = 0
    print(rndScoreInvert)

    # ScoreCard Processing

    athleteCurr = athleteArray[i]["name"]

    rndDetail = compData["items"][rnd - 1]["linescores"]
    # print(rndDetail)
    
    rndNormal = pd.json_normalize(rndDetail)
    # print(rndNormal)

    # Find shot variants
    scoreTypes = rndNormal["scoreType.name"].value_counts()
    scoreDict = scoreTypes.to_dict()
    # print(scoreDict)

    ## Eagles
    try:
        rndEagles = scoreDict['EAGLE']
    except:
        rndEagles = 0

    ## Bogeys
    try:
        rndBogeys = scoreDict['BOGEY']
    except:
        rndBogeys = 0

    ## Doubles
    try:
        rndDoubles = scoreDict['DOUBLE_BOGEY']
    except:
        rndDoubles = 0

    ## Holes In One (HIO)
    strokes = rndNormal["displayValue"].value_counts()
    strokeDict = strokes.to_dict()
    try:
        rndHIO = strokeDict['1']
    except KeyError:
        rndHIO = 0

    # Bogey Free?
    if rndBogeys == 0 and rndDoubles == 0:
        rndBFree = 'Yes'
    else:
        rndBFree = 'No'

    compDict = {
        "name": athleteCurr,
        "score": rndScoreInvert,
        "eagles": rndEagles,
        "bogeys": rndBogeys,
        "doubles": rndDoubles,
        "bogeyfree": rndBFree
    }
    roundArray.append(compDict)

# Convert round output into an dataframe for export
roundDF = pd.DataFrame(roundArray)
# print(roundDF)

# Write out to storage
roundDF.to_excel(writeOutPath,
                 sheet_name="R" + str(rnd))

# END