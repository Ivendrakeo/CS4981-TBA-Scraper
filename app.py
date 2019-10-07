import requests
import json

# add's a key from a input dictionary to an output dictionary
def addField(key, inputDict, outputDict):
    if key in inputDict:
        outputDict[key] = inputDict[key]
    else:
        outputDict[key] = None


# Create a result formatted entry for output
def createEntry(eventInfo, team, numTeams):
    resultEntry = {}
    #print(eventInfo)
    #print(team)
    addField('team_key', team, resultEntry)
    addField('rank', team, resultEntry)
    addField('dq', team, resultEntry)
    addField('year', eventInfo, resultEntry)
    addField('address', eventInfo, resultEntry)
    addField('city', eventInfo, resultEntry)
    addField('week', eventInfo, resultEntry)
    addField('district', eventInfo, resultEntry)
    addField('event_type_string', eventInfo, resultEntry)
    addField('lat', eventInfo, resultEntry)
    addField('lng', eventInfo, resultEntry)
    addField('playoff_type_string', eventInfo, resultEntry)
    addField('postal_code', eventInfo, resultEntry)
    addField('state_prov', eventInfo, resultEntry)
    resultEntry['event_size'] = numTeams
    # team record...
    if(team['record'] != None):
        resultEntry['wins'] = team['record']['wins']
        resultEntry['losses'] = team['record']['losses']
        resultEntry['ties'] = team['record']['ties']
    else:
        resultEntry['wins'] = None
        resultEntry['losses'] = None
        resultEntry['ties'] = None
    return resultEntry



flag = 0
_auth_key = "X-TBA-Auth-Key=SppFLxpmcNKjZ7llJwg8Q9qWfVG3NrgjTi91rI36fzAoCW0ptgwCChCNsUh4eKAw"
_url = "https://www.thebluealliance.com/api/v3"
r = requests.get(_url + "/events/2002", params=_auth_key)
result = []
print("Welcome to the TBA scraper!")
for year in range(2002, 2020, 1):
    print("Scraping year " + str(year) + "...")
    events = requests.get(_url + "/events/" + str(year) + "/keys", params=_auth_key).json()
    # Getting event data
    for eventKey in events:
        try:
            eventInfo = requests.get(_url + "/event/" + str(eventKey), params=_auth_key).json()
            eventRankings = requests.get(_url + "/event/" + str(eventKey) + "/rankings", params=_auth_key).json()
            # Create column entries
            if eventRankings['rankings'] != None:
                for team in eventRankings['rankings']:
                    result.append(createEntry(eventInfo, team, len(eventRankings)))
        except:
            print("error found... skipping event " + eventKey)

# Store Results
print("Writing Results to file...")
with open('tba-data.txt', 'w') as outfile:
    json.dump(result, outfile)