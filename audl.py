 class Game():
     def __init__(self,dataSeries):
         self.game_id = dataSeries['game_id']
         self.year_id = dataSeries['year_id']
         self.date = dataSeries['date']
         self.seasongame = dataSeries['seasongame']
         self.is_playoffs = dataseries['is_playoffs']
         self.home_team = Team()
         self.home_score =
         self.away_team = Team()
         self.away_score =
         self.forecast = 


 class Team():
     def __init__(self,dataSeries):
         self.team_name =
         self.franchise =
         self.abbr =
         self.website =
         self.division =
         self.seasons = []

 class Franchise():
     def __init__(self,dataSeries):
         self.franchise_name =
         self.divistoin =
         self.team_list = []
         self.seasons = []
