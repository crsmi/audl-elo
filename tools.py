import datetime
import pandas as pd
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_team(team):
    years = [2012,2013,2014,2015,2016,2017]
    g = pd.read_csv("audl_elo.csv")

    dates = pd.to_datetime(g[(g["team_id"] == team)]["date"])
    elo = g[(g["team_id"] == team)]["elo_n"]

    plt.plot(dates,elo)
    plt.show()

def plot_team_b(team):
    years = [2012,2013,2014,2015,2016,2017]
    g = pd.read_csv("audl_elo.csv")

    fig, axs = plt.subplots(1,len(years),sharey=True)
    for i in range(len(axs)):
        #Plotting
        dates = pd.to_datetime(g[(g["team_id"] == team) & (g["year_id"] == years[i])]["date"])
        elo = g[(g["team_id"] == team) & (g["year_id"] == years[i])]["elo_n"]
        axs[i].plot(dates,elo)
        #Formatting
        axs[i].xaxis.set_ticks_position('none')
        axs[i].set_xlabel(str(years[i]))
        axs[i].tick_params('x',labelbottom=False)
        axs[i].set_ylim(1050,1950)
        if i == 0:
            axs[i].yaxis.tick_left()
            axs[i].set_yticks(range(1100,2000,100))
        if i != len(axs)-1:
            axs[i].spines['right'].set_visible(False)
        if i != 0:
            axs[i].yaxis.set_ticks_position('none')
            axs[i].spines['left'].set_visible(False)
    plt.show()

def plot_teams(teams):
    years = [2012,2013,2014,2015,2016,2017]
    g = pd.read_csv("audl_elo.csv")


    #plt.style.use('fivethirtyeight')
    fig, axs = plt.subplots(1,len(years),sharey=True)
    for i in range(len(axs)):
        season_start = pd.to_datetime(g[(g["year_id"] == years[i])]["date"]).min() - datetime.timedelta(7)
        season_end= pd.to_datetime(g[(g["year_id"] == years[i])]["date"]).max()
        #Plotting
        colors = ['b','g','r','c','m','y','k']
        for j,team in enumerate(teams):
            dates = pd.to_datetime(g[(g["team_id"] == team) & (g["year_id"] == years[i])]["date"])
            if dates.shape[0] > 0:
                dates = pd.Series(season_start).append(dates)
            elo = g[(g["team_id"] == team) & (g["year_id"] == years[i])]["elo_n"]
            if elo.shape[0] > 0:
                start_elo = g[(g["team_id"] == team) & (g["year_id"] == years[i])]["elo_i"].iloc[0]
                elo = pd.Series(start_elo).append(elo)
            axs[i].plot(dates,elo,color = colors[j])
        #Formatting
        axs[i].xaxis.set_ticks_position('none')
        axs[i].set_xlabel(str(years[i]))
        axs[i].tick_params('x',labelbottom=False)
        axs[i].set_ylim(1050,1950)
        axs[i].set_xlim(season_start,season_end)
        axs[i].grid(True)
        if i == 0:
            axs[i].yaxis.tick_left()
            axs[i].set_yticks(range(1100,2000,100))
        if i != len(axs)-1:
            axs[i].spines['right'].set_visible(False)
        if i != 0:
            axs[i].yaxis.set_ticks_position('none')
            axs[i].spines['left'].set_visible(False)
        if i == len(axs)-1:
            axs[i].legend(teams)
    plt.show()

def better_plot(team):
    years = mdates.YearLocator()   # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    # load a numpy record array from yahoo csv data with fields date,
    # open, close, volume, adj_close from the mpl-data/example directory.
    # The record array stores python datetime.date as an object array in
    # the date column
    g = pd.read_csv("audl_elo.csv")
    dates = pd.to_datetime(g[(g["team_id"] == team)]["date"])
    elo = g[(g["team_id"] == team)]["elo_n"]

    fig, ax = plt.subplots()
    ax.plot(dates, elo)


    # format the ticks
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)

    datemin = datetime.date(dates.min().year, 1, 1)
    datemax = datetime.date(dates.max().year + 1, 1, 1)
    ax.set_xlim(datemin, datemax)



    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    #ax.format_ydata = price
    ax.grid(True)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    plt.show()

