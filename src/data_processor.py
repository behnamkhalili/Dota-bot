from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Optional
from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


class StatsItem(BaseModel):
    itemId: int
    time: int
    matchId: int
    steamAccountId: int


class StratzPlayer(BaseModel):
    steamAccountId: int
    matchId: int
    smurfFlag: Optional[int] = 999
    countryCode: Optional[str] = "N/A"
    seasonRank: Optional[int] = 999
    name: str
    realName: Optional[str] = "N/A"
    dotaAccountLevel: int
    hero: str
    imp: Optional[int] = 999
    kills: int
    deaths: int
    assists: int
    intentionalFeeding: Optional[bool] = False
    numLastHits: int
    numDenies: int
    experiencePerMinute: int
    goldPerMinute: int
    heroDamage: int
    towerDamage: int
    heroHealing: int
    isRadiant: bool
    isVictory: bool
    networth: int
    level: int
    position: Optional[str] = "N/A"
    partyId: Optional[int] = 999
    itemPurchases: Optional[list[StatsItem]] = []

    @model_validator(mode="before")
    @classmethod
    def player_data_flatter(cls, player_data: dict[str, Any]):
        player_data["hero"] = player_data["hero"].get("shortName")
        player_data["smurfFlag"] = player_data["steamAccount"].get("smurfFlag")
        player_data["countryCode"] = player_data["steamAccount"].get("countryCode")
        player_data["seasonRank"] = player_data["steamAccount"].get("seasonRank")
        player_data["name"] = player_data["steamAccount"].get("name")
        player_data["realName"] = player_data["steamAccount"].get("realName")
        player_data["dotaAccountLevel"] = player_data["steamAccount"].get(
            "dotaAccountLevel"
        )
        player_data["lastMatchDateTime"] = player_data["steamAccount"].get(
            "lastMatchDateTime"
        )
        if items := player_data["stats"].get("itemPurchases"):
            for item in items:
                item["steamAccountId"] = player_data["steamAccountId"]
                item["matchId"] = player_data["matchId"]
        player_data["itemPurchases"] = items
        return player_data

    @field_validator("partyId", "imp", "smurfFlag", "seasonRank", mode="before")
    @classmethod
    def int_parameters_none_handler(cls, v: int | None):
        if v:
            return v
        return 999

    @field_validator("position", "realName", "countryCode", mode="before")
    @classmethod
    def str_parameters_none_handler(cls, v: str | None):
        if v:
            return v
        return "N/A"


class StratzMatchDetail(BaseModel):
    id: int
    gameVersionId: int
    midLaneOutcome: str
    topLaneOutcome: str
    bottomLaneOutcome: str
    actualRank: int
    durationSeconds: int
    firstBloodTime: int
    regionId: int
    didRadiantWin: bool
    gameMode: str
    rank: int
    startDateTime: datetime
    parsedDateTime: Optional[datetime]
    endDateTime: datetime
    statsDateTime: Optional[datetime]
    averageImp: Optional[int] = 999
    towerStatusDire: int
    barracksStatusDire: int
    towerStatusRadiant: int
    barracksStatusRadiant: int
    players: list[StratzPlayer]

    @field_validator(
        "endDateTime", "parsedDateTime", "statsDateTime", "startDateTime", mode="before"
    )
    @classmethod
    def unix_time_to_datetime(cls, unixtime: int):
        if not unixtime:
            unixtime = 1002819727
        return datetime.fromtimestamp(unixtime, tz=ZoneInfo("Asia/Tehran"))

    @field_validator(
        "midLaneOutcome", "topLaneOutcome", "bottomLaneOutcome", mode="before"
    )
    @classmethod
    def lane_outcome_none_handler(cls, v: str | None):
        if v:
            return v
        return "N/A"

    @field_validator("averageImp", mode="before")
    @classmethod
    def int_parameters_none_handler(cls, v: int | None):
        if v:
            return v
        return 999


