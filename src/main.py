import time
from typing import Any, Dict, List

from dotenv import load_dotenv
from sqlalchemy import Row

from api_clients import OpenDotaApiClient, SteamApiClient, StratzApiClient
from config import get_settings
from data_processor import (
    MatchHistory,
    StratzMatchDetail,
    steam_api_match_history_parser,
    stratz_match_detail_parser,
)
from database_manager import DatabaseManager
from logging_config import get_logger

load_dotenv()
log = get_logger()

STEAM_WAIT_SLEEP = 0.5
STRATZ_WAIT_SLEEP = 0.5


def extract_match_histories(
    steam_client: SteamApiClient, players: List[Row[Any]]
) -> tuple[List[dict[str, Any]], List[int]]:
    raw_histories: List[dict[str, Any]] = []
    last_matches: List[int] = []
    for player in players:
        if lastmatch := player[3]:
            raw_match_history = steam_client.get_player_match_history(
                account_id=player[0], matches_number=100
            )
        else:
            log.debug(msg=f"no last match for player:{player[1]}")
            raw_match_history = steam_client.get_player_match_history(
                account_id=player[0], matches_number=100
            )
        if raw_match_history:
            raw_histories.append(raw_match_history)
            last_matches.append(lastmatch or 0)
        time.sleep(STEAM_WAIT_SLEEP)  # for api rate limit
    return raw_histories, last_matches


def transform_match_histories(
    raw_histories: List[dict[str, Any]],
    lastmatches: List[int],
    steam_history_parser,
) -> List[MatchHistory] | None:
    matches_to_fetch: Dict[int, MatchHistory] = {}
    counter = 0
    for raw_match_history in raw_histories:
        if valid_match_history := steam_history_parser(raw_match_history):
            for match in valid_match_history:
                if match.match_id > lastmatches[counter]:
                    matches_to_fetch[match.match_id] = match
        else:
            log.error(msg="cant validate matches history.")
            log.debug(msg=f"raw_match_history:{raw_match_history}")
        counter += 1
    if matches_to_fetch:
        sorted_matches_to_fetch = sorted(
            matches_to_fetch.values(), key=lambda m: m.start_time
        )
        return sorted_matches_to_fetch


def extract_match_details(
    stratz_client: StratzApiClient, matches: List[MatchHistory]
) -> List[Dict[str, Any]] | None:
    raw_details = []
    for match in matches:
        if raw_match_detail := stratz_client.get_match_details(match.match_id):
            raw_details.append(raw_match_detail)
        else:
            log.error(msg=f"cant fetch data of match:{match.match_id} from stratz")
        time.sleep(STRATZ_WAIT_SLEEP)
    return raw_details


def transform_match_details(
    raw_details: List[Dict[str, Any]], stratz_match_parser
) -> List[StratzMatchDetail] | None:
    valid_match_details_list = []
    for match in raw_details:
        if valid_match_detail := stratz_match_parser(match):
            valid_match_details_list.append(valid_match_detail)
    return valid_match_details_list


def load_matches(db: DatabaseManager, match_details: List[StratzMatchDetail]) -> None:
    for valid_match_detail in match_details:
        db.add_match(valid_match_detail)


def main(
    steam: SteamApiClient,
    database: DatabaseManager,
    opendota: OpenDotaApiClient,
    stratz: StratzApiClient,
    steam_history_parser,
    stratz_match_parser,
):

    if tracked_players := database.get_tracked_players():
        log.debug(msg=f"tracked players : {[player[1] for player in tracked_players]}")
        raw_histories, last_matches = extract_match_histories(
            steam_client=steam, players=tracked_players
        )
        if raw_histories and last_matches:
            if histories := transform_match_histories(
                raw_histories, last_matches, steam_history_parser
            ):
                if raw_details := extract_match_details(
                    stratz_client=stratz, matches=histories
                ):
                    if details := transform_match_details(
                        raw_details, stratz_match_parser
                    ):
                        load_matches(db=database, match_details=details)


if __name__ == "__main__":
    settings = get_settings()

    steam = SteamApiClient(key=settings.steam_api_key)
    stratz = StratzApiClient(token=settings.stratz_api_key)
    opendota = OpenDotaApiClient()
    database = DatabaseManager()

    steam_history_parser = steam_api_match_history_parser
    stratz_match_parser = stratz_match_detail_parser

    main(steam, database, opendota, stratz, steam_history_parser, stratz_match_parser)  # type: ignore
