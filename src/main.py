import os, json
from api_clients import OpenDotaApiClient, SteamApiClient


def save_json(data, filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing = data
    else:
        existing = []

    if isinstance(existing, list):
        existing.append(data)
    else:
        existing = [existing, data]

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)


def main():
    player_id = {
        "Ayatollah": 1033644716,
        "amu_ezi": 1199778230,
        "Sad bHnM": 1242992203,
        "Serpico": 104374667,
        "1000-7": 104374667
    }

    client = OpenDotaApiClient()
    res = client.get_player_data(account_id=player_id["Sad bHnM"])
    save_json(res, "data.json")
    print(res["rank_tier"])


if __name__ == "__main__":
    main()