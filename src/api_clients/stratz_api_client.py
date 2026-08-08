import time
from typing import Any

import requests

from logging_config import get_logger

log = get_logger()


class StratzApiClient:
    BASE_URL = "https://api.stratz.com/graphql"
    RETRIES = 4
    TIMEOUT = 5

    def __init__(self, token: str) -> None:
        self.s = requests.session()
        self.s.headers = {
            "User-Agent": "STRATZ_API",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _call_api(self, url: str, query: str) -> dict[str, Any] | None:
        for attempt in range(self.RETRIES):
            try:
                response = self.s.post(url, json={"query": query}, timeout=self.TIMEOUT)
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

    def get_match_details(self, match_id: int):
        log.info(msg=f"fetching match:{match_id} detail from stratz")
        query = f"""{{
            match(id: {match_id}) {{
            id
            gameVersionId
            midLaneOutcome
            topLaneOutcome
            bottomLaneOutcome
            actualRank
            durationSeconds
            firstBloodTime
            regionId
            didRadiantWin
            gameMode
            rank
            startDateTime
            parsedDateTime
            endDateTime
            statsDateTime
            averageImp
            towerStatusDire
            barracksStatusDire
            towerStatusRadiant
            barracksStatusRadiant
            players {{
                steamAccountId
                matchId
                steamAccount {{
                smurfFlag
                countryCode
                seasonRank
                name
                realName
                dotaAccountLevel
                }}
                hero {{
                id
                }}
                kills
                deaths
                assists
                imp
                intentionalFeeding
                numLastHits
                experiencePerMinute
                goldPerMinute
                heroDamage
                towerDamage
                heroHealing
                isRadiant
                isVictory
                numDenies
                networth
                level
                position
                partyId
                stats {{
                itemPurchases {{
                    itemId
                    time
                }}
                }}
            }}
            }}
        }}"""
        return self._call_api(self.BASE_URL, query=query)
