import requests
from bs4 import BeautifulSoup
import pandas
import datetime


def get_weeks_games(week):
    print(week)
    new_games = []
    teams = pandas.read_csv("2019_audl_teams.csv")
    #headers = {'Host': 'theaudl.com','Connection': 'keep-alive','Cache-Control': 'max-age=0','Upgrade-Insecure-Requests': '1','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9', 'Cookie': 'has_js=1; _ga=GA1.2.1750178249.1522537508; _gid=GA1.2.1723616333.1522537508','If-None-Match': '"1522534324-1"'}
    response = requests.get("http://theaudl.com/league/schedule/" + week)
    content = response.content
    print(content[0:24])
    parser = BeautifulSoup(content, 'html.parser')
    game_tables = parser.find_all("table", class_="audl-schedule-box")
    is_playoffs = 0
    if week in ["playoffs","championship-weekend"]:
        is_playoffs = 1
    for game_table in game_tables:
        date_string = game_table.find(class_='audl-schedule-start-time-text').text.split(' ')[1]
        dt = datetime.datetime.strptime(date_string + " 2019","%m/%d %Y").date()
        str_date = dt.strftime("%m/%d/%Y")
        team_names = game_table.find_all(class_='audl-schedule-team-name')
        scores = game_table.find_all(class_='audl-schedule-team-score')
        away_team_name = team_names[0].text
        print(away_team_name)
        away_team = teams[teams['team_name'] == away_team_name]['abbr'].iloc[0]
        home_team_name = team_names[1].text
        print(home_team_name)
        home_team = teams[teams['team_name'] == home_team_name]['abbr'].iloc[0]
        home_score = scores[1].text
        away_score = scores[0].text
        new_games.append([str_date,home_team,home_score,away_team,away_score,is_playoffs])
    return new_games



def run():
    games = pandas.DataFrame(columns = ["date","team_id","pts","opp_id","opp_pts","is_playoffs"])
    pages = ["week-" + str(i) for i in range(1,9)]# + ['playoffs','championship-weekend']

    for page in pages:
        new_games = pandas.DataFrame(get_weeks_games(page),columns = ["date","team_id","pts","opp_id","opp_pts","is_playoffs"])

        games = pandas.concat([games,new_games],ignore_index=True)

    games["is_playoffs"] = games["is_playoffs"].astype(int)
    games.to_csv("2019_audl_games.csv")



if __name__ == "__main__":
    run()