def plot_teams_one(target_team):
    years = [2012,2013,2014,2015,2016,2017]
    g = pd.read_csv("audl_elo.csv")
    teams = g["team_id"].unique()
    teams_df = pd.read_csv("audl_teams.csv")
    team_name = teams_df[teams_df['abbr'] == target_team]["team_name"].iloc[0]

    #plt.style.use('fivethirtyeight')
    fig, axs = plt.subplots(1,len(years),sharey=True)
    fig.suptitle(team_name, fontsize=20)
    for i in range(len(axs)):
        season_start = pd.to_datetime(g[(g["year_id"] == years[i])]["date"]).min() - datetime.timedelta(7)
        season_end= pd.to_datetime(g[(g["year_id"] == years[i])]["date"]).max()
        #Plotting
        colors = ['b','g','r','c','m','y','k']
        for j,team in enumerate(teams):
            dates = pd.to_datetime(g[(g["team_id"] == team) & (g["year_id"] == years[i])]["date"])
            if dates.shape[0] > 0:
                dates = pd.Series(season_start).append(dates)
            elo = g[(g["team_id"] == team) & (g["year_id"] == years[i])]["elo_n"]
            if elo.shape[0] > 0:
                start_elo = g[(g["team_id"] == team) & (g["year_id"] == years[i])]["elo_i"].iloc[0]
                elo = pd.Series(start_elo).append(elo)
            if team == target_team:
                axs[i].plot(dates,elo,color = 'b',linewidth=3)
            else:
                axs[i].plot(dates,elo,color = '0.6',linewidth=1)
        #Formatting
        axs[i].xaxis.set_ticks_position('none')
        axs[i].set_xlabel(str(years[i]))
        axs[i].tick_params('x',labelbottom=False)
        axs[i].set_ylim(1050,1950)
        axs[i].set_xlim(season_start,season_end)
        axs[i].grid(True)
        if i == 0:
            axs[i].yaxis.tick_left()
            axs[i].set_yticks(range(1100,2000,100))
        if i != len(axs)-1:
            axs[i].spines['right'].set_visible(False)
        if i != 0:
            axs[i].yaxis.set_ticks_position('none')
            axs[i].spines['left'].set_visible(False)
    plt.show()

def plot_teams_many(target_teams,title = "Elo Ratings"):
    years = [2012,2013,2014,2015,2016,2017]
    g = pd.read_csv("audl_elo.csv")
    teams = g["team_id"].unique()
    teams_df = pd.read_csv("audl_teams.csv")


    #plt.style.use('fivethirtyeight')
    fig, axs = plt.subplots(1,len(years),sharey=True)
    fig.suptitle(title, fontsize=20)
    for i in range(len(axs)):
        season_start = pd.to_datetime(g[(g["year_id"] == years[i])]["date"]).min() - datetime.timedelta(7)
        season_end= pd.to_datetime(g[(g["year_id"] == years[i])]["date"]).max()
        #Plotting
        colors = ['b','g','r','c','m','y','k']
        count = 0
        teams_legend = []
        for j,team in enumerate(teams):
            dates = pd.to_datetime(g[(g["team_id"] == team) & (g["year_id"] == years[i])]["date"])
            if dates.shape[0] > 0:
                dates = pd.Series(season_start).append(dates)
            elo = g[(g["team_id"] == team) & (g["year_id"] == years[i])]["elo_n"]
            if elo.shape[0] > 0:
                start_elo = g[(g["team_id"] == team) & (g["year_id"] == years[i])]["elo_i"].iloc[0]
                elo = pd.Series(start_elo).append(elo)
            if team in target_teams:
                handle, = axs[i].plot(dates,elo,color = colors[count],linewidth=2,label=team)
                count += 1
                teams_legend.append(handle)
            else:
                axs[i].plot(dates,elo,color = '0.6',linewidth=1)
        #Formatting
        axs[i].xaxis.set_ticks_position('none')
        axs[i].set_xlabel(str(years[i]))
        axs[i].tick_params('x',labelbottom=False)
        axs[i].set_ylim(1050,1950)
        axs[i].set_xlim(season_start,season_end)
        axs[i].grid(True)
        if i == 0:
            axs[i].yaxis.tick_left()
            axs[i].set_yticks(range(1100,2000,100))
        if i != len(axs)-1:
            axs[i].spines['right'].set_visible(False)
        if i != 0:
            axs[i].yaxis.set_ticks_position('none')
            axs[i].spines['left'].set_visible(False)
        if i == len(axs)-1:
            axs[i].legend(handles = teams_legend)
    plt.show()



