import requests
import json
import os.path

_team_list = []

if os.path.exists('tba-data.txt'):
    print("Found cache! Loading data...")
    with open('tba-data.txt') as json_file:
        _team_stats = json.load(json_file)
        for key in _team_stats:
            item = _team_stats.get(key)
            item['team'] = key
            _team_list.append(item)
else:
    print("fail")
# Store Results
print("[INFO] Done! Writing Results to file...")
with open('tba-data-formatted.txt', 'w') as outfile:
    json.dump(_team_list, outfile)