from dotenv import load_dotenv
import os
import requests
import time
import traceback
import json
from collections import defaultdict, deque

load_dotenv()

MAP_ID = os.getenv("MAP_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
CONNECTIONS_FILE = "connections.json"
HOME_SYSTEM_NAME = "J103453"
HIGHSEC_NAMES_FILE = "highsec_system_names.json"
LAST_PATH_FILE = "last_path.json"

# Load highsec names
with open(HIGHSEC_NAMES_FILE) as f:
    HIGHSEC_NAMES = set(json.load(f))

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": (
        "cookie=1; "
        f"pathfinder_session={os.getenv('PF_SESSION')}; "
        f"char_756f808ea2cc0b9e3480676514e66368={os.getenv('PF_CHAR_COOKIE')}"
    ),
    "pf-character": os.getenv("PF_CHARACTER"),
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://path.shadowflight.org/map"
}


TRADE_HUBS = {
    "Jita": 30000142,
    "Amarr": 30002187,
    "Dodixie": 30002659,
    "Rens": 30002510,
    "Hek": 30002053
}

def resolve_system_name_to_id(name):
    url = "https://esi.evetech.net/latest/universe/ids/"
    response = requests.post(url, json=[name])
    response.raise_for_status()
    data = response.json()
    if "systems" in data:
        return data["systems"][0]["id"]
    return None

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

def send_discord_alert(message):
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

def log_alert(message):
    with open("wh_alerts.log", "a") as f:
        f.write(f"{time.ctime()} - {message}\n")

def get_map_data():
    url = "https://path.shadowflight.org/api/Map/updateData"
    headers = HEADERS.copy()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    data = "getUserData=1"
    r = requests.post(url, headers=headers, data=data)
    r.raise_for_status()
    return r.json()

def print_graph(graph, system_name_lookup):
    print("🌌 Pathfinder Wormhole Graph:")
    for system_id, neighbors in graph.items():
        name = system_name_lookup.get(system_id, str(system_id))
        neighbor_names = [f"{system_name_lookup.get(n, str(n))} (id: {n})" for n in neighbors]
        print(f"  {name} (id {system_id}) → {', '.join(neighbor_names)}")

def find_path_to_highsec(graph, start_id, name_lookup):
    visited = set()
    queue = deque([(start_id, [start_id])])

    while queue:
        current, path = queue.popleft()
        current_name = name_lookup.get(current, str(current))
        print(f"🛰️ Visiting {current_name} (ID: {current}), path: {[name_lookup.get(p, str(p)) for p in path]}")
        if current in visited:
            continue
        visited.add(current)

        if current_name in HIGHSEC_NAMES:
            print(f"✅ High-sec system reached: {current_name}")
            return path

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))
    return None

def get_route_length(origin_id, destination_id):
    url = f"https://esi.evetech.net/latest/route/{origin_id}/{destination_id}/"
    r = requests.get(url)
    if r.status_code == 200:
        return len(r.json()) - 1
    return None

def report_trade_hub_distances(highsec_entry_id):
    distances = {}
    for hub_name, hub_id in TRADE_HUBS.items():
        jumps = get_route_length(highsec_entry_id, hub_id)
        if jumps is not None:
            print(f"📦 {hub_name}: {jumps} jumps")
            distances[hub_name] = jumps
    return distances

def main():
    print("🚀 Pathfinder WH Alert Bot running...")
    prior_connections = load_prior_connections()

    while True:
        try:
            data = get_map_data()
            graph = defaultdict(list)

            # Collect systems and connections
            system_ids = [
                (s["id"], s["name"])
                for map_data in data.get("mapData", [])
                for s in map_data["data"].get("systems", [])
            ]
            name_lookup = dict(system_ids)
            reverse_lookup = {name: sid for sid, name in system_ids}

            connections = {
                (c["source"], c["target"])
                for map_data in data.get("mapData", [])
                for c in map_data["data"].get("connections", [])
            }

            for source, target in connections:
                graph[source].append(target)
                graph[target].append(source)

            # Show the full graph
            print_graph(graph, name_lookup)

            # Pathfinding from home system to highsec
            home_id = reverse_lookup.get(HOME_SYSTEM_NAME)
            if not home_id:
                print(f"⚠️ Could not find system ID for {HOME_SYSTEM_NAME}")
            else:
                path = find_path_to_highsec(graph, home_id, name_lookup)
                if path:
                    named_path = [name_lookup.get(s, str(s)) for s in path]
                    last_path = load_last_path()

                    if named_path != last_path:
                        entry_point_id = resolve_system_name_to_id(name_lookup.get(path[-1]))
                        msg = f"🧭 Route from {named_path[0]} to High-Sec:\n`" + " → ".join(named_path) + "`"
                        distances = report_trade_hub_distances(entry_point_id)
                        distances_msg = "\n".join([f"📦 {hub}: {jumps} jumps" for hub, jumps in distances.items()])
                        msg = (
                            f"🧭 Route from {named_path[0]} to High-Sec:\n`" + " → ".join(named_path) + "`\n" +
                            distances_msg
                        )
                        send_discord_alert(msg)
                        log_alert(msg)
                        save_last_path(named_path)
                    else:
                        print("🟢 High-sec path unchanged; no alert sent.")


            # Compare changes
            added = connections - prior_connections
            removed = prior_connections - connections

            for source, target in added:
                alert = f"➕ New connection: `{name_lookup.get(source, 'Unknown')}` → `{name_lookup.get(target, 'Unknown')}`"
                log_alert(alert)
            for source, target in removed:
                alert = f"❌ Connection removed: `{name_lookup.get(source, 'Unknown')}` → `{name_lookup.get(target, 'Unknown')}`"
                log_alert(alert)

            save_prior_connections(connections)
            prior_connections = connections

            time.sleep(60)
        except Exception as e:
            print(f"[ERROR] {e}")
            print(traceback.format_exc())
            time.sleep(10)

if __name__ == "__main__":
    main()
