import pandas as pd
import datetime
import math

# dict of teams having their home stadium host the playoffs each year
PLAYOFF_HOME_TEAMS = {2012 : "DET",
                      2013 : "CHI",
                      2014 : "TOR",
                      2015 : None,
                      2016 : "MAD",
                      2017 : "MTL",
                      2018 : "MAD",
                      2019 : "SJ"} #TODO Check this

# Lists of neutral games by game_id for each year
NEUTRAL_GAME_LIST = {2012 : ["201208110PHS"],
                     2013 : ["201308030TOR","201308040TOR"],
                     2014 : ["201407260MAD"],
                     2015 : ["201507250PIT","201508080MAD","201508080SJX","201508090SJX"],#Midwest playoffs on same day, PIT played CHI outside madison to see who would face madison  #Playoffs/Championship was in SJ but not in their home stadium
                     2016 : ["201608060DAL","201608070DAL"],
                     2017 : ["201708260MAD","201708260DAL","201708270SFX","201708270TOR"],
                     2018 : ["201808110DAL"],
                     2019 : ["201907200TOR","201908100NYX","201908100SDX","201908110NYX"]}

def three_pad(s):
    """Pads a string, s, to length 3 with trailing X's"""
    if len(s) < 3:
        return three_pad(s + "X")
    return s

def fill(teams,games,starting_game_number,year):
    """
    Fills in a DataFrame of games (from a specific year) with basic game information.

    Adds the following columns to games:
        gameorder - gives a basic ordering to games
        game_id - created from year + month + day + number_of_game + padded team id
        game_result - W or L depending on scores for the game
        game_location - H or N depending on if the game_id is in NEUTRAL_GAME_LIST
        year_id - lists year in each row
        fran_id - franchise of the home team looked up from teams
        opp_fran - franchise of the away team looked up from teams
        _iscopy - 0 to indicate these rows are initial rows after a copy process
                    is done later

    Parameters
    ----------
    teams: DataFrame
        dataFrame of information about teams that played in this set of games
    games: DataFrame
        list of games that is expanded with more game information
    starting_games_number: int
        number to be used for beginning of gameorder column
    year: int
        year to be used for year_id column

    Returns:
        None
            the games DataFrame is modified by the function

    """
    num_games = len(games)
    games["gameorder"] = pd.Series(range(starting_game_number,starting_game_number + num_games))
    game_ids = []
    game_result = []
    game_location = []

    # iterate over all games
    for i,row in games.iterrows():
        # Create game_id based on date and home team name
        # game_id = year + month + day + game_id_copy + padded team id
        dt = row['date'].split("/")
        game_id_copy = 0
        game_id = dt[2] + dt[0] + dt[1] + str(game_id_copy) + three_pad(row["team_id"])

        # game_id copy is used to indicate a more than one game between two
        # teams on the same day.
        # Look to see if game_id already exists and increment game_id_copy
        # until we get a unique id.
        while game_id in game_ids:
            game_id_copy += 1
            if game_id_copy > 9:
                raise Exception("game_id_copy can not be greater than 9. Are you sure there were 10 or more games between the same teams on the same day?")
            game_id = dt[2] + dt[0] + dt[1] + str(game_id_copy) + three_pad(row["team_id"])
        game_ids.append(game_id)

        # Determine if game is a win or loss for the home team
        if row["pts"] > row["opp_pts"]:
            game_result.append("W")
        else:
            game_result.append("L")

        # Check to see if the game is on the NEUTRAL_GAME_LIST for the given
        # year. If not it is a home game.
        if game_id in NEUTRAL_GAME_LIST[int(dt[2])]:
            game_location.append("N")
        else:
            game_location.append("H")

    # Add the columns to the dataframe
    games["game_id"] = pd.Series(game_ids)
    games["year_id"] = pd.Series([str(year)]*(num_games+1))
    # Lookup franchises from the team dataFrame
    games["fran_id"] = teams.loc[games["team_id"],"franchise"].values
    games["opp_fran"] = teams.loc[games["opp_id"],"franchise"].values
    games["game_location"] = pd.Series(game_location)
    games["game_result"] = pd.Series(game_result)
    games["_iscopy"] = 0

