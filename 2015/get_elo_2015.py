import pandas as pd
import datetime
import math

def four_pad(s):
    if len(s) < 4:
        return four_pad("0" + s)
    return s

def fill(teams,games):
    num_games = len(games)
    games["gameorder"] = pd.Series(range(1,num_games+1))
    game_ids = []
    game_result = []

    for i,row in games.iterrows():
        #Create game_id based on date and home team name
        dt = row['date'].split("/")
        game_id = dt[2] + dt[0] + dt[1] + four_pad(row["team_id"])
        game_ids.append(game_id)
        if row["pts"] > row["opp_pts"]:
            game_result.append("W")
        else:
            game_result.append("L")

    games["game_id"] = pd.Series(game_ids)
    games["year_id"] = pd.Series(["2015"]*(num_games+1))
    games["game_location"] = "H"
    games["game_result"] = pd.Series(game_result)
    games["_iscopy"] = 0

def calc(teams,games):
    K = 20
    STARTING_ELO = 1500
    #Set starting elo
    teams["elo"] = STARTING_ELO
    new_columns = ["elo_i","elo_n","opp_elo_i","opp_elo_n"]
    for column in new_columns:
        games[column] = 0


    for i,row in games.iterrows():
        #Get starting elos
        row["elo_i"] = teams.loc[row["team_id"],"elo"]
        row["opp_elo_i"] = teams.loc[row["opp_id"],"elo"]
        #get winning and losing team's starting elos
        if row["game_result"] == "W":
            elow = row["elo_i"]+100
            elol = row["opp_elo_i"]
        elif row["game_result"] == "L":
            elol = row["elo_i"]+100
            elow = row["opp_elo_i"]


        dr = elow-elol
        #Calc Margin of Victory Mulitplier
        movm = math.log(abs(row['pts']-row['opp_pts'])+1)*(2.2/((dr)*.001+2.2))

        elo_change = movm * K * (1 - (1/(10**(-dr/400)+1)))


        #Adjust elo
        if row["game_result"] == "W":
            row["elo_n"] = row["elo_i"] + elo_change
            row["opp_elo_n"] = row["opp_elo_i"] - elo_change
        elif row["game_result"] == "L":
            row["elo_n"] = row["elo_i"] - elo_change
            row["opp_elo_n"] = row["opp_elo_i"] + elo_change

        #update elos in teams
        teams.loc[row["team_id"],"elo"] = row["elo_n"]
        teams.loc[row["opp_id"],"elo"] = row["opp_elo_n"]
        games.iloc[i] = row

        games["forecast"] = 1/(1+(10**-((games["elo_i"]-games["opp_elo_i"]+100)/400)))

def duplicate(teams,games):
    #After calculating elo stats duplicate each row for easy analysis across each team's seasongame

    #Duplicate games for away teams
    duplicate_games = games.copy()
    duplicate_games["_iscopy"] = 1
    duplicate_games["team_id"] = games["opp_id"]
    duplicate_games["opp_id"] = games["team_id"]
    duplicate_games["pts"] = games["opp_pts"]
    duplicate_games["opp_pts"] = games["pts"]
    duplicate_games["elo_i"] = games["opp_elo_i"]
    duplicate_games["opp_elo_i"] = games["elo_i"]
    duplicate_games["elo_n"] = games["opp_elo_n"]
    duplicate_games["opp_elo_n"] = games["elo_n"]

    w_flip = {"W":"L","L":"W"}
    home_flip = {"H":"A","A":"H","N":"N"}

    duplicate_games["game_result"] = games["game_result"].map(w_flip)
    duplicate_games["game_location"] = games["game_location"].map(home_flip)
    duplicate_games["forecast"] = 1 - games["forecast"]

    #merge the two
    games = pd.concat([games,duplicate_games])

    #sort by gameorder,_iscopy
    games.sort_values(["gameorder","_iscopy"],inplace=True)
    games.reset_index(drop=True,inplace=True)
    #After Duplication and sorting
    seasongame = []
    #Get seasongame counts
    teams["game_count"] = 0
    for i,row in games.iterrows():
        #Set seasongame
        teams.loc[row["team_id"],"game_count"] += 1
        seasongame.append(teams.loc[row["team_id"],"game_count"])
    games["seasongame"] = pd.Series(seasongame)
    return games



if __name__ == "__main__":
    teams = pd.read_csv("2015_audl_teams.csv")
    teams.set_index('abbr',inplace=True)
    games = pd.read_csv("2015_audl_games.csv",index_col=0)

    fill(teams,games)
    calc(teams,games)
    games = duplicate(teams,games)

    column_order = ["gameorder","game_id","_iscopy","year_id","date","seasongame","is_playoffs","team_id","pts","elo_i","elo_n","opp_id","opp_pts","opp_elo_i","opp_elo_n","game_location","game_result","forecast"]
    games = games[column_order]

    games.to_csv("2015_audl_elo.csv")
