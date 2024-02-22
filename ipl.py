import json
import connect_database
import numpy as np
import pandas as pd


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

#call function connect_database because this have matches_data and ball_data
connect_database.load_cached_data()
from connect_database import matches_data, balls_data

#matches have all match data
matches = matches_data

#balls has all bowled data
balls = balls_data

ball_withmatch = balls.merge(matches, on='ID', how='inner').copy()
ball_withmatch['BowlingTeam'] = ball_withmatch.Team1 + ball_withmatch.Team2
ball_withmatch['BowlingTeam'] = ball_withmatch[['BowlingTeam', 'BattingTeam']].apply(
    lambda x: x.values[0].replace(x.values[1], ''), axis=1)
batter_data = ball_withmatch[np.append(balls.columns.values, ['BowlingTeam', 'Player_of_Match'])]

def all_teams():
    unique_teams = list(set(matches['Team1'].unique()) | set(matches['Team2'].unique()))
    return {
        'teams': unique_teams
    }

def team_vs_team(team1,team2):
    unique_teams = list(set(matches['Team1'].unique()) | set(matches['Team2'].unique()))
    if team1 in unique_teams and team2 in unique_teams:

        result = matches[((matches['Team1'] == team1) & (matches['Team2'] == team2)) | ((matches['Team1'] == team2) & (matches['Team2'] == team1))]
        total_matches = result.shape[0]
        match_won_by_team1 = result['WinningTeam'].value_counts()[team1]
        match_won_by_team2 = result['WinningTeam'].value_counts()[team2]
        draw = total_matches - (match_won_by_team1 + match_won_by_team2)
        result = {
            'total matches' : total_matches,
             team1 : match_won_by_team1,
             team2 : match_won_by_team2,
             'draw' : draw
        }
        return result
    return {'message' : 'Invalid team team'}
def team1vsteam2(team, team2):

    df = matches[((matches['Team1'] == team) & (matches['Team2'] == team2)) | (
            (matches['Team2'] == team) & (matches['Team1'] == team2))].copy()
    mp = df.shape[0]
    won = df[df.WinningTeam == team].shape[0]
    nr = df[df.WinningTeam.isnull()].shape[0]
    loss = mp - won - nr

    return {'matchesplayed': mp,
            'won': won,
            'loss': loss,
            'noResult': nr}


def allRecord(team):
    df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)].copy()
    mp = df.shape[0]
    won = df[df.WinningTeam == team].shape[0]
    nr = df[df.WinningTeam.isnull()].shape[0]
    loss = mp - won - nr
    nt = df[(df.MatchNumber == 'Final') & (df.WinningTeam == team)].shape[0]
    return {'matchesplayed': mp,
            'won': won,
            'loss': loss,
            'noResult': nr,
            'title': nt}


def teamAPI(team, matches=matches):
    unique_teams = list(set(matches['Team1'].unique()) | set(matches['Team2'].unique()))
    if team in unique_teams:
        df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)].copy()
        self_record = allRecord(team)
        TEAMS = matches.Team1.unique()
        against = {team2: team1vsteam2(team, team2) for team2 in TEAMS}
        data = {team: {'overall': self_record,
                       'against': against}}
        return json.dumps(data, cls=NpEncoder)
    return {'message':'Invalid team name'}




