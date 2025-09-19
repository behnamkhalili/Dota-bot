from typing import List
from sqlalchemy import Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass


class PlayerStats(Base):
    __tablename__ = "players_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        Integer, index=True
    )  # ForeignKey("players.account_id") after making the table and relationship
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.match_id"), index=True)
    hero_id: Mapped[int] = mapped_column(
        Integer, index=True
    )  # ForeignKey("heroes.hero_id") after making the table and relationship
    kills: Mapped[int] = mapped_column(Integer)
    deaths: Mapped[int] = mapped_column(Integer)
    assists: Mapped[int] = mapped_column(Integer)
    level: Mapped[int] = mapped_column(Integer)
    gold_per_min: Mapped[int] = mapped_column(Integer)
    xp_per_min: Mapped[int] = mapped_column(Integer)
    last_hits: Mapped[int] = mapped_column(Integer)
    denies: Mapped[int] = mapped_column(Integer)
    net_worth: Mapped[int] = mapped_column(Integer)
    hero_damage: Mapped[int] = mapped_column(Integer)
    tower_damage: Mapped[int] = mapped_column(Integer)
    hero_healing: Mapped[int] = mapped_column(Integer)
    is_win: Mapped[bool] = mapped_column(Boolean, index=True)
    is_radiant: Mapped[bool] = mapped_column(Boolean, index=True)
    match: Mapped["Match"] = relationship("Match", back_populates="players")


class Match(Base):
    __tablename__ = "matches"

    match_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_time: Mapped[datetime] = mapped_column(DateTime,index=True)
    duration: Mapped[int] = mapped_column(Integer)
    radiant_win: Mapped[int] = mapped_column(Boolean, index=True)
    game_mode: Mapped[int] = mapped_column(Integer, index=True)
    lobby_type: Mapped[int] = mapped_column(Integer)
    first_blood_time: Mapped[int] = mapped_column(Integer)
    dire_score: Mapped[int] = mapped_column(Integer)
    radiant_score: Mapped[int] = mapped_column(Integer)
    tower_status_radiant: Mapped[int] = mapped_column(Integer)
    tower_status_dire: Mapped[int] = mapped_column(Integer)
    barracks_status_radiant: Mapped[int] = mapped_column(Integer)
    barracks_status_dire: Mapped[int] = mapped_column(Integer)
    patch: Mapped[int] = mapped_column(Integer, index=True)
    region: Mapped[int] = mapped_column(Integer, index=True)
    has_parsed: Mapped[bool] = mapped_column(Boolean, index=True)
    players: Mapped[List["PlayerStats"]] = relationship(
        "PlayerStats",
        back_populates="match",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Match(match_id={self.match_id!r}, start_time={self.start_time!r}, game_mode={self.game_mode!r})"


"""
class Player(Base):  # TODO complete
    __tablename__ = "players"
    pass
"""

# should make a player_parser and get_player_info and logic for it
# after completing items and heroes and matches_items table
"""class Items(Base):  # TODO complete
    __tablename__ = "items"
    pass
"""

# after completing constants parser


"""class Hero(Base):  # TODO complete
    __tablename__ = "heroes"
    pass"""


# after completing constants parser


"""class MatchItem(Base):  # TODO complete
    __tablename__ = "matches_items"
    pass"""


# after making items table
