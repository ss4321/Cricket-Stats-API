from flask import Flask, jsonify, request
import connect_database
connect_database.connect_to_mysql_and_get_data()
import ipl
import numpy as np
from history import add_to_history, get_history
import bowler_related
import batsman_related
import stadium_ground
import all_matcheds_detail
import batsman_scorecard


app = Flask(__name__)




@app.before_request
def add_request_to_history():
    url = request.url
    query = f"{request.path}?{request.query_string.decode()}"
    add_to_history(url, query, None)



@app.route('/')
def home():
    return 'Welcome to Ipl API'


@app.route('/api/teams')
def all_teams():
    teams = ipl.all_teams()
    return jsonify(teams)


@app.route("/api/teamvsteam")
def teamvsteam():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')

    # Assuming ipl.team_vs_team returns a dictionary with int64 values
    res = ipl.team_vs_team(team1, team2)

    # Convert int64 values in the dictionary to int
    for key, value in res.items():
        if isinstance(value, np.int64):
            res[key] = int(value)

    return jsonify(res)


@app.route('/api/team-record')
def team_record():
    team = request.args.get('team')
    response = ipl.teamAPI(team)
    return response


@app.route('/api/batsmen-record')
def batsman_record():
    batsmen = request.args.get('batsmen')
    result = batsman_related.batsmanAPI(batsmen)
    return result


@app.route('/api/batsman-vs-bowler')
def batsman_bowler():
    batsman = request.args.get('batsmen')
    result = batsman_related.bowler_batsmen_all_record(batsman)
    return result


@app.route('/api/bowling-record')
def bowling_record():
    bowler = request.args.get('bowler')
    response = bowler_related.bowlerAPI(bowler)
    return response


@app.route('/history')
def view_history():
    history = get_history()
    return jsonify(history)


@app.route('/api/bowlers')
def get_all_bowlers():
    response = bowler_related.all_ipl_bowler()
    return response


@app.route('/api/batsmen')
def get_all_batsmen():
    response = batsman_related.all_ipl_batsman()
    return jsonify(response)

@app.route('/api/batsman_stadium')
def get_all_stadium():
    batter = request.args.get('batsmen')
    response = stadium_ground.stadium_vs_batsman(batter)
    return response

@app.route('/api/overall_stadium')
def overall_stadium_analysis():
    reponse = stadium_ground.stadium_overall()
    return reponse

@app.route('/api/total_match_overview')
def overall_data():
    response = all_matcheds_detail.generate_match_summary()
    return response

@app.route('/api/scorecard')
def detail_scorecard():
    ID = request.args.get('id')
    response = batsman_scorecard.scorecard(ID)
    return response




app.run(debug=True)
