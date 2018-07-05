def formatDate(inDate):
    inDate = inDate.split("/")
    return inDate[2] + "-" + inDate[0] + "-" + inDate[1]


import pandas as pd
import psycopg2
from sqlalchemy import create_engine

#contants
postgres_username = "postgres"
postgres_password = "tikki"


#Setup SQLAchemy engine
engine = create_engine('postgresql://' + postgres_username + ":" + postgres_password + '@localhost:5432/audl_elo')
#df.to_sql('table_name', engine)


#read in information
games = pd.read_csv("audl_elo.csv")
franchises = pd.read_csv("audl_franchises.csv")
teams = pd.read_csv("audl_teams.csv")

#Modify dates for SQL
games["date"] = games["date"].apply(formatDate)

#Create tables
games.to_sql("games",engine,if_exists='replace')
teams.to_sql("teams",engine,if_exists='replace',index=False)
franchises.to_sql("franchises",engine,if_exists='replace',index=False)


#Create connection and modify tables
conn = psycopg2.connect(dbname = "audl_elo", user = postgres_username)
conn.autocommit=True
cur = conn.cursor()
cur.execute("ALTER TABLE franchises ADD PRIMARY KEY(franchise);")
cur.execute("ALTER TABLE teams ADD PRIMARY KEY(abbr);")
cur.execute("ALTER TABLE teams ADD FOREIGN KEY(franchise) REFERENCES franchises(franchise)")
cur.execute("ALTER TABLE games ADD FOREIGN KEY(team_id) REFERENCES teams(abbr);")
cur.execute("ALTER TABLE games ADD FOREIGN KEY(fran_id) REFERENCES franchises(franchise)")
cur.execute("ALTER TABLE games ADD FOREIGN KEY(opp_id) REFERENCES teams(abbr);")
cur.execute("ALTER TABLE games ADD FOREIGN KEY(opp_fran) REFERENCES franchises(franchise)")


#close connection
conn.close()