def calc(teams,games,starting_elo,k):
    """ Calculate elo change based on the game result and add to games.

        Acts on both teams and games and updates them without returning.

    Parameters
    ----------
    teams: DataFrame
        information about the teams playing in the given season
    games: DataFrame
        list of season games with information from fill
    starting_elo: list or int
        starting elos to be used at beginning of season
    k: int
        update parameter for elo algorithm
    """

    #K = 20
    #STARTING_ELO = 1500
    #Set home field advantage elo points
    HFA = 64
    #Set starting elo
    if type(starting_elo) != int:
        print(teams.shape[0],len(starting_elo))
    teams["elo"] = starting_elo

    # Initialize new columns
    new_columns = ["elo_i","elo_n","opp_elo_i","opp_elo_n","forecast"]
    for column in new_columns:
        games[column] = 0


    for i,row in games.iterrows():
        #Get starting elos
        row["elo_i"] = teams.loc[row["team_id"],"elo"]
        row["opp_elo_i"] = teams.loc[row["opp_id"],"elo"]

        #Determine home field advantage
        if row["game_location"] == 'N':
            home_field_advantage = 0
        else:
            home_field_advantage = HFA

        #Get winning and losing team's starting elos including home field advantage
        if row["game_result"] == "W":
            elow = row["elo_i"]+home_field_advantage
            elol = row["opp_elo_i"]
        elif row["game_result"] == "L":
            elol = row["elo_i"]+home_field_advantage
            elow = row["opp_elo_i"]


        #Calc Margin of Victory Mulitplier
        movm = math.log(abs(row['pts']-row['opp_pts'])+1)*(2.2/((elow-elol)*.001+2.2))

        dr = row["elo_i"]+home_field_advantage - row["opp_elo_i"]

        elo_change = movm * k * (1 - (1/(10**(-(elow-elol)/400)+1)))

        #Adjust elo
        if row["game_result"] == "W":
            row["elo_n"] = row["elo_i"] + elo_change
            row["opp_elo_n"] = row["opp_elo_i"] - elo_change
        elif row["game_result"] == "L":
            row["elo_n"] = row["elo_i"] - elo_change
            row["opp_elo_n"] = row["opp_elo_i"] + elo_change

        # Update elos in teams
        teams.loc[row["team_id"],"elo"] = row["elo_n"]
        teams.loc[row["opp_id"],"elo"] = row["opp_elo_n"]

        row["forecast"] = 1/(1+(10**(-dr/400))) #Predicted probability that the home team wins.

        games.iloc[i] = row



def duplicate(teams,games):
    """
    After calculating elo stats duplicate each row switching home and away info.

    To be used after fill() and calc(). Reverses home and away team information
    so there is a copy of each game with each teams information in the main team
    columns as well as opponent columns.

    Parameters
    ----------
    teams: DataFrame
        team information for the season of games
    games: DataFrame
        list of games for the season complete with elo information

    Returns
    -------
    DataFrame
        updated with duplicate games
    """

    # Switch basic home and away information for game copy
    duplicate_games = games.copy()
    duplicate_games["_iscopy"] = 1
    duplicate_games["team_id"] = games["opp_id"]
    duplicate_games["fran_id"] = games["opp_fran"]
    duplicate_games["opp_id"] = games["team_id"]
    duplicate_games["opp_fran"] = games["fran_id"]
    duplicate_games["pts"] = games["opp_pts"]
    duplicate_games["opp_pts"] = games["pts"]
    duplicate_games["elo_i"] = games["opp_elo_i"]
    duplicate_games["opp_elo_i"] = games["elo_i"]
    duplicate_games["elo_n"] = games["opp_elo_n"]
    duplicate_games["opp_elo_n"] = games["elo_n"]

    # Flip results and location
    w_flip = {"W":"L","L":"W","T":"T"}
    location_flip = {"H":"A","A":"H","N":"N"}

    duplicate_games["game_result"] = games["game_result"].map(w_flip)
    duplicate_games["game_location"] = games["game_location"].map(location_flip)
    duplicate_games["forecast"] = 1 - games["forecast"]

    # Merge the duplicates into the whole list
    games = pd.concat([games,duplicate_games])

    # Sort by gameorder,_iscopy
    games.sort_values(["gameorder","_iscopy"],inplace=True)
    games.reset_index(drop=True,inplace=True)

    # After Duplication and sorting add a column listing which game of the
    # season a game is for the team in team_id
    seasongame = []
    #Get seasongame counts
    teams["game_count"] = 0
    for i,row in games.iterrows():
        #Set seasongame
        teams.loc[row["team_id"],"game_count"] += 1
        seasongame.append(teams.loc[row["team_id"],"game_count"])
    games["seasongame"] = pd.Series(seasongame)
    return games



