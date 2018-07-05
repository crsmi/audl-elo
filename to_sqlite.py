def formatDate(inDate):
    inDate = inDate.split("/")
    return inDate[2] + "-" + inDate[0] + "-" + inDate[1]

import pandas as pd
import sqlite3
import time

#read in information
games = pd.read_csv("audl_elo.csv")
franchises = pd.read_csv("audl_franchises.csv")
teams = pd.read_csv("audl_teams.csv")

#Modify dates for SQL
games["date"] = games["date"].apply(formatDate)



#Connect and create tables
conn = sqlite3.connect("audl_elo.db")
#Incase all sqlite code in try/finally so it gets closed no matter what.
try:
    games.to_sql("games",conn,if_exists='replace')
    franchises.to_sql("franchises",conn,if_exists='replace',index=False)
    teams.to_sql("teams",conn,if_exists='replace',index=False)

    #Create relations
    #conn.execute("PRAGMA foreign_keys = OFF")

    #Set franchises table
    franchises_two_create = '''CREATE TABLE franchises_prime (
    franchise TEXT PRIMARY KEY,
    division TEXT,
    abbr TEXT,
    team_name TEXT,
    href TEXT,
    first_season INTEGER,
    last_season INTEGER);'''
    conn.execute(franchises_two_create)
    franchise_info = conn.execute("SELECT * FROM franchises;").fetchall()
    insert_franchise_info = "INSERT INTO franchises_prime (franchise,division,abbr,team_name,href,first_season,last_season) VALUES (?,?,?,?,?,?,?);"
    conn.executemany(insert_franchise_info,franchise_info)
    conn.execute("DROP TABLE franchises;")
    conn.execute("ALTER TABLE franchises_prime RENAME TO franchises;")

    teams_two_create = '''CREATE TABLE teams_two (
    division TEXT,
    abbr TEXT PRIMARY KEY,
    team_name TEXT,
    franchise TEXT REFERENCES franchises(franchise),
    href TEXT,
    first_season INTEGER,
    last_season INTEGER);'''
    conn.execute(teams_two_create)
    team_info = conn.execute("SELECT * FROM teams;").fetchall()
    insert_team_info = "INSERT INTO teams_two (division,abbr,team_name,franchise,href,first_season,last_season) VALUES (?,?,?,?,?,?,?);"
    conn.executemany(insert_team_info,team_info)
    conn.execute("DROP TABLE teams;")
    conn.execute("ALTER TABLE teams_two RENAME TO teams;")

    games_two_create = '''CREATE TABLE games_two (
    id INTEGER PRIMARY KEY,
    gameorder INTEGER,
    game_id TEXT,
    _iscopy INTEGER,
    year_id INTEGER,
    date TEXT,
    seasongame INTEGER,
    is_playoffs INTEGER,
    team_id TEXT REFERENCES teams(abbr),
    fran_id TEXT REFERENCES franchises(franchise),
    pts INTEGER,
    elo_i REAL,
    elo_n REAL,
    opp_id TEXT REFERENCES teams(abbr),
    opp_fran TEXT REFERENCES franchises(franchise),
    opp_pts INTEGER,
    opp_elo_i REAL,
    opp_elo_n REAL,
    game_location TEXT,
    game_result TEXT,
    forecast REAL);'''
    conn.execute(games_two_create)
    game_info = conn.execute("SELECT * FROM games;").fetchall()
    insert_game_info = "INSERT INTO games_two (id,gameorder,game_id,_iscopy,year_id,date,seasongame,is_playoffs,team_id,fran_id,pts,elo_i,elo_n,opp_id,opp_fran,opp_pts,opp_elo_i,opp_elo_n,game_location,game_result,forecast) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
    conn.executemany(insert_game_info,game_info)
    conn.execute("DROP TABLE games;")
    conn.execute("ALTER TABLE games_two RENAME TO games;")


    #Check Tables
    #print(conn.execute("PRAGMA table_info(games)").fetchall())
    #print(conn.execute("PRAGMA table_info(franchises)").fetchall())
    #print(conn.execute("PRAGMA table_info(teams)").fetchall())
    #print(conn.execute("SELECT sql FROM sqlite_master WHERE name='games';").fetchall())
    #print(conn.execute("SELECT * FROM teams INNER JOIN franchises ON teams.franchise = franchises.franchise;").fetchall())
    #query = "SELECT * FROM games INNER JOIN teams home on games.team_id = home.abbr INNER JOIN teams away on games.opp_id = away.abbr WHERE team_id = 'MAD';"
    query = "SELECT * FROM games INNER JOIN franchises home on games.fran_id = home.franchise INNER JOIN franchises away on games.opp_fran = away.franchise WHERE date > '2017-01-01';"
    mad_games = conn.execute(query).fetchall()
    for row in mad_games:
        print(row)
finally:
    #Close connection
    conn.close()
