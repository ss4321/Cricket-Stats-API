import pandas as pd
import numpy as np
import json
from connect_database import load_cached_data

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


# function of loaded catch
load_cached_data()
from connect_database import balls_data, matches_data


def all_ipl_bowler():
    #matches = pd.read_csv('ipl-matches.csv')
    #balls = pd.read_csv('IPL_Ball_by_Ball_2008_2022 - IPL_Ball_by_Ball_2008_2022.csv')
    matches = matches_data
    balls = balls_data
    all_bowler = list(set(balls['bowler']))
    balls_matches = pd.merge(matches, balls, on='ID', how='inner')

    seasonwise_bowler = {}
    all_bowler = list(set(balls['bowler']))
    season = list(matches['Season'].unique())
    total = len(all_bowler)
    for i in season:
        filtered_data = balls_matches.loc[balls_matches['Season'] == i]
        seasonwise_bowler[i] = list((filtered_data['bowler'].unique()))
    new_dict = {
        'total': total,
        'all_bolwer_ipl': all_bowler,
        'seasons': season,
        'seasonwise_bowlers': seasonwise_bowler

    }
    return json.dumps(new_dict, cls=NpEncoder)


#ipl_matches = 'ipl-matches.csv'
#matches = pd.read_csv(ipl_matches)
matches = matches_data
#ipl_ball = 'IPL_Ball_by_Ball_2008_2022 - IPL_Ball_by_Ball_2008_2022.csv'
#balls = pd.read_csv(ipl_ball)
balls = balls_data
ball_withmatch = balls.merge(matches, on='ID', how='inner').copy()
ball_withmatch['BowlingTeam'] = ball_withmatch.Team1 + ball_withmatch.Team2
ball_withmatch['BowlingTeam'] = ball_withmatch[['BowlingTeam', 'BattingTeam']].apply(
    lambda x: x.values[0].replace(x.values[1], ''), axis=1)
batter_data = ball_withmatch[np.append(balls.columns.values, ['BowlingTeam', 'Player_of_Match'])]
bowler_data = batter_data.copy()


def bowlerRun(x):
    if x[0] in ['penalty', 'legbyes', 'byes']:
        return 0
    else:
        return x[1]


bowler_data['bowler_run'] = bowler_data[['extra_type', 'total_run']].apply(bowlerRun, axis=1)


def bowlerWicket(x):
    if x[0] in ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket']:
        return x[1]
    else:
        return 0


bowler_data['isBowlerWicket'] = bowler_data[['kind', 'isWicketDelivery']].apply(bowlerWicket, axis=1)


def bowlerRecord(bowler, df):
    # if df.empty:
    # return np.nan

    df = df[df['bowler'] == bowler]
    inngs = df.ID.unique().shape[0]
    nballs = df[~(df.extra_type.isin(['wides', 'noballs']))].shape[0]
    runs = df['bowler_run'].sum()
    if nballs:
        eco = runs / nballs * 6
    else:
        eco = 0
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]

    wicket = df.isBowlerWicket.sum()
    if wicket:
        avg = runs / wicket
    else:
        avg = np.inf

    if wicket:
        strike_rate = nballs / wicket * 100
    else:
        strike_rate = np.nan

    gb = df.groupby('ID').sum()
    w3 = gb[(gb.isBowlerWicket >= 3)].shape[0]

    best_wicket = gb.sort_values(['isBowlerWicket', 'bowler_run'], ascending=[False, True])[
        ['isBowlerWicket', 'bowler_run']].head(1).values
    if best_wicket.size > 0:

        best_figure = f'{best_wicket[0][0]}/{best_wicket[0][1]}'
    else:
        best_figure = np.nan
    mom = df[df.Player_of_Match == bowler].drop_duplicates('ID', keep='first').shape[0]
    data = {
        'innings': inngs,
        'wicket': wicket,
        'economy': eco,
        'average': avg,
        'avg': avg,
        'strikeRate': strike_rate,
        'fours': fours,
        'sixes': sixes,
        'best_figure': best_figure,
        '3+W': w3,
        'mom': mom
    }

    return data


def bowlerVsTeam(bowler, team, df):
    df = df[df.BattingTeam == team].copy()
    return bowlerRecord(bowler, df)


def bowlerAPI(bowler, balls=bowler_data):
    df = balls[balls.innings.isin([1, 2])]  # Excluding Super overs
    self_record = bowlerRecord(bowler, df=df)
    TEAMS = matches.Team1.unique()
    against = {team: bowlerVsTeam(bowler, team, df) for team in TEAMS}
    data = {
        bowler: {'all': self_record,
                 'against': against}
    }
    return json.dumps(data, cls=NpEncoder)
