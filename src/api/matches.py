import requests

BASE_URL = "https://api.opendota.com/api/matches"


def data(match_id):
    url = f"{BASE_URL}/{match_id}"
    response = requests.get(url)
    return response.json()