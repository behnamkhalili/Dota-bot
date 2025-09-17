import os, json
import matches, players


def save_json(data, filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    if isinstance(existing, list):
        existing.append(data)
    else:
        existing = [existing, data]

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)


def main():
    player_id = {"Sad bHnM": 1242992203, "Serpico": 104374667}
    res = matches.data(8440438303)
    save_json(res, "data.json")
    # time.sleep(2)
    # print(get_pro_player())

    print()


if __name__ == "__main__":
    main()