def one_plot(team_input, title = "Elo Ratings", label = "team_name", team_colors=False):
    """ Plot historical elo ratings for every AUDL team with selected teams highlighted.

    Parameters
    ----------
    team_input: list
        list of teams to be highlighted, can contain team abbreviations, names, or franchises.
    title: string
        title of the plot, defaults to "Elo Ratings".
    label: string
        column header from audl_franchises.csv to choose which column to pull legend information from.
    team_colors: boolean
        True to utilize team colors in the plot or False to use a standard color set.

    Returns
    -------
    None
        Creates and plots the historical elo plot.
    """
    g = pd.read_csv("audl_elo.csv")
    franchises = pd.read_csv("audl_franchises.csv").set_index("franchise",drop=False)
    target_teams = []
    for t in team_input:
        target_teams.append(franchise_lookup(t))
    print(target_teams)
    teams = [i for i in g["fran_id"].unique() if i not in target_teams] + target_teams
    years = g["year_id"].unique()
    #teams_df = pd.read_csv("audl_teams.csv")

    #plt.style.use('fivethirtyeight')
    fig, ax = plt.subplots()
    fig.suptitle(title, fontsize=20)

    #Get Seasons Data
    year_group = g.groupby('year_id')
    season_starts = pd.to_datetime(year_group.date.min()) - datetime.timedelta(7)
    season_ends =  pd.to_datetime(year_group.date.max())
    playoffs_starts = pd.to_datetime(g[g['is_playoffs'] == 1].groupby('year_id').date.min())
    reg_ssn_ends = pd.to_datetime(g[g['is_playoffs'] == 0].groupby('year_id').date.max())
    # Because 2018 season is not over
    season_ends[2018] = pd.to_datetime('08/12/2018')
    reg_ssn_ends[2018] = pd.to_datetime('07/15/2018')
    playoffs_starts[2018] = pd.to_datetime('07/21/2018')
    season_lengths = (season_ends - season_starts).dt.days

    #Plotting

    # Get colors for target teams
    if team_colors:
        colors = []
        for fran in target_teams:
            color = fran_color(fran)
            if (color in colors):
                color = fran_color(fran,2)
            colors.append(color)
    else:
        colors = ['b','g','r','c','m','y','k']


    count = 0
    teams_legend = []
    for team in teams:

        team_games = g[(g["fran_id"] == team)]

        for year in years:
            year_games = team_games[team_games["year_id"] == year]
            if year_games.shape[0] > 0:
                # Set X-values based on dates
                # first_value = sum(season_lengths[season_lengths.index < year])
                dates = pd.to_datetime(year_games["date"]).reset_index(drop = True)
                season_start_list = season_starts[year_games["year_id"]].reset_index(drop = True)
                day_of_season = (dates - season_start_list).dt.days

                day_of_season_norm = year + day_of_season / season_lengths[year]
                x_values = [year] + day_of_season_norm.tolist()

                #Set Y-values as elo
                year_elo = [year_games["elo_i"].iloc[0]] + year_games["elo_n"].tolist()
                print()
                print(team,year)
                print(len(x_values), x_values)
                print(len(year_elo), year_elo)
                if team in target_teams:
                    fran_label = franchises.loc[team][label]
                    handle, = ax.plot(x_values,year_elo,color = colors[count],linewidth=2,label=fran_label)
                else:
                    ax.plot(x_values,year_elo,color = '0.6',linewidth=1)
        if team in target_teams:
            count += 1
            teams_legend.append(handle)
    #Formatting
    ax.xaxis.set_ticks_position('none')
    #ax.set_xlabel(years)
    ax.tick_params('x',labelbottom=True)
    ax.set_ylim(1150,1850)
    ax.set_xlim(years[0],years[-1]+1.1)
    ax.grid(True)
    ax.yaxis.tick_left()
    ax.set_yticks(range(1200,1900,100))
    #ax.spines['right'].set_visible(False)
    #axs[i].yaxis.set_ticks_position('none')
    #axs[i].spines['left'].set_visible(False)
    ax.legend(handles = teams_legend)

    # Grey out background to indicate playoffs
    playoff_day_of_season = ((reg_ssn_ends - season_starts).dt.days + (playoffs_starts - season_starts).dt.days)/2 + 1
    for year in years:
        playoff_day_of_season_norm = year + playoff_day_of_season[year] / season_lengths[year]
        ax.axvspan(playoff_day_of_season_norm,year+1,facecolor='0.8',alpha=0.5)

    plt.show()

def franchise_lookup(name):
    """Look up team franchise by team abbreviation, name or franchise."""
    teams = pd.read_csv("audl_teams.csv").set_index("abbr")
    if name in teams.index:
        return teams.loc[name]["franchise"]
    if name in teams["team_name"].values:
        return teams[teams["team_name"] == name]["franchise"].iloc[0]
    if name in teams["franchise"].str.lower().values:
        return name[0].upper() + name[1:]
    return name

def fran_color(fran_id,colornum=1):
    """Look up the primary or secondary color for a team."""
    teams_2018 = pd.read_csv("2018/2018_audl_teams.csv").set_index('franchise')
    color_index = 'color' + str(colornum)
    return teams_2018.loc[fran_id,color_index]


def predict_results():
    """Print table of elo-based predictions for future AUDL games."""

    ELO_POINT_RATIO = 1/32 # 1 point difference corresponds to 32 elo points
    HFA = 64 #home field advantage is 64 elo points ~ 2 points
    days_diff = 1

    g = pd.read_csv("audl_elo.csv")
    g["date"] = pd.to_datetime(g["date"])
    t = g[g["date"] >= datetime.datetime.today()-datetime.timedelta(days=days_diff)]
    t = t[t['game_location'] == 'H']
    t["elo_diff"] = t.loc[:,"elo_i"] - t.loc[:,"opp_elo_i"] + HFA
    t["audl_diff"] = t["elo_diff"]*ELO_POINT_RATIO

    # Get a prediction of the total nubmer of points score in each game
    # based on previous games this year (2018).
    g2018 =  g[(g["year_id"] == 2018) & (g['date'] < datetime.datetime.today()-datetime.timedelta(days=days_diff))]
    def estimate_points(l):
        home_points = g2018[g2018['team_id'] == l['team_id']].pts.mean()
        away_points = g2018[g2018['team_id'] == l['opp_id']].pts.mean()
        return home_points + away_points
    t['points_est'] = t.apply(estimate_points,axis=1)

    print(t.loc[:,["team_id","opp_id","date","points_est","forecast","audl_diff"]])
