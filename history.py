import os
import json

# File path for storing history
HISTORY_FILE = 'history.json'
MAX_HISTORY_SIZE = 30

def add_to_history(url, query, result):
    # Load existing history from the file
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    history.append(entry)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    print(f"Problematic line: {line}")

    # Add the new data to the history
    new_data = {
        'url': url,
        'query': query
    }

    # Add the new entry at the beginning of the history
    history.insert(0, new_data)

    # If history size exceeds the maximum, remove the oldest entry
    if len(history) > MAX_HISTORY_SIZE:
        history = history[:MAX_HISTORY_SIZE]

    # Write the updated history back to the file
    with open(HISTORY_FILE, 'w') as f:
        for entry in history:
            json.dump(entry, f)
            f.write('\n')

def get_history():
    history = []

    # Read history data from the file
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    history.append(entry)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    print(f"Problematic line: {line}")

    return history

