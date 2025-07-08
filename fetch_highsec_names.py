import requests
import json
import time
import os

FINAL_FILE = "highsec_system_names.json"
PARTIAL_FILE = "highsec_system_names.partial.json"

SLEEP_INTERVAL = 1
SAVE_EVERY = 50
MAX_RETRIES = 3

def get_all_system_ids():
    print("📡 Fetching all solar system IDs from ESI...")
    url = "https://esi.evetech.net/latest/universe/systems/"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_system_details(system_id):
    url = f"https://esi.evetech.net/latest/universe/systems/{system_id}/"
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ Status {response.status_code} for {system_id}, retrying...")
        except requests.RequestException as e:
            print(f"❌ Error fetching {system_id}: {e}")
        time.sleep(SLEEP_INTERVAL * (attempt + 1))
    return None

def load_partial():
    if os.path.exists(PARTIAL_FILE):
        with open(PARTIAL_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_partial(highsec_names):
    with open(PARTIAL_FILE, "w") as f:
        json.dump(sorted(highsec_names), f)
    print(f"💾 Progress saved: {len(highsec_names)} high-sec systems so far.")

def save_final(highsec_names):
    with open(FINAL_FILE, "w") as f:
        json.dump(sorted(highsec_names), f, indent=2)
    print(f"✅ Saved {len(highsec_names)} high-sec system names to {FINAL_FILE}")
    if os.path.exists(PARTIAL_FILE):
        os.remove(PARTIAL_FILE)

def fetch_highsec_system_names():
    all_ids = get_all_system_ids()
    highsec_names = load_partial()
    checked_ids = set()

    # Remove already checked from the list
    if highsec_names:
        print(f"🔁 Resuming from {PARTIAL_FILE} with {len(highsec_names)} names...")
    remaining_ids = [sid for sid in all_ids if sid not in checked_ids]

    for i, sid in enumerate(remaining_ids, start=1):
        data = get_system_details(sid)
        if data and data.get("security_status", 0.0) >= 0.5:
            highsec_names.add(data["name"])

        if i % SAVE_EVERY == 0:
            save_partial(highsec_names)
            print(f"🔍 Checked {i}/{len(remaining_ids)} systems...")

        time.sleep(SLEEP_INTERVAL)

    return highsec_names

if __name__ == "__main__":
    highsec_names = fetch_highsec_system_names()
    save_final(highsec_names)
