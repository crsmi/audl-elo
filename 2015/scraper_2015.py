import requests
from bs4 import BeautifulSoup
import pandas
import re
import datetime

def get_href(s):
    regex = r"/teams/(\w+)"
    match = re.search(regex,s)
    return match.group(1)

def get_weeks_games():
    new_games = []
    teams = pandas.read_csv("2015_audl_teams.csv")
    f = open("C:/Users/crsmi/Desktop/2015 Game Results _ The AUDL.html")
    content = f.read()
    parser = BeautifulSoup(content, 'html.parser')
    division = parser.find_all("div", id="block-system-main")
    score_tables = division[0].find_all("table")
    for score_table in score_tables:
        date_string = score_table.previous_sibling.previous_sibling.text
        dt = datetime.datetime.strptime(date_string,"%A, %B %d, %Y").date()
        str_date = dt.strftime("%m/%d/%Y")
        rows = score_table.find_all("tr")
        rows = rows[1:]
        print(date_string)
        is_playoffs = 0
        if (dt > datetime.date(2015,7,23)):
            is_playoffs = 1
        for row in rows:

            cols = row.find_all("td")
            away_team_href = get_href(cols[0].find_all('a')[0].get('href'))
            #print(away_team_href)
            away_team = teams[teams['href'] == away_team_href]['abbr'].iloc[0]
            if date_string == "Saturday, May 2, 2015" and cols[2].find_all('a') == []:
                home_team_href = "cannons"
            else:
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
                # Site has IND and DET flipped between home and away but has home and away scores right
                if str_date == "05/15/2015" and away_team == "DET" and home_team == "IND":
                    home_team = "DET"
                    away_team = "IND"
                # Site has RAL and CHA flipped b/w home and scores associated correctly, so need to change both.
                if str_date == "06/20/2015" and home_team == "RAL" and away_team == "CHA":
                    home_team = "CHA"
                    away_team = "RAL"
                    tmp_score = away_score
                    away_score = home_score
                    home_score = tmp_score
                new_games.append([str_date,home_team,home_score,away_team,away_score,is_playoffs])
    return new_games



def run():
    games = pandas.DataFrame(get_weeks_games(),columns = ["date","team_id","pts","opp_id","opp_pts","is_playoffs"])

    games.to_csv("2015_audl_games.csv")



if __name__ == "__main__":
    run()
