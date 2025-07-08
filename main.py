from dotenv import load_dotenv
import os
import requests
import time
import traceback

load_dotenv()

MAP_ID = os.getenv("MAP_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

cookie = (
    "cookie=1; "
    f"pathfinder_session={os.getenv('PF_SESSION')}; "
    f"char_756f808ea2cc0b9e3480676514e66368={os.getenv('PF_CHAR_COOKIE')}"
)

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,de;q=0.8,fr;q=0.7",
    "Cookie": cookie,
    "pf-character": os.getenv("PF_CHARACTER"),
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://path.shadowflight.org/map",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

previous_signatures = {}

def diff_dicts(old, new):
    added = new.keys() - old.keys()
    removed = old.keys() - new.keys()
    changed = {k for k in old.keys() & new.keys() if old[k] != new[k]}
    unchanged = {k for k in old.keys() & new.keys() if old[k] == new[k]}

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged
    }

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

def get_all_system_ids(data):
    systems = []
    for map_data in data.get("mapData", []):
        for s in map_data.get("data").get("systems", []):
            systems.append((s["id"], s["name"]))
        return systems

def get_all_connections(data):
    connections = []
    for map_data in data.get("mapData", []):
        for s in map_data.get("data").get("connections", []):
            connections.append((s["source"], s["target"]))
        return connections

def get_system_data(system_id):
    url = f"https://path.shadowflight.org/api/rest/System/{system_id}?mapId={MAP_ID}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code in [401, 403]:
        print("❌ Pathfinder session expired. Please update your session cookie.")
        exit(1)
    r.raise_for_status()
    return r.json()

def check_for_changes(system_name, system_id, current):
    alerts = []
    prev = previous_signatures.get(system_id, {})

    # New or updated sigs
    for sig_id, sig_data in current.items():
        if sig_id not in prev:
            alerts.append(f"🆕 `{system_name}`: New WH `{sig_data['name']}`")
        else:
            old = prev[sig_id]
            if sig_data["eol"] and not old["eol"]:
                alerts.append(f"⏳ `{system_name}`: WH `{sig_data['name']}` is now **EOL**")
            if sig_data["mass"] != old["mass"]:
                alerts.append(f"⚖️ `{system_name}`: WH `{sig_data['name']}` mass changed: {old['mass']} → {sig_data['mass']}")

    # Disappeared sigs
    for sig_id in prev:
        if sig_id not in current:
            alerts.append(f"💀 `{system_name}`: WH `{prev[sig_id]['name']}` disappeared (likely collapsed)")

    previous_signatures[system_id] = current
    return alerts

def main():
    print("🚀 Pathfinder WH Alert Bot running...")
    
    prior_connections = set()
    while True:
        try:
            map_data = get_map_data()
            system_ids = get_all_system_ids(map_data)
            system_ids_dict = dict(system_ids)
            connections = set(get_all_connections(map_data))
            if not prior_connections:
                prior_connections = connections
                print(f"connections: ")
                for source, target in connections:
                    print(f"`{system_ids_dict.get(source, 'Unknown')}` → `{system_ids_dict.get(target, 'Unknown')}`")

            added = connections - prior_connections
            removed = prior_connections - connections

            for source, target in added:
                alert_content = f"➕ New connection: `{system_ids_dict.get(source, 'Unknown')}` → `{system_ids_dict.get(target, 'Unknown')}`"
                send_discord_alert(alert_content)
                log_alert(alert_content)

            for source, target in removed:
                alert_content = f"❌ Connection removed: `{system_ids_dict.get(source, 'Unknown')}` → `{system_ids_dict.get(target, 'Unknown')}`"
                send_discord_alert(alert_content)
                log_alert(alert_content)

            if not added and not removed:
                print("nothing has changed. Not sending an alert now")
            time.sleep(60)
        except Exception as e:
            print(f"[ERROR] {e}")
            print(traceback.format_exc())
            time.sleep(5)

if __name__ == "__main__":
    main()
