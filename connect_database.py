import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
import pickle
import gzip

# Initialize dataframes as None initially
matches_data = None
balls_data = None

def connect_to_mysql_and_get_data():
    global matches_data, balls_data

    # Check if data is already retrieved, if not, fetch it from the database
    if matches_data is None or balls_data is None:
        try:
            # Establish a MySQL connection (use your actual credentials)
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user='root',
                password='',
                database='ipl_database'
            )

            if conn.is_connected():
                print('Connection established')
            else:
                print('Connection error')

            # Create an SQLAlchemy engine using the MySQL connection
            engine = create_engine("mysql+mysqlconnector://root:@127.0.0.1/ipl_database")

            # Create dataframes from the tables using SQLAlchemy
            matches_data = pd.read_sql('SELECT * FROM matches', con=engine)
            balls_data = pd.read_sql('SELECT * FROM balls', con=engine)

            # Close the MySQL connection
            conn.close()
            print('Connection closed')

            # Store the data in a file using pickle
            with gzip.open('data_cache.pkl', 'wb') as cache_file:
                data_to_store = {'matches_data': matches_data, 'balls_data': balls_data}
                pickle.dump(data_to_store, cache_file)
                print('Data cached to data_cache.pkl')

        except mysql.connector.Error as err:
            print(f'Error: {err}')

def load_cached_data():
    global matches_data, balls_data

    try:
        with gzip.open('data_cache.pkl', 'rb') as cache_file:
            cached_data = pickle.load(cache_file)
            matches_data = cached_data.get('matches_data')
            balls_data = cached_data.get('balls_data')
            print('Cached data loaded')

    except FileNotFoundError:
        print('No cached data found')
