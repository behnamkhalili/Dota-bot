from datetime import datetime
from typing import Any, Optional
from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


class Player(BaseModel):
    account_id: Optional[int] = 0  # Only public accounts has a visible account_id.
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


class Match(BaseModel):
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
    players: list[Player]

    @model_validator(mode="before")
    @classmethod
    def get_has_parsed(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(has_parsed_value := data["od_data"].get("has_parsed"), bool):
            data["has_parsed"] = has_parsed_value
        else:
            data["has_parsed"] = False

        players: list[dict[str, Any]] = data["players"]
        for player in players:
            player["match_id"] = data["match_id"]
        data["players"] = players
        return data

    @field_validator("start_time", mode="before")
    @classmethod
    def unix_time_to_datetime(cls, unixtime: int) -> datetime:
        return datetime.fromtimestamp(unixtime)


class MatchHistory(BaseModel):
    match_id: int
    start_time: datetime

    @field_validator("start_time", mode="before")
    @classmethod
    def unix_time_to_datetime(cls, unixtime: int) -> datetime:
        return datetime.fromtimestamp(unixtime)


def open_dota_match_detail_parser(data: dict[str, Any]) -> Match | None:
    try:
        return Match.model_validate(data)
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


# TODO OpenDota constants parser
# TODO OpenDota match history parser
