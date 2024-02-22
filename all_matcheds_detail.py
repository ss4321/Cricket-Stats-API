import pandas as pd
from connect_database import load_cached_data
load_cached_data()
from connect_database import balls_data, matches_data
import numpy as np
import json

balls = balls_data
match = matches_data

balls_match = pd.merge(balls_data, matches_data, on='ID')

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
def generate_match_summary():
    global balls_match
    # Group the DataFrame by 'Stadium', 'ID', and 'innings', and calculate the maximum score for each inning of each match
    highest_scores_first_inning = balls_match[balls_match['innings'] == 1].groupby(['Stadium', 'ID'])['total_run'].sum()
    wickets_first_inning = balls_match[balls_match['innings'] == 1].groupby(['Stadium', 'ID'])['isWicketDelivery'].sum()
    highest_scores_second_inning = balls_match[balls_match['innings'] == 2].groupby(['Stadium', 'ID'])['total_run'].sum()
    wickets_second_inning = balls_match[balls_match['innings'] == 2].groupby(['Stadium', 'ID'])['isWicketDelivery'].sum()

    # Initialize a list to store the results
    results = []

    # Iterate through the grouped data and append the results as dictionaries to the list
    for (stadium_name, match_id), highest_score_first_inning in highest_scores_first_inning.items():
        # Get the corresponding 'Team1' and 'Team2' for the match
        team1 = balls_match[(balls_match['ID'] == match_id) & (balls_match['innings'] == 1)]['Team1'].iloc[0]
        team2 = balls_match[(balls_match['ID'] == match_id) & (balls_match['innings'] == 1)]['Team2'].iloc[0]

        # Get the date for the match
        match_date = balls_match[balls_match['ID'] == match_id]['Date'].iloc[0]

        # Get the highest score for the second inning (default to 0 if not available)
        highest_score_second_inning = highest_scores_second_inning.get((stadium_name, match_id), 0)

        # Get the wickets for both innings
        wickets_first = wickets_first_inning.get((stadium_name, match_id), 0)
        wickets_second = wickets_second_inning.get((stadium_name, match_id), 0)

        # Get Winning Team
        winning_team = balls_match.loc[balls_match['ID'] == match_id, 'WinningTeam'].values[0]

        # Get man_of_match
        Player_of_Match = balls_match.loc[balls_match['ID'] == match_id, 'Player_of_Match'].values[0]

        result = {
            'MatchID': match_id,
            'Stadium': stadium_name,
            'Team1': team1,
            'Team2': team2,
            'ScoreFirstInning': highest_score_first_inning,
            'WicketsFirstInning': wickets_first,
            'ScoreSecondInning': highest_score_second_inning,
            'WicketsSecondInning': wickets_second,
            'Winning Team': winning_team,
            'Date': match_date,
            'Player_of_Match': Player_of_Match
        }
        results.append(result)

    return json.dumps(results, cls=NpEncoder)
