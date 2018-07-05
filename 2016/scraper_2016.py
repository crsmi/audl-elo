import requests
from bs4 import BeautifulSoup
import pandas
import re

def get_href(s):
    regex = r"/teams/(\w+)"
    match = re.search(regex,s)
    return match.group(1)

def get_weeks_games(week):
    new_games = []
    teams = pandas.read_csv("2016_audl_teams.csv")
    response = requests.get("http://theaudl.com/scores/2016/" + week)
    content = response.content
    parser = BeautifulSoup(content, 'html.parser')
    score_tables = parser.find_all("table")
    is_playoffs = 0
    if week == "postseason":
        is_playoffs = 1
    for score_table in score_tables:
        rows = score_table.find_all("tr")
        rows = rows[1:]
        for row in rows:
            print(row)
            cols = row.find_all("td")
            if week == "Week7" and cols[0].find_all('a') == []:
                away_team_href = "cascades"
            else:
                away_team_href = get_href(cols[0].find_all('a')[0].get('href'))
            print(week,away_team_href)
            away_team = teams[teams['href'] == away_team_href]['abbr'].iloc[0]
            home_team_href = get_href(cols[2].find_all('a')[0].get('href'))
            home_team = teams[teams['href'] == home_team_href]['abbr'].iloc[0]
            score_line = cols[1].text
            score_regex = r"(\d+)\s*\-\s*(\d+)"
            scores = re.match(score_regex,score_line)
            if scores == None:
                home_score = score_line
                away_score = score_line
            else:
                home_score = scores.group(2)
                away_score = scores.group(1)
                new_games.append([home_team,home_score,away_team,away_score,is_playoffs])
    return new_games

def run():
    games = pandas.DataFrame(columns = ["team_id","pts","opp_id","opp_pts","is_playoffs"])
    pages = []
    for i in range(1,16):
        pages.append("Week" + str(i))
    pages.append("postseason")

    for page in pages:
        new_games = pandas.DataFrame(get_weeks_games(page),columns = ["team_id","pts","opp_id","opp_pts","is_playoffs"])

        games = pandas.concat([games,new_games],ignore_index=True)

    games["is_playoffs"] = games["is_playoffs"].astype(int)
    
    games.to_csv("2016_audl_games.csv")



if __name__ == "__main__":
    run()
