import requests
import json

# add's a key from a input dictionary to an output dictionary
def addField(key, inputDict, outputDict):
    if key in inputDict:
        outputDict[key] = inputDict[key]
    else:
        outputDict[key] = None


# Create a result formatted entry for output
def createEntry(eventInfo, team, numTeams, ccwm, opr, dpr, team_awards):
    resultEntry = {}
    #print(eventInfo)
    #print(team)
    addField('team_key', team, resultEntry)
    resultEntry['total_team_awards'] = team_awards['total_awards']
    resultEntry['total_team_blue_banners'] = team_awards['blue_banners']
    resultEntry['total_team_champ_wins'] = team_awards['champ_wins']
    #addField('dq', team, resultEntry)
    addField('year', eventInfo, resultEntry)
    addField('address', eventInfo, resultEntry)
    #addField('city', eventInfo, resultEntry)
    addField('week', eventInfo, resultEntry)
    addField('district', eventInfo, resultEntry)
    addField('event_type_string', eventInfo, resultEntry)
    addField('lat', eventInfo, resultEntry)
    addField('lng', eventInfo, resultEntry)
    addField('playoff_type_string', eventInfo, resultEntry)
    #addField('postal_code', eventInfo, resultEntry)
    addField('state_prov', eventInfo, resultEntry)
    resultEntry['event_size'] = numTeams
    addField('rank', team, resultEntry)
    resultEntry['ccwm'] = ccwm
    resultEntry['opr'] = opr
    resultEntry['dpr'] = dpr
    # team event record...
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

print("Start by caching all team id's")
_team_stats = {}
for page_num in range(0, 17, 1):
    print("collecting teams page " + str(page_num) + "/17")
    team_keys = requests.get(_url + "/teams/" + str(page_num) + "/keys", params=_auth_key).json()
    for key in team_keys:
        team_awards = requests.get(_url + "/team/" + key + "/awards", params=_auth_key).json()
        awards_entry = {}
        blue_banners = 0
        total_awards = 0
        champ_wins = 0
        for award in team_awards:
            total_awards = total_awards + 1
            if award['award_type'] == 1:
                blue_banners = blue_banners + 1
            if award['name'] == "Championship Winners":
                champ_wins = champ_wins + 1
        awards_entry['blue_banners'] = blue_banners
        awards_entry['total_awards'] = total_awards
        awards_entry['champ_wins'] = champ_wins
        _team_stats[key] = awards_entry
print("Caching Team data to file...")
with open('team-data.txt', 'w') as outfile:
    json.dump(_team_stats, outfile)




print("Begin Scraping Competition data...")
for year in range(2002, 2020, 1):
    print("Scraping year " + str(year) + "...")
    events = requests.get(_url + "/events/" + str(year) + "/keys", params=_auth_key).json()
    # Getting event data
    for eventKey in events:
        try:
            eventInfo = requests.get(_url + "/event/" + str(eventKey), params=_auth_key).json()
            eventRankings = requests.get(_url + "/event/" + str(eventKey) + "/rankings", params=_auth_key).json()
            eventOprs = requests.get(_url + "/event/" + str(eventKey) + "/oprs", params=_auth_key).json()
            # Create column entries
            if eventRankings['rankings'] != None:
                for team in eventRankings['rankings']:
                    result.append(createEntry(eventInfo, team, len(eventRankings), eventOprs['ccwms'][team['team_key']],
                                              eventOprs['oprs'][team['team_key']], eventOprs['dprs'][team['team_key']],
                                              _team_stats[team['team_key']]))
                    #result.append(createEntry(eventInfo, team, len(eventRankings), 0, 0, 0))
        except:
            print("error found... skipping event " + eventKey)

# Store Results
print("Writing Results to file...")
with open('tba-data.txt', 'w') as outfile:
    json.dump(result, outfile)