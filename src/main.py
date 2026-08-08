import os
import time

from api_clients.steam_api_client import SteamApiClient
from api_clients.stratz_api_client import StratzApiClient
from data_processor import steam_api_match_history_parser, stratz_match_detail_parser
from database_manager import DatabaseManager
from logging_config import get_logger

#this is just a test for etl 
# i will compelete the etl steps next commits
def main():
    database = DatabaseManager()
    log = get_logger()
    user = os.getenv("Sad_bHnM")

    steam = SteamApiClient(key=os.getenv("STEAM_API_KEY"))
    stratz = StratzApiClient(token=os.getenv("STRATZ_API_KEY"))

    log.info(msg=f"getting {user} match history from steam")
    matches_raw = steam.get_player_match_history(user, 1)
    log.info(msg="matches fetched")

    if matches_raw:
        log.info(msg=f"parsing {user} match history results")
        matches = steam_api_match_history_parser(matches_raw)
        log.info(msg="parsed")

        if matches:
            for match in matches:
                time.sleep(0.1)
                log.info(msg=f"getting {match.match_id} detail from stratz")
                if raw_match_detail := stratz.get_match_details(match.match_id):
                    log.info(msg=f"parsing {match.match_id} detail ")
                    if valid_match_detail := stratz_match_detail_parser(
                        raw_match_detail
                    ):
                        log.info(msg=f"adding {match.match_id} detail from stratz")
                        database.add_match(valid_match_detail)


if __name__ == "__main__":
    main()
