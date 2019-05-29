import pandas as pd
import numpy as np
from math import log as ln

from abc import ABC, abstractmethod


class Rater(ABC):

    @abstractmethod
    def blank_run(self, results):
        pass

    @abstractmethod
    def get_uninformed_default(self):
        pass


class EloRater(Rater):

    def __init__(self,
                 default_rating=1500,
                 k=20,
                 hfa=64,
                 regression_factor=1/3,
                 MOVF = '538nfl'):
            """
            fundamental elo model is described at:
            https://math.stackexchange.com/questions/1731991/why-does-the-elo-rating-system-work
            the specifics of including home field advantage and margin of victory are
            detailed in the FiveThirtyEight article:
            https://fivethirtyeight.com/methodology/how-our-nfl-predictions-work/
            :param default_rating: starting elo for a team with no history
            :param k: Elo k-factor weighs how much each result changes a team's rating
            :param hfa: home field advantage in elo rating points
            :param regression_factor: amount to regress each team towards default_rating before each new season
            """
            self._default_rating = default_rating
            self._k = k
            self._hfa = hfa
            self._regression_factor = regression_factor
            self._MOVF = MOVF

    def batch_run(self, previous_ratings, results):
        """
        run the elo algorithm continuing from a set of starting elo ratings
        :param previous_ratings: a dictionary of teams starting elo ratings
        :param results: game results to add to the elo results
        :return: a dataframe including elo scores for each game result
        """
        elo_series = pd.DataFrame()
        elo_ratings = previous_ratings.copy()#Store current team elo ratings as we iterate through the season results

        for game in results.itertuples():
            #Grab a teams elo rating before the game
            elo1_pre = elo_ratings[game.team1]
            elo2_pre = elo_ratings[game.team2]

            elo_diff = elo1_pre - elo2_pre + self._hfa * (1 - game.neutral) # eliminates hfa at neautral sites

            #Calculate both teams' elo probability
            elo_prob1 = 1 / (10**(-elo_diff / 400) + 1)
            elo_prob2 = 1 - elo_prob1

            #Calculate elo change
            point_diff = game.score1 - game.score2
            game_result = 1 if point_diff > 0 else (0 if point_diff < 0 else .5)
            delta = game_result - elo_prob1
            winner_elo_diff = elo_diff if game_result else -elo_diff
            if self.MOVM = '538nfl':
                movm = ln(abs(point_diff) + 1) * (2.2 / (winner_elo_diff * .001 + 2.2))
            else:
                movm = 1
            elo_change = self._k * movm * delta

            #test validation against original model
            if game_result == .5:
                elo_change = 0

            #Calculate both teams' elo rating after the game
            elo1_post = elo1_pre + elo_change
            elo2_post = elo2_pre - elo_change

            #Update current elos for both teams
            elo_ratings[game.team1] = elo1_post
            elo_ratings[game.team2] = elo2_post

            #Add line to the DataFrame
            elo_series = elo_series.append({"elo1_pre": elo1_pre,
                                    "elo2_pre": elo2_pre,
                                    "elo_prob1": elo_prob1,
                                    "elo_prob2": elo_prob2,
                                    "elo1_post": elo1_post,
                                    "elo2_post": elo2_post},
                                 ignore_index=True)
        return elo_series, elo_ratings

    def blank_run(self, results):
        """
        run the elo algorithm from the top with no previous ratings
        :param results: game results to run through to calculate elo rating
        :return: a dataframe including elo scores for each game result
        """
        starting_elos = {team: self._default_rating for team in
                            pd.concat([results['team1'],results['team2']]).unique()}

        elos = starting_elos.copy()

        season_grouped_results = results.groupby('season')

        col_order = ['date','season','neutral','playoff','team1','team2',
                        'elo1_pre','elo2_pre','elo_prob1','elo_prob2','elo1_post',
                        'elo2_post','score1','score2']

        all_results = pd.DataFrame(columns = col_order)

        for season, results in season_grouped_results:
            season_results, elos  = self._update_single_season(elos,results.reset_index(drop=True))
            season_results['season'] = season
            all_results = all_results.append(season_results, ignore_index=True)

        return all_results[col_order]

    def get_current_elos(results):
        home_elos = results.groupby('team1').last()
        away_elos = results.groupby('team2').last()
        current_elos = {}
        for team in home_elos.index.append(away_elos.index).unique():
            current_elos[team] = min(home_elos.loc[team,'elo1_post'],away_elos.loc[team,'elo2_post'])
        return current_elos

    def _update_single_season(self, previous_ratings, results):
        """ Iterate through a whole season """
        #To start season, regress each team's previous rating to the mean by 1/3.
        beginning_ratings = {k: ((self._regression_factor * self._default_rating) + ((1 - self._regression_factor) * v)) for k, v in previous_ratings.items()}
        #Create new previous rating for new teams TODO probably not necessary
        for team in np.union1d(results['team1'].unique(),results['team2'].unique()):
            if team not in beginning_ratings:
                beginning_ratings[team] = self._default_rating

        elo_results, end_of_season_ratings = self.batch_run(beginning_ratings, results)

        #Add elo ratings to results
        results = pd.concat([results, elo_results], axis=1)

        return results, end_of_season_ratings

    def get_uninformed_default(self):
        return self._default_rating

    def __str__(self):
        return f"Elo538nfl_k={self._k}_hfa={self._hfa}_default={self._default_rating}"

