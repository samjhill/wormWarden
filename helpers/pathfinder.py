import os
import requests

from dotenv import load_dotenv

load_dotenv()

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