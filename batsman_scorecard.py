import numpy as np
import pandas as pd
import json
from connect_database import load_cached_data
load_cached_data()
from connect_database import balls_data, matches_data
balls = balls_data
matches = matches_data

balls_match = pd.merge(matches, balls, on='ID')

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)



def get_player_dismissal_details(match_id, player_name, curr_inning):
    # Filter data for the given match and player
    player_data = balls[
        (balls['isWicketDelivery'] == 1) & (balls['innings'] == curr_inning) & (balls['ID'] == match_id) & (
                    balls['batter'] == player_name)]

    # Check if the player was dismissed
    if not player_data.empty:
        dismissal_details = ''
        kind_out = player_data['kind'].values[0]
        bowler = player_data['bowler'].values[0]
        fielder_involved = player_data['fielders_involved'].values[0]

        if kind_out == 'bowled':
            return f"bowled b {bowler}"
        elif kind_out == 'caught':
            return f"b {bowler} & c {fielder_involved}"
        elif kind_out == 'caught and bowled':
            return f"c&b {bowler}"
        elif kind_out == 'run out':
            return f"run out by {bowler}"
        elif kind_out == 'stumped':
            return f"stumped by {fielder_involved}, b {bowler}"
        elif kind_out == 'lbw':
            return f"lbw b {bowler}"
        elif kind_out == 'hit wicket':
            return f"hit wicket by {bowler}"
        elif kind_out == 'retired hurt':
            return "retired hurt"
        elif kind_out == 'retired out':
            return "retired out"
        elif kind_out == 'obstructing the field':
            return "obstructing the field"
    else:
        return 'not out'


def scorecard_inning(team, t, match_id, inning_inning):
    # Initialize lists to store player and extra statistics
    player_stats = []
    extra_stats = []

    # Define a function to calculate player statistics
    def calculate_player_stats(player_data):
        total_runs = player_data['batsman_run'].sum()
        total_balls = player_data['batsman_run'].count()
        wide_balls = (player_data['extra_type'] == 'wides').sum()
        played_balls = total_balls - wide_balls
        fours = (player_data['batsman_run'] == 4).sum()
        sixes = (player_data['batsman_run'] == 6).sum()
        strike_rate = round((total_runs / played_balls) * 100, 2)
        b_t_o = get_player_dismissal_details(match_id, player, inning_inning)
        return {
            'Player Name': player,
            'Total Runs': total_runs,
            'Total Balls': played_balls,
            'Fours': fours,
            'Sixes': sixes,
            'Strike Rate': strike_rate,
            '---': b_t_o
        }

    # Iterate through each player in the team
    for player in team:
        player_data = t[t['batter'] == player]
        player_stat = calculate_player_stats(player_data)
        player_stats.append(player_stat)

    # Calculate extra statistics
    unique_extra_types = t['extra_type'].unique()
    unique_extra_types = [et for et in unique_extra_types if not pd.isna(et)]
    for extra_type in unique_extra_types:
        extra_data = t[t['extra_type'] == extra_type]
        count = extra_data.shape[0]
        extra_stat = {'Extra Type': extra_type, 'Count': count}
        extra_stats.append(extra_stat)

    return player_stats, extra_stats


def scorecard(match_id):
    # for inning 1
    match_id = int(match_id)
    result_dict = {}
    curr_match_data = balls_match[balls_match['ID'] == match_id]
    team1 = list(balls[(balls['ID'] == match_id) & (balls['innings'] == 1)].batter.unique())
    inning_1 = 1
    inning1, extra_inning1_run = scorecard_inning(team1, curr_match_data,match_id, inning_1)

    # for inning 2
    team2 = list(balls[(balls['ID'] == match_id) & (balls['innings'] == 2)].batter.unique())
    inning_2 = 2
    inning2, extra_inning2_run = scorecard_inning(team2, curr_match_data,match_id, inning_2)
    result_dict = {
        'inning1' : inning1,
        'extra_runs_inning1' :extra_inning1_run,
        'inning2' : inning2,
        'extra_runs_inning2' : extra_inning2_run


    }
    return json.dumps(result_dict, cls=NpEncoder)