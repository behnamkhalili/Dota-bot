import time
from database_manager import DatabaseManager
from dotenv import load_dotenv
import os
from api_clients import SteamApiClient , StratzApiClient
from data_processor import steam_api_match_history_parser,stratz_match_detail_parser

if __name__ == "__main__":
    load_dotenv()
    database = DatabaseManager()
'''    user = os.getenv("sid")

    steam = SteamApiClient(key=os.getenv('STEAM_API_KEY'))
    stratz = StratzApiClient(token=os.getenv('STRATZ_API_KEY'))

    matches_raw = steam.get_player_match_history(user,100)
    matches = steam_api_match_history_parser(matches_raw)
    for match in matches:
        time.sleep(0.1)
        print(match)
        database.save_match_data(stratz_match_detail_parser(stratz.get_match_details(match.match_id)))
        print(match.match_id)'''
