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


#matches['Stadium'] = matches['Venue'].str.split(', ', n=1).str[0] #create new_csv file to add stadium column
#new_csv_file_path = "stadium_column_add.csv"
#matches.to_csv(new_csv_file_path, index=False)


# To load the data in balls and matches
load_cached_data()
from connect_database import balls_data, matches_data

def stadium_vs_batsman(batsman_name):
    try:
        # Read CSV data from stadium file
        #matches = pd.read_csv('stadium_column_add.csv')
        matches = matches_data

        # Read CSV file from ball by ball
        #ipl_ball = "IPL_Ball_by_Ball_2008_2022 - IPL_Ball_by_Ball_2008_2022.csv"
        #balls = pd.read_csv(ipl_ball)
        balls = balls_data

        # Merge both CSV files
        balls_match = pd.merge(balls, matches, on='ID')

        # Filter the DataFrame for the specified batsman
        batsman_data = balls_match[balls_match['batter'] == batsman_name]

        # Create a list of unique stadiums where the batsman played
        unique_stadiums = batsman_data['Stadium'].unique()

        result_dict = {}  # Initialize an empty dictionary to store results

        for stadium in unique_stadiums:
            # Filter data for the current stadium and batsman
            specific_data = batsman_data[batsman_data['Stadium'] == stadium]

            # Calculate statistics
            total_runs = specific_data['batsman_run'].sum()
            total_balls = specific_data.shape[0]
            wide_balls = (specific_data['extra_type'] == 'wides').sum()
            balls_faced_by_batsman = total_balls - wide_balls
            strike_rate = round((total_runs / balls_faced_by_batsman) * 100, 2)
            fours = len([run for run in specific_data['batsman_run'] if run == 4])
            sixes = len([run for run in specific_data['batsman_run'] if run == 6])
            dismissals = (specific_data['isWicketDelivery'] == 1).sum()
            total_innings = len(specific_data['ID'].unique())

            # Store results in the dictionary
            result_dict[stadium] = {
                'Total_Runs': total_runs,
                'Fours': fours,
                'Sixes': sixes,
                'Strike_Rate': strike_rate,
                'Dismissals': dismissals,
                'Total_Innings': total_innings
            }

        data = {
            batsman_name: {'against': result_dict}
        }

        return json.dumps(data, cls=NpEncoder)

    except Exception as e:
        return str(e)  # Handle exceptions and return an error message if necessary

def average_stadium(stadium, inning):
    matches = matches_data
    balls = balls_data
    balls_match = pd.merge(matches, balls, on='ID')
    data = balls_match[(balls_match['Stadium'] == stadium) & (balls_match['innings'] == inning)]
    total_runs = data['total_run'].sum()
    total_balls = data.shape[0]
    wide_ball = (data['extra_type'] == 'wides').sum()
    four = (data['batsman_run'] == 4).sum()
    six = (data['batsman_run'] == 6).sum()
    played_balls = total_balls - wide_ball
    average_boundary = played_balls / (four + six)
    four_average = played_balls / four
    six_average = played_balls / six
    stadium_average = (total_runs / played_balls) * 120
    return stadium_average, four, six, four_average, six_average

def stadium_overall():
    result_dict = {}
    matches = matches_data
    balls = balls_data
    all_stadiums = list(matches['Stadium'].unique())

    for stadium in all_stadiums:
        first_batting_win = (matches[matches['Stadium'] == stadium]['WonBy'] == 'Wickets').sum()
        second_batting_win = (matches[matches['Stadium'] == stadium]['WonBy'] == 'Runs').sum()
        superover = (matches[matches['Stadium'] == stadium]['WonBy'] == 'SuperOver').sum()
        no_result = (matches[matches['Stadium'] == stadium]['WonBy'] == 'NoResults').sum()

        first_inning, f_four, f_six, f_four_average, f_six_average = average_stadium(stadium, 1)
        second_inning, s_four, s_six, s_four_average, s_six_average = average_stadium(stadium, 2)

        result_dict[stadium] = {
            'Total_Match' : first_batting_win + second_batting_win + superover +no_result,
            'first_batting_win': first_batting_win,
            'second_batting_win': second_batting_win,
            'superover': superover,
            'no_result': no_result,
            'first_inning': {
                'average': first_inning,
                'four': f_four,
                'six': f_six,
                'four_average': f_four_average,
                'six_average': f_six_average
            },
            'second_inning': {
                'average': second_inning,
                'four': s_four,
                'six': s_six,
                'four_average': s_four_average,
                'six_average': s_six_average
            }
        }

    return json.dumps(result_dict, cls=NpEncoder)






