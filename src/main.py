import os
import time

from api_clients.steam_api_client import SteamApiClient
from api_clients.stratz_api_client import StratzApiClient
from database_manager import DatabaseManager
from logging_config import get_logger
from data_processor import steam_api_match_history_parser , stratz_match_detail_parser

# this is just a test for etl
# i will compelete the etl steps next commits
def main():
    database = DatabaseManager()
    log = get_logger()
    steam = SteamApiClient(key=os.getenv("STEAM_API_KEY"))
    stratz = StratzApiClient(token=os.getenv("STRATZ_API_KEY"))
    # matches_raw = steam.get_player_match_history(os.getenv("Ayatollah") , 1)
    # matches_valid =steam_api_match_history_parser(matches_raw)
    # print(matches_valid)
    database.set_player_track_status(player_steam_id=1033644716 , status=True)
    print(database.get_tracked_players())
    time.sleep(0.5)
    log.info(msg="getting 8937132384 detail from stratz")
    if raw_match_detail := stratz.get_match_details(8937132384):
        log.info(msg="parsing 8937132384 detail ")
        if valid_match_detail := stratz_match_detail_parser(raw_match_detail):
            log.info(msg="adding 8937132384 detail from stratz")
            database.add_match(valid_match_detail)

    print(database.get_tracked_players())


if __name__ == "__main__":
    main()
