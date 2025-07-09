import requests

def resolve_system_name_to_id(name):
    url = "https://esi.evetech.net/latest/universe/ids/"
    response = requests.post(url, json=[name])
    response.raise_for_status()
    data = response.json()
    if "systems" in data:
        return data["systems"][0]["id"]
    return None

def get_route_length(origin_id, destination_id):
    url = f"https://esi.evetech.net/latest/route/{origin_id}/{destination_id}/?flag=secure"
    r = requests.get(url)
    if r.status_code == 200:
        return len(r.json()) - 1
    return None