import pandas as pd

from rating.result_fetcher import ResultFetcher
from rating.elo import Elo538nfl

results = None
if True:
    results = pd.read_csv('rating/audl_games_w_neutral.csv')
else:
    with ResultFetcher() as fetcher:
        results = fetcher.get_results()

elo_rater = Elo538nfl()
historical_elos = elo_rater.blank_run(results)

if __name__ == '__main__':
    historical_elos.to_csv('rating/data/audl_elo.csv', index=False)
else:
    h = historical_elos
