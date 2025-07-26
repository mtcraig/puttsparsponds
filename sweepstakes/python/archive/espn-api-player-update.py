import pandas as pd
import requests
import json
import re
from pathlib import Path
import openpyxl

# FETCH COMPETITORS

# Tournament Details API
tournID = str(401703521)
tournName = "TheOpen"

# Perform API Call
tournURL = "http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/" + tournID + "/competitions/" + tournID + "?lang=en&region=us"
tournResponse = requests.get(tournURL)
tournResponse.raise_for_status()  # Raises an error for bad responses

tournData = tournResponse.json()  # Parse JSON response

# Loop through for all competitors to fetch their order number and athlete ID required to fetch individual score details
i = 0
athleteArray = []
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
    athleteArray.append(athleteDict)
    i = i + 1

print(athleteArray)

athleteDF = pd.DataFrame(athleteArray)
athletePath = Path("C:/Users/zz1/OneDrive/Documents/PPP/Sweepstakes/" + tournName + "-athletes.csv")
athleteDF.to_csv(athletePath)

# END