def calc_season_elo(year,starting_elo,k,starting_game_number):
    """Create a dataframe of games for an AUDL season with elo information.

    This function creates the games and teams DataFrames, then calls the
    functions fill, calc, and duplicate in order to fill in all information for
    a season. Finally, it reorders the columns and returns the results.

    Parameters
    ----------
    year: int
        year of the season
    starting_elo: list
        list of starting elo's for each team playing in the season
    k: int
        k value to be used in Elo algorithm
    starting_game_number: int
        number to start the ordering of games with

    Returns:
        games dataframe with all elo information for the season
        teams dataframe with current elo column added
    """
    teams_filename = str(year) + "/" + str(year) + "_audl_teams.csv"
    games_filename = str(year) + "/" + str(year) + "_audl_games.csv"
    teams = pd.read_csv(teams_filename)
    teams.set_index('abbr',inplace=True)
    games = pd.read_csv(games_filename,index_col=0)

    fill(teams,games,starting_game_number,year)
    calc(teams,games,starting_elo,k)
    games = duplicate(teams,games)

    column_order = ["gameorder","game_id","_iscopy","year_id","date","seasongame","is_playoffs","team_id","fran_id","pts","elo_i","elo_n","opp_id","opp_fran","opp_pts","opp_elo_i","opp_elo_n","game_location","game_result","forecast"]
    games = games[column_order]

    return games, teams

def generate(K=20,SE=1500,TE=1500):
    """Create a dataframe of elo information for all AUDL games.

    Iterate over years from 2012 to 2018. Using <year>_audl_games.csv files get
    elo information for each season and collate them into one large dataframe.
    Before each season this function handles updating team elos for the start
    of the next season.

    Parameters
    ----------
    K: int
        update value for our elo algorithm
    SE: int
        starting elo value to use for each teams first season
    TE: int
        target elo to regress each team to after each season

    Returns
    -------
    DataFrame
        containing all game and elo information for all AUDL games
    """
    game_number = 1
    games = pd.DataFrame(columns = ["gameorder","game_id","_iscopy","year_id","date","seasongame","is_playoffs","team_id","fran_id","pts","elo_i","elo_n","opp_id","opp_fran","opp_pts","opp_elo_i","opp_elo_n","game_location","game_result","forecast"])
    years = [2012,2013,2014,2015,2016,2017,2018,2019]
    starting_elo = SE
    for year in years:
        new_games, previous_teams = calc_season_elo(year,starting_elo,K,game_number)
        games = pd.concat([games,new_games],ignore_index=True)
        game_number = int(games["gameorder"].iloc[-1])+1

        #update elos for the beginning of the next season
        if year != years[-1]:
            next_teams = pd.read_csv(str(year + 1) + "/" + str(year + 1) + "_audl_teams.csv")
            prev_elo = []
            for i,row in next_teams.iterrows():
                if row['franchise'] in previous_teams["franchise"].values:
                    # Revert to mean by 1/3
                    team_elo = previous_teams.set_index('franchise').loc[row['franchise']]["elo"]
                    prev_elo.append((2*team_elo + TE) / 3)
                else:
                    prev_elo.append(SE)
            starting_elo = prev_elo
            #Update elo for start of next season
            #Revert to mean by 1/3
            #starting_elo = ((2*next_teams["prev_elo"] + TE) / 3).tolist()

    int_columns = ["gameorder","_iscopy","seasongame","is_playoffs","pts","opp_pts"]
    for c in int_columns:
        games[c] = games[c].astype(int)
    return games

if __name__ == "__main__":
    # When called as a script, generate the elo table using default k of 20 then save to file
    games = generate(20)
    games.to_csv("audl_elo.csv",index=False)
