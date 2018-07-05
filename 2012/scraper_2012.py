import requests
from bs4 import BeautifulSoup
import pandas
import re
import datetime

def get_games():
    new_games = []
    teams = pandas.read_csv("2012_audl_teams.csv")

    f = open("2012_games_focused.txt")
    content = f.read()
    parser = BeautifulSoup(content, 'html.parser')

    rows = parser.find_all("tr")

    is_playoffs = 0

    for row in rows:

        cols = row.find_all('td')




        #Check to see if it is a header row in which case just get the date and continue
        if len(cols) == 1 or cols[1].text == 'Team':
            date_string = cols[0].text
            print(date_string)
            dt = datetime.datetime.strptime(date_string, "%A %m/%d/%y").date()
            str_date = dt.strftime("%m/%d/%Y")
            print(str_date)
            #set is_playoffs if game is after the last date of the regular season 7/22/2012
            if dt > datetime.date(2012,7,22):
                is_playoffs = 1
            else:
                is_playoffs = 0
            continue





        away_team_name = cols[1].text.strip()
        home_team_name = cols[3].text.strip()
        scores = cols[2].text.strip().split("\n")[0].split('-')
        #this ignores a 0-0* game that was presumably not played
        if '*' in scores[1]:
            continue
        away_score = int(scores[0])
        home_score = int(scores[1])

        #name_map = {"Salt Lake City Lions": "Salt Lake Lions","Philadelphia Phoenix Noon": "Philadelphia Phoenix","San Fransisco Flamethrowers": "San Francisco FlameThrowers","San Francisco Flamethrowers":"San Francisco FlameThrowers","Minnesota Windchill":"Minnesota Wind Chill"}
        #if away_team_name in name_map:
        #    away_team_name = name_map[away_team_name]
        print("away: "+away_team_name)
        #if home_team_name[:2] == "at":
        #    home_team_name = home_team_name[2:].strip()
        #if home_team_name in name_map:
        #    home_team_name = name_map[home_team_name]
        print("home: "+home_team_name)
        print()
        away_team = teams[teams['team_name'] == away_team_name]['abbr'].iloc[0]
        home_team = teams[teams['team_name'] == home_team_name]['abbr'].iloc[0]

        new_games.append([str_date,home_team,home_score,away_team,away_score,is_playoffs])
    return new_games



def run():
    games = pandas.DataFrame(get_games(),columns = ["date","team_id","pts","opp_id","opp_pts","is_playoffs"])

    games.sort_values("date", inplace=True)
    games.reset_index(drop=True,inplace=True)

    games.to_csv("2012_audl_games.csv")



if __name__ == "__main__":
    run()
