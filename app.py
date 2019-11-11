import requests
import json
import os.path

# Authentication tokens and request URL
_auth_key = "X-TBA-Auth-Key=SppFLxpmcNKjZ7llJwg8Q9qWfVG3NrgjTi91rI36fzAoCW0ptgwCChCNsUh4eKAw"
_url = "https://www.thebluealliance.com/api/v3"
#result = [] # final JSON output array indexed by team key
_team_stats = {}  # results from querrying each team

def appendTeamData(teamRanking, eventOprs, eventKey):
    team_key = teamRanking['team_key']
    if team_key in _team_stats:
        _team_stats[team_key]['competitions_attended'] += 1
        _team_stats[team_key]['avg_rank'] += teamRanking['rank']
        if teamRanking['record'] is not None:
            _team_stats[team_key]['num_match_wins'] += teamRanking['record']['wins']
            _team_stats[team_key]['num_match_losses'] += teamRanking['record']['losses']
            _team_stats[team_key]['total_matches_played'] += teamRanking['matches_played']
        _team_stats[team_key]['avg_opr'] += eventOprs['oprs'][team_key]
        _team_stats[team_key]['avg_dpr'] += eventOprs['dprs'][team_key]
        _team_stats[team_key]['avg_ccwm'] += eventOprs['ccwms'][team_key]
    else:
        print("[WARNING] skipping team: " + team_key + " at event: " + eventKey)


"""
------------------------LEGACY CODE-------------------
# add's a key from a input dictionary to an output dictionary
def addField(key, inputDict, outputDict):
    if key in inputDict:
        outputDict[key] = inputDict[key]
    else:
        outputDict[key] = None


# Create a result formatted entry for output
def createEntry(eventInfo, team, numTeams, ccwm, opr, dpr, team_awards):
    resultEntry = {}
    addField('team_key', team, resultEntry)
    resultEntry['total_team_awards'] = team_awards['total_awards']
    resultEntry['total_team_blue_banners'] = team_awards['blue_banners']
    resultEntry['total_team_champ_wins'] = team_awards['champ_wins']
    resultEntry['city'] = team_awards['city']
    resultEntry['state_prov'] = team_awards['state_prov']
    resultEntry['lat'] = team_awards['lat']
    resultEntry['lng'] = team_awards['lng']
    resultEntry['rookie_year'] = team_awards['rookie_year']
    #addField('dq', team, resultEntry)
    addField('year', eventInfo, resultEntry)
    #addField('address', eventInfo, resultEntry)
    #addField('city', eventInfo, resultEntry)
    addField('week', eventInfo, resultEntry)
    #addField('district', eventInfo, resultEntry)
    #addField('event_type_string', eventInfo, resultEntry)
    #addField('lat', eventInfo, resultEntry)
    #addField('lng', eventInfo, resultEntry)
    #addField('playoff_type_string', eventInfo, resultEntry)
    #addField('postal_code', eventInfo, resultEntry)
    #addField('state_prov', eventInfo, resultEntry)
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
"""

print("Welcome to the TBA scraper!")

print("[INFO] Checking for local cache.")
if os.path.exists('team-data.txt'):
    print("Found cache! Loading data...")
    print("Skipping Step 1!")
    with open('team-data.txt') as json_file:
        _team_stats = json.load(json_file)
else:
    print("Cache not found! Need to scrape API.")
    print("Be patient. This is going to take awhile...")
    print("[INFO] STEP 1: Gather team data")
    for page_num in range(0, 17, 1):
        print("-------------------- Collecting teams page " + str(page_num) + "/17 --------------------")
        # collect all teams
        team_keys = requests.get(_url + "/teams/" + str(page_num) + "/keys", params=_auth_key).json()
        for key in team_keys:
            print("Requesting team records for team: " + key + "/frc8357")
            # Request team records
            team_awards = requests.get(_url + "/team/" + key + "/awards", params=_auth_key).json()
            team_years_participated = requests.get(_url + "/team/" + key + "/years_participated", params=_auth_key).json()
            team_data = requests.get(_url + "/team/" + key, params=_auth_key).json()
            team_entry = {}
            blue_banners = 0
            total_awards = 0
            champ_wins = 0
            # Calculate award data
            for award in team_awards:
                total_awards = total_awards + 1
                if award['award_type'] == 1:
                    blue_banners = blue_banners + 1
                if award['name'] == "Championship Winners":
                    champ_wins = champ_wins + 1
            # Fill with team award data
            team_entry['blue_banners'] = blue_banners
            team_entry['total_awards'] = total_awards
            team_entry['champ_wins'] = champ_wins
            # Collect team locational data
            team_entry['state_prov'] = team_data['state_prov']
            team_entry['postal_code'] = team_data['postal_code']
            team_entry['rookie_year'] = team_data['rookie_year']
            # Collect number of competitions
            team_entry['years_attended'] = len(team_years_participated)
            # create place holders for interpreted stats
            team_entry['competitions_attended'] = 0
            team_entry['avg_rank'] = 0
            team_entry['num_match_wins'] = 0
            team_entry['num_match_losses'] = 0
            team_entry['total_matches_played'] = 0
            team_entry['avg_opr'] = 0
            team_entry['avg_dpr'] = 0
            team_entry['avg_ccwm'] = 0
            team_entry['match_win_rate'] = 0
            # create dictionary entry to cache for later
            _team_stats[key] = team_entry
    print("Writing team cache to file")
    with open('team-data.txt', 'w') as outfile:
        json.dump(_team_stats, outfile)

print("[INFO] STEP 2: Begin Scraping Competition Data...")
for year in range(2002, 2020, 1):
    print("Scraping year " + str(year) + "...")
    events = requests.get(_url + "/events/" + str(year) + "/keys", params=_auth_key).json()
    # Getting event data
    for eventKey in events:
        try:
            print("Requesting Event info for event: " + eventKey)
            eventRankings = requests.get(_url + "/event/" + str(eventKey) + "/rankings", params=_auth_key).json()
            eventOprs = requests.get(_url + "/event/" + str(eventKey) + "/oprs", params=_auth_key).json()
            # Create column entries
            if eventRankings['rankings'] != None:
                for team in eventRankings['rankings']:
                    #result.append(createEntry(eventInfo, team, len(eventRankings), eventOprs['ccwms'][team['team_key']],
                    #                          eventOprs['oprs'][team['team_key']], eventOprs['dprs'][team['team_key']],
                    #                          _team_stats[team['team_key']]))
                    appendTeamData(team, eventOprs, eventKey)
        except Exception as e:
            print("[WARNING] skipping event: " + eventKey)

# Average the stats that need to be averaged
print("[INFO] STEP 3: Wrapping up! Performing data preparation...")
for team in _team_stats:
    if _team_stats[team]['competitions_attended'] != 0:
        _team_stats[team]['avg_rank'] = _team_stats[team]['avg_rank'] / _team_stats[team]['competitions_attended']
        _team_stats[team]['avg_opr'] = _team_stats[team]['avg_opr'] / _team_stats[team]['competitions_attended']
        _team_stats[team]['avg_dpr'] = _team_stats[team]['avg_dpr'] / _team_stats[team]['competitions_attended']
        _team_stats[team]['avg_ccwm'] = _team_stats[team]['avg_ccwm'] / _team_stats[team]['competitions_attended']
    if _team_stats[team]['total_matches_played'] != 0:
        _team_stats[team]['match_win_rate'] = _team_stats[team]['num_match_wins'] / _team_stats[team]['total_matches_played']

# Store Results
print("[INFO] Done! Writing Results to file...")
with open('tba-data.txt', 'w') as outfile:
    json.dump(_team_stats, outfile)