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

#function to get the data balls and matches
load_cached_data()
from connect_database import balls_data, matches_data

def all_ipl_batsman():
    #matches = pd.read_csv('ipl-matches.csv')
    #balls = pd.read_csv('IPL_Ball_by_Ball_2008_2022 - IPL_Ball_by_Ball_2008_2022.csv')
    matches = matches_data
    balls = balls_data
    balls_matches = pd.merge(matches, balls, on='ID', how='inner')

    seasonwise_batsman = {}
    all_batsman = list(set(balls['batter']))
    season = list(matches['Season'].unique())
    for i in season:
        filtered_data = balls_matches.loc[balls_matches['Season'] == i]
        seasonwise_batsman[i] = list((filtered_data['batter'].unique()))
    result = {
        'total': len(all_batsman),
        'all_batsman_ipl': all_batsman,
        'seasons': season,
        'seasonwise_batsmen': seasonwise_batsman
    }
    return json.dumps(result, cls=NpEncoder)


#ipl_matches = 'ipl-matches.csv'
#matches = pd.read_csv(ipl_matches)
matches = matches_data
#ipl_ball = 'IPL_Ball_by_Ball_2008_2022 - IPL_Ball_by_Ball_2008_2022.csv'
#balls = pd.read_csv(ipl_ball)
balls = balls_data
ball_withmatch = balls.merge(matches, on='ID', how='inner').copy()
ball_withmatch['BowlingTeam'] = ball_withmatch.Team1 + ball_withmatch.Team2
ball_withmatch['BowlingTeam'] = ball_withmatch[['BowlingTeam', 'BattingTeam']].apply(lambda x: x.values[0].replace(x.values[1], ''), axis=1)
batter_data = ball_withmatch[np.append(balls.columns.values, ['BowlingTeam', 'Player_of_Match'])]


def batsmanRecord(batsman, df):
    if df.empty:
        return np.nan
    out = df[df.player_out == batsman].shape[0]
    df = df[df['batter'] == batsman]
    inngs = df.ID.unique().shape[0]
    runs = df.batsman_run.sum()
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]
    if out:
        avg = runs / out
    else:
        avg = np.inf

    nballs = df[~(df.extra_type == 'wides')].shape[0]
    if nballs:
        strike_rate = runs / nballs * 100
    else:
        strike_rate = 0
    gb = df.groupby('ID').sum()
    fifties = gb[(gb.batsman_run >= 50) & (gb.batsman_run < 100)].shape[0]
    hundreds = gb[gb.batsman_run >= 100].shape[0]
    try:
        highest_score = gb.batsman_run.sort_values(ascending=False).head(1).values[0]
        hsindex = gb.batsman_run.sort_values(ascending=False).head(1).index[0]
        if (df[df.ID == hsindex].player_out == batsman).any():
            highest_score = str(highest_score)
        else:
            highest_score = str(highest_score) + '*'
    except:
        highest_score = gb.batsman_run.max()

    not_out = inngs - out
    man_of_match = df[df.Player_of_Match == batsman].drop_duplicates('ID', keep='first').shape[0]
    data = {
        'innings': inngs,
        'runs': runs,
        'fours': fours,
        'sixes': sixes,
        'avg': avg,
        'strikeRate': strike_rate,
        'fifties': fifties,
        'hundreds': hundreds,
        'highestScore': highest_score,
        'notOut': not_out,
        'man_of_match': man_of_match
    }

    return data


def batsmanVsTeam(batsman, team, df):
    df = df[df.BowlingTeam == team].copy()
    return batsmanRecord(batsman, df)


def batsmanAPI(batsman, balls=batter_data):
    df = balls[balls.innings.isin([1, 2])]  # Excluding Super overs
    self_record = batsmanRecord(batsman, df=df)
    TEAMS = matches.Team1.unique()
    against = {team: batsmanVsTeam(batsman, team, df) for team in TEAMS}
    data = {
        batsman: {'all': self_record,
                  'against': against}
    }
    return json.dumps(data, cls=NpEncoder)

bowler_data = batter_data.copy()


def bowler_batsmen_all_record(batsman):
    result_dict = {}
    all_bowler = balls[balls['batter'] == batsman]
    all_bowler = set(all_bowler['bowler'])
    record = balls.groupby(['batter', 'bowler'])
    # print(all_bowler)

    for i in all_bowler:
        group = record.get_group((batsman, i))
        runs = group['batsman_run'].sum()
        four = (group['batsman_run'] == 4).sum()
        six = (group['batsman_run'] == 6).sum()
        total_balls = record.get_group((batsman, i)).shape[0]
        wide_balls = (group['extra_type'] == 'wides').sum()
        # print(total_balls)
        balls_played = total_balls - wide_balls
        batsman_strike_rate = round((runs / balls_played) * 100, 2)
        out = (group['isWicketDelivery'] == 1).sum()
        # print(out)
        # print(batsman_strikate)

        result_dict[i] = {
            'Runs': int(runs),
            'Fours': four,
            'Sixes': six,
            'Strike Rate': batsman_strike_rate,
            'Dismissal': out
        }
    data = {
        batsman: {'against': result_dict
                  }
    }

    return json.dumps(data, cls=NpEncoder)