class Elo538nfl(EloRater):
    def __init__(self,
                 default_rating=1500,
                 k=20,
                 hfa=64,
                 regression_factor=1/3):
       EloRater.__init__(self, default_rating, k, hfa, regression_factor,
                        MOVF = '538nfl')


def short_to_long(gelo):
    #list of long-form columns
    col_order = ["gameorder","game_id","_iscopy","year_id","date","seasongame","is_playoffs","team_id","fran_id","pts","elo_i","elo_n","opp_id","opp_fran","opp_pts","opp_elo_i","opp_elo_n","game_location","game_result","forecast"]
    #Carryover some columns
    col_name_map = {'season':'year_id',
                    'neutral':'game_location',
                    'team1':'team_id',
                    'team2':'opp_id',
                    'elo1_pre':'elo_i',
                    'elo2_pre':'opp_elo_i',
                    'elo_prob1':'forecast',
                    'elo1_post':'elo_n',
                    'elo2_post':'opp_elo_n',
                    'score1':'pts',
                    'score2':'opp_pts'}
    drop_cols = ['elo_prob2']
    audl_teams = pd.read_csv('../audl_teams.csv',index_col='abbr')
    audl_teams['last_season'] = audl_teams['last_season'].fillna(2019).astype(int) #CHANGE 2019 TO CURRENT YEAR
    #NOT QUITE RIGHT BUT MAYBE ON THE RIGHT TRACK
    fran_to_team_abbr_map = audl_teams.apply(lambda r: {year:r['franchise'] for year in range(int(r['first_season']),int(r['last_season'])+1)}, axis=1)
    audl_teams['abbr'] = audl_teams.index
    fran_map = {}
    fran_group = audl_teams.groupby('franchise')
    for fran,group in fran_group:
        fran_map[fran] = {{year:row['abbr'] for year in range(int(row['first_season']),int(row['last_season'])+1)} for _,row in group.iterrows()}
    #add and calculate gameorder
    gelo['gameorder'] = pd.Series(range(1,1+len(gelo)))
    gelo['fran_id'] = gelo['team1'].map(audl_teams['franchise'])
    #translate team1 and team2 to historically correct team abbr
    def abbr_map(row):

    gelo['team_id'] = gelo['team1'].map()

    #create game_id

    #carry over date
    #translate playoff from 0/letters to 1s
    #team1 -> team_id w/ historial abbr translation
    #translate to fran_id
    #score1 -> PTS

    #team2 -> opp_id w/ historical abbr translation

    #calculate seasongame AFTER DUPLICATION
    gelo['seasongame'] = gelo.gropuby(['team_id','season']).size()indices #not quite what we weant
    pass




if __name__ == "__main__":
    rater = Elo538nfl()
    results = pd.read_csv('rating/audl_games_w_neutral_and_correct_team.csv')
    h = rater.blank_run(results)
    h.to_csv('rating/data/test_audl_elo.csv', index=False)
