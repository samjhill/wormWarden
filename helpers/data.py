import os
import json
import time 

LAST_PATH_FILE = "last_path.json"
CONNECTIONS_FILE = "connections.json"

def load_last_path():
    if os.path.exists(LAST_PATH_FILE):
        with open(LAST_PATH_FILE, "r") as f:
            return json.load(f)
    return []

def save_last_path(path):
    with open(LAST_PATH_FILE, "w") as f:
        json.dump(path, f)


def load_prior_connections():
    if os.path.exists(CONNECTIONS_FILE):
        with open(CONNECTIONS_FILE, "r") as f:
            return set(tuple(conn) for conn in json.load(f))
    return set()

def save_prior_connections(connections):
    with open(CONNECTIONS_FILE, "w") as f:
        json.dump([list(conn) for conn in connections], f)

def log_alert(message):
    with open("wh_alerts.log", "a") as f:
        f.write(f"{time.ctime()} - {message}\n")