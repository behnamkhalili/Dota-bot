import time
from typing import Any

import requests

from logging_config import get_logger

log = get_logger()


class OpenDotaApiClient:
    BASE_URL = "https://api.opendota.com/api/"
    RETRIES = 4
    TIMEOUT = 5

    def __init__(self) -> None:
        self.s = requests.session()

    def _call_api(self, url: str) -> dict[str, Any] | None:
        for attempt in range(self.RETRIES):
            try:
                response = self.s.get(url, timeout=self.TIMEOUT)
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

    def get_match_details(self, match_id: int) -> dict[str, Any] | None:
        url = f"{self.BASE_URL}matches/{match_id}"
        return self._call_api(url)

    def get_player_match_history(self, account_id: int) -> dict[str, Any] | None:
        url = f"{self.BASE_URL}players/{account_id}/matches"
        return self._call_api(url)

    def get_player_data(self, account_id: int) -> dict[str, Any] | None:
        url = f"{self.BASE_URL}players/{account_id}"
        return self._call_api(url)

    def get_constants(self, resource: str) -> dict[str, Any] | None:
        log.info(msg=f"fetching dota constants:{resource} data from opendota api")
        url = f"{self.BASE_URL}constants/{resource}"
        return self._call_api(url)
