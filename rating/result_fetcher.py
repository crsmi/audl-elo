from datetime import datetime
import pandas as pd

class ResultFetcher:
    def __init__(self):
        pass

    def get_results(self,
                    min_date=None,
                    max_date=None):
        """
        fetch all audl results within date range
        #TODO documentation
        """

        #mid_date = datetime.min.date() if min_date is None else min_date
        #max_date = datetime.max_date() if max_date is None else max_date

        # if min_date > max_date:
        #     raise ValueError('min_date argument cannot be great than max_date argument')

        col_map = {'team_id': 'team1',
                   'opp_id': 'team2',
                   'pts': 'score1',
                   'opp_pts': 'score2'}

        col_order = ['date','season','neutral','playoff','team1','team2','score1','score2']

        results_df = pd.DataFrame()

        for season in ['2012','2013','2014','2015','2016','2017','2018']:
            season_games = pd.read_csv(season + '/' + season + '_audl_games.csv', index_col = 0)
            season_games = season_games.rename(col_map,axis='columns')
            season_games['season'] = season_games['date'].str[-4:]
            season_games['neutral'] = 0
            season_games['playoff'] = season_games['is_playoffs']

            results_df = results_df.append(season_games[col_order], ignore_index=True)

        return results_df

if __name__ == "__main__":
    fetcher = ResultFetcher()
    results = fetcher.get_results()
    results.to_csv('rating/audl_games.csv', index=False)
