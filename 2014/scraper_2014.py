import requests
from bs4 import BeautifulSoup
import pandas
import re
import datetime

def get_games():
    new_games = []
    teams = pandas.read_csv("2014_audl_teams.csv")
    f = open('The AUDL_2014_Scores.html')
    content = f.read()
    parser = BeautifulSoup(content, 'html.parser')
    weeks = parser.select(".field-content")
    week_num = 0

    # The site we scraped didn't have scores for the playoffs so we'll but them here to be looked up while scraping
    playoff_score_list = [[26,16],[37,11],[25,16],[22,17],[31,16],[20,23],[18,28]]

    for week in weeks:
        print(week_num,week)
        day_list = week.find_all("p")
        if week_num == "16":
            day_list = [week]
        if day_list == []:
            week_num = re.match(r'[Ww]eek (\d+)',week.text).group(1)
            continue
        for day in day_list:
            game_list = day.text.split('\n')
            print(game_list)
            if len(game_list) == 1:
                continue

            date_string = game_list[0].strip()
            print(date_string)
            game_list = game_list[1:]
            dt = datetime.datetime.strptime(date_string[:-2] + " 2014","%A %B %d %Y").date()
            str_date = dt.strftime("%m/%d/%Y")
            print(str_date)
            is_playoffs = 0
            if (dt > datetime.date(2014,7,17)):
                is_playoffs = 1
            for game in game_list:
                if game == '' or game[-12:] == "(Rain Delay)":
                    continue
                info_regex = r'^([A-Za-z\s]+[A-Za-z])\s+(\d+)\s+([A-Za-z\s]+[A-Za-z])\s+(\d+)'
                game = game.replace("@","at").strip()
                game = game.replace("vs","at")
                info = re.match(info_regex,game)
                if info == None:
                    print(game)
                    playoff_regex = r'^([A-Za-z\s]+[A-Za-z])\s+at\s+([A-Za-z\s]+[A-Za-z])'
                    p_info = re.match(playoff_regex,game)
                    playoff_game_score = playoff_score_list.pop(0)
                    away_team_name = p_info.group(1)
                    home_team_name = p_info.group(2)
                    #Switch hometeam for one championship weekend gamge b/c they were held in TOR
                    if away_team_name == "Toronto Rush":
                        away_team_name = home_team_name
                        home_team_name = "Toronto Rush"
                    #Get score from list defined earlier
                    away_score = playoff_game_score[1]
                    home_score = playoff_game_score[0]
                else:
                    away_team_name = info.group(1)
                    home_team_name = info.group(3)
                    away_score = info.group(2)
                    home_score = info.group(4)
                name_map = {"Salt Lake City Lions": "Salt Lake Lions","Philadelphia Phoenix Noon": "Philadelphia Phoenix","San Fransisco Flamethrowers": "San Francisco FlameThrowers","San Francisco Flamethrowers":"San Francisco FlameThrowers","Minnesota Windchill":"Minnesota Wind Chill"}
                if away_team_name in name_map:
                    away_team_name = name_map[away_team_name]
                print("away: "+away_team_name)
                if home_team_name[:2] == "at":
                    home_team_name = home_team_name[2:].strip()
                if home_team_name in name_map:
                    home_team_name = name_map[home_team_name]
                print("home: "+home_team_name)
                print()
                away_team = teams[teams['team_name'] == away_team_name]['abbr'].iloc[0]
                home_team = teams[teams['team_name'] == home_team_name]['abbr'].iloc[0]

                new_games.append([str_date,home_team,home_score,away_team,away_score,is_playoffs])
    #championship game (not in html file)
    new_games.append(["07/27/2014","TOR",18,"SJ",28,1])
    return new_games



def run():
    games = pandas.DataFrame(get_games(),columns = ["date","team_id","pts","opp_id","opp_pts","is_playoffs"])

    games.to_csv("2014_audl_games.csv")



if __name__ == "__main__":
    run()
