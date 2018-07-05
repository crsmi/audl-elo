import requests
from bs4 import BeautifulSoup
import pandas
import re
import datetime

def get_games():
    new_games = []
    teams = pandas.read_csv("2013_audl_teams.csv")
    f = open("2013_games_focused.txt")
    content = f.read()
    parser = BeautifulSoup(content, 'html.parser')

    weeks = [str(i) for i in range(1,15)] + ["p1","c"]


    for week in weeks:
        print(week)

        is_playoffs = 0
        if week in ["p1","c"]:
            is_playoffs = 1

        week_games = parser.find(id=week)

        game_list = week_games.find_all("tr")[1:]

        for game in game_list:

            info = game.text.split("\n")[1:6]

            #Get date - only listed for first game of the day so need to reuse
            if info[0] != "\xa0":
                date_string = info[0]
                print(date_string)
                dt = datetime.datetime.strptime(date_string + " 2013","%A, %B %d %Y").date()
                str_date = dt.strftime("%m/%d/%Y")
                print(str_date)


            away_team_href = info[4].lower().replace(' ','')
            home_team_href = info[2].lower().replace(' ','')
            scores = info[3].split('-')
            if "PPD" in scores:
                continue
            away_score = int(scores[1])
            home_score = int(scores[0])

            #name_map = {"Salt Lake City Lions": "Salt Lake Lions","Philadelphia Phoenix Noon": "Philadelphia Phoenix","San Fransisco Flamethrowers": "San Francisco FlameThrowers","San Francisco Flamethrowers":"San Francisco FlameThrowers","Minnesota Windchill":"Minnesota Wind Chill"}
            #if away_team_name in name_map:
            #    away_team_name = name_map[away_team_name]
            print("away: "+away_team_href)
            #if home_team_name[:2] == "at":
            #    home_team_name = home_team_name[2:].strip()
            #if home_team_name in name_map:
            #    home_team_name = name_map[home_team_name]
            print("home: "+home_team_href)
            print()
            away_team = teams[teams['href'] == away_team_href]['abbr'].iloc[0]
            home_team = teams[teams['href'] == home_team_href]['abbr'].iloc[0]

            new_games.append([str_date,home_team,home_score,away_team,away_score,is_playoffs])
    return new_games



def run():
    games = pandas.DataFrame(get_games(),columns = ["date","team_id","pts","opp_id","opp_pts","is_playoffs"])

    games.to_csv("2013_audl_games.csv")



if __name__ == "__main__":
    run()
