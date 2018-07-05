import requests
from bs4 import BeautifulSoup
import pandas
import re
import datetime

def get_href(s):
    regex = r"/teams/(\w+)"
    match = re.search(regex,s)
    return match.group(1)

def get_team_home_games(team):
    """ two teams don't exist anymore so we can't acess their team pages to scrape. We'll have to be creative
    luckily these two never played each other
    SOUTH,CHA,Charlotte Express,express
    MIDWEST,CIN,Cincinnati Revolution,revolution
    """
    discontinued_teams = ["express","revolution"]
    if team in discontinued_teams:
        return
    print("      ", team)
    new_games = []
    teams = pandas.read_csv("2016_audl_teams.csv")
    #Code to pull from web
    #response = requests.get("http://theaudl.com/teams/" + team + "/schedule/2016")
    #content = response.content
    #Updated for saved pages of 2017 teams historical(2016) results
    with open("team-pages/" + team + ".html", errors = 'ignore') as content:
        parser = BeautifulSoup(content, 'html.parser')


    score_table = parser.find_all("table")[0]


    is_playoffs = 0

    rows = score_table.find_all("tr")
    rows = rows[1:] #drop header
    for row in rows:
        print(row)
        print(row.text)
        if 'PLAYOFFS' in row.text:
            is_playoffs = 1
            continue
        cols = row.find_all("td")

        #find home team and only continue if it matches team we are getting games for
        #also include if the home team is a discontinued team
        home_team_href = get_href(cols[1].find_all('a')[0].get('href'))
        if home_team_href != team and home_team_href not in discontinued_teams:
            continue
        #Get team abbreviation
        home_team = teams[teams['href'] == home_team_href]['abbr'].iloc[0]

        #get date and format correctly for our table
        date_string = cols[0].text
        dt = datetime.datetime.strptime(date_string + " 2016","%B %d %Y").date()
        str_date = dt.strftime("%m/%d/%Y")

        #Get away team and translate to abbreviation
        away_team_href = get_href(cols[3].find_all('a')[0].get('href'))
        away_team = teams[teams['href'] == away_team_href]['abbr'].iloc[0]

        score_line = cols[2].text
        score_regex = r"(\d+)\s*\-\s*(\d+)"
        scores = re.match(score_regex,score_line)
        if scores == None:
            home_score = score_line
            away_score = score_line
        else:
            home_score = scores.group(1)
            away_score = scores.group(2)
            new_games.append([str_date,home_team,home_score,away_team,away_score,is_playoffs])
    return new_games

def run():
    games = pandas.DataFrame(columns = ["date","team_id","pts","opp_id","opp_pts","is_playoffs"])
    teams = pandas.read_csv("2016_audl_teams.csv")

    for team in teams["href"]:
        new_games = pandas.DataFrame(get_team_home_games(team),columns = ["date","team_id","pts","opp_id","opp_pts","is_playoffs"])

        games = pandas.concat([games,new_games],ignore_index=True)

    games["is_playoffs"] = games["is_playoffs"].astype(int)
    games.sort_values("date", inplace=True)
    games.reset_index(drop=True,inplace=True)
    games.to_csv("2016_audl_games.csv")



if __name__ == "__main__":
    run()
