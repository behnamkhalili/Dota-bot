import requests

BASE_URL = "https://api.opendota.com/api/players"


def data(player_id):
    url = f"{BASE_URL}/{player_id}/data"
    response = requests.get(url)
    return response.json()


def matches(player_id, query_params):
    url = f"{BASE_URL}/{player_id}/matches"
    response = requests.get(url, params=query_params)
    return response.json()

