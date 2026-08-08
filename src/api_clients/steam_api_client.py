import time
from typing import Any, Mapping, Optional

import requests

from logging_config import get_logger

log = get_logger()


class SteamApiClient:
    BASE_URL = "https://api.steampowered.com/IDOTA2Match_570/"
    RETRIES = 4

    def __init__(self, key: str) -> None:
        self.s = requests.session()
        self.s.params = {"key": key}

    def _call_api(
        self, url: str, params: Optional[Mapping[str, Any]] = None
    ) -> dict[str, Any] | None:
        for attempt in range(self.RETRIES):
            try:
                response = self.s.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                log.warning(
                    f"an http error on attempt {attempt + 1}/{self.RETRIES}: {e}"
                )
            except requests.exceptions.Timeout as e:
                log.warning(
                    f"timeout error  on attempt {attempt + 1}/{self.RETRIES}: {e}"
                )
            except requests.exceptions.SSLError as e:
                log.warning(f"ssl error  on attempt {attempt + 1}/{self.RETRIES}: {e}")
            except requests.exceptions.ConnectionError as e:
                log.warning(
                    f"connection error  on attempt {attempt + 1}/{self.RETRIES}: {e}"
                )
            except requests.exceptions.RequestException as e:
                log.warning(
                    f"request error  on attempt {attempt + 1}/{self.RETRIES}: {e}"
                )
            except ValueError as e:
                log.warning(
                    f"failed to parse json  on attempt {attempt + 1}/{self.RETRIES}: {e}"
                )
            if attempt < self.RETRIES - 1:
                wait_time = 2**attempt
                time.sleep(wait_time)
        log.error(msg=f"all {self.RETRIES} attemts failed.")
        return None

    def get_player_match_history(
        self, account_id: int, matches_number: int
    ) -> dict[str, Any] | None:
        log.info(msg=f"fetching player:{account_id} match history from steam api.")
        url = f"{self.BASE_URL}GetMatchHistory/v1/"
        params: dict[str, str | int] = {
            "account_id": account_id,
            "matches_requested": matches_number,
        }
        return self._call_api(url, params=params)

    def get_match_details(self, match_id: int) -> dict[str, Any] | None:
        # its not working !
        url = f"{self.BASE_URL}GetMatchDetails/v1/"
        params = {"match_id": match_id}
        return self._call_api(url, params=params)

    def get_heroes(self):
        # its not working !
        url = f"{self.BASE_URL}GetHeroes/v1"
        return self._call_api(url)

    def get_items(self):
        # its not working !
        url = f"{self.BASE_URL}GetGameItems/v1"
        return self._call_api(url)
