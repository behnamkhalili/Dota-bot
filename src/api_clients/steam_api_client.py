import time
from typing import Any, Mapping, Optional
import requests


class SteamApiClient:
    BASE_URL = "https://api.steampowered.com/IDOTA2Match_570/"
    RETRIES = 4

    def __init__(self, key: str) -> None:
        self.key = key
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
                print(f"an http error occurred : {e}")
            except requests.exceptions.Timeout as e:
                print(f"request timeout error : {e}")
            except requests.exceptions.SSLError as e:
                print(f"an ssl error occurred : {e}")
            except requests.exceptions.ConnectionError as e:
                print(f"connection error : {e}")
            except requests.exceptions.RequestException as e:
                print(f"request error : {e}")
            except ValueError as e:
                print(f"failed to parse json : {e}")
            if attempt < self.RETRIES - 1:
                wait_time = 2**attempt
                time.sleep(wait_time)
        print("failed to call api !")
        return None

    def get_player_match_history(
        self, account_id: int, matches_number: int
    ) -> dict[str, Any] | None:
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
