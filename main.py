from dotenv import load_dotenv
import os
import requests
import time
import traceback
import json
from collections import defaultdict, deque

from helpers.data import (
    load_last_path,
    load_prior_connections,
    log_alert,
    save_last_path,
    save_prior_connections,
)
from helpers.esi import get_route_length, resolve_system_name_to_id
from helpers.pathfinder import get_map_data, print_graph

load_dotenv()

MAP_ID = os.getenv("MAP_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
HOME_SYSTEM_NAME = "J103453"
HIGHSEC_NAMES_FILE = "highsec_system_names.json"

# Load highsec names
with open(HIGHSEC_NAMES_FILE) as f:
    HIGHSEC_NAMES = set(json.load(f))

TRADE_HUBS = {
    "Jita": 30000142,
    "Amarr": 30002187,
    "Dodixie": 30002659,
    "Rens": 30002510,
    "Hek": 30002053,
}


def send_discord_alert(message):
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message})


def find_path_to_highsec(graph, start_id, name_lookup):
    visited = set()
    queue = deque([(start_id, [start_id])])

    while queue:
        current, path = queue.popleft()
        current_name = name_lookup.get(current, str(current))
        print(
            f"🛰️ Visiting {current_name} (ID: {current}), path: {[name_lookup.get(p, str(p)) for p in path]}"
        )
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
                        entry_point_id = resolve_system_name_to_id(
                            name_lookup.get(path[-1])
                        )
                        msg = (
                            f"🧭 Route from {named_path[0]} to High-Sec:\n`"
                            + " → ".join(named_path)
                            + "`"
                        )
                        distances = report_trade_hub_distances(entry_point_id)
                        distances_msg = "\n".join(
                            [
                                f"• {hub}: {jumps} jumps"
                                for hub, jumps in distances.items()
                            ]
                        )
                        msg = (
                            f"🧭 Route from {named_path[0]} to High-Sec:\n`"
                            + " → ".join(named_path)
                            + "`\n"
                            + distances_msg
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
            send_discord_alert("error - check app logs")
            print(f"[ERROR] {e}")
            print(traceback.format_exc())
            exit(1)


if __name__ == "__main__":
    main()