class OpenDotaPlayer(BaseModel):
    account_id: Optional[int] = 0  # Only public accounts
    rank_tier: Optional[int] = 0  # Only public accounts
    personaname: Optional[str] = "Unknown"  # Only public accounts
    match_id: int
    hero_id: int
    kills: int
    deaths: int
    assists: int
    level: int
    gold_per_min: int
    xp_per_min: int
    last_hits: int
    denies: int
    net_worth: int
    hero_damage: int
    tower_damage: int
    hero_healing: int
    item_0: int
    item_1: int
    item_2: int
    item_3: int
    item_4: int
    item_5: int
    item_neutral: int
    item_neutral2: int
    backpack_0: int
    backpack_1: int
    backpack_2: int
    is_win: bool = Field(
        validation_alias=AliasChoices("win", "is_win")
    )  # The key in api response is "win"
    is_radiant: bool = Field(
        validation_alias=AliasChoices("isRadiant", "is_radiant")
    )  # The key in api response is "isRadiant"
    aghanims_shard: bool
    aghanims_scepter: bool
    moonshard: bool

    @field_validator("rank_tier", "account_id", mode="before")
    @classmethod
    def set_default_if_none(cls, v: int | None) -> int:
        if v is None:
            return 1  # its for unranked accounts and account id is for safety XD
        return v

    @field_validator("personaname", mode="before")
    @classmethod
    def set_default_name_if_none(cls, v: str | None) -> str:
        if v is None:
            return "InvalidName"
        return v


class OpenDotaMatch(BaseModel):
    match_id: int
    start_time: datetime
    duration: int
    radiant_win: bool
    game_mode: int
    lobby_type: int
    first_blood_time: int
    dire_score: int
    radiant_score: int
    tower_status_radiant: int
    tower_status_dire: int
    barracks_status_radiant: int
    barracks_status_dire: int
    patch: int
    region: int
    has_parsed: bool
    players: list[OpenDotaPlayer]

    @model_validator(mode="before")
    @classmethod
    def get_has_parsed(cls, data: dict[str, Any]):
        od_data: dict[str, bool] | None = data.get("od_data")
        if od_data and isinstance(has_parsed_value := od_data.get("has_parsed"), bool):
            data["has_parsed"] = has_parsed_value
        else:
            data["has_parsed"] = False
        return data

    @model_validator(mode="before")
    @classmethod
    def give_players_match_id(cls, data: dict[str, Any]):
        players = data.get("players")
        match_id = data.get("match_id")
        if match_id and players:
            for player in players:
                player["match_id"] = match_id
            data["players"] = players
        return data

    @field_validator("start_time", mode="before")
    @classmethod
    def unix_time_to_datetime(cls, unixtime: int):
        return datetime.fromtimestamp(unixtime, tz=ZoneInfo("Asia/Tehran"))


class MatchHistory(BaseModel):
    match_id: int
    start_time: datetime

    @field_validator("start_time", mode="before")
    @classmethod
    def unix_time_to_datetime(cls, unixtime: int):
        return datetime.fromtimestamp(unixtime, tz=ZoneInfo("Asia/Tehran"))


def open_dota_match_detail_parser(data: dict[str, Any]) -> OpenDotaMatch | None:
    try:
        return OpenDotaMatch.model_validate(data)
    except ValidationError as e:
        print(f"pydantic validation error : {e}")
    return None


def steam_api_match_history_parser(data: dict[str, Any]) -> list[MatchHistory] | None:
    if result := data.get("result"):
        if raw_matches := result.get("matches"):
            matches: list[dict[str, Any]] = raw_matches
            try:
                return [MatchHistory.model_validate(match) for match in matches]
            except ValidationError as e:
                print(f"pydantic validation error : {e}")
    return None


def stratz_match_detail_parser(data: dict[str, Any]) -> StratzMatchDetail | None:
    try:
        match = data.get("data")
        if match:
            return StratzMatchDetail.model_validate(match.get("match"))
    except ValidationError as e:
        print(f"pydantic validation error : {e}")
    return None
