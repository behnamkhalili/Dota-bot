from typing import List
from sqlalchemy import DateTime, Integer, Boolean, ForeignKey, String, BigInteger
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    pass


class PlayerStats(Base):
    __tablename__ = "players_stats"

    id: Mapped[int] = mapped_column(unique=True, primary_key=True)
    steamAccountId: Mapped[int] = mapped_column(BigInteger)
    matchId: Mapped[int] = mapped_column(ForeignKey("matches.matchId"))
    # smurfFlag: Mapped[int] = mapped_column(Integer)
    countryCode: Mapped[str] = mapped_column(String, index=True, nullable=True)
    seasonRank: Mapped[int] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String, index=True)
    realName: Mapped[str] = mapped_column(String, index=True, nullable=True)
    dotaAccountLevel: Mapped[int] = mapped_column(Integer)
    hero: Mapped[str] = mapped_column(String, index=True)
    imp: Mapped[int] = mapped_column(Integer, nullable=True)
    # intentionalFeeding: Mapped[bool] = mapped_column(Boolean, index=True)
    kills: Mapped[int] = mapped_column(Integer)
    deaths: Mapped[int] = mapped_column(Integer)
    assists: Mapped[int] = mapped_column(Integer)
    numLastHits: Mapped[int] = mapped_column(Integer)
    numDenies: Mapped[int] = mapped_column(Integer)
    experiencePerMinute: Mapped[int] = mapped_column(Integer)
    goldPerMinute: Mapped[int] = mapped_column(Integer)
    heroDamage: Mapped[int] = mapped_column(Integer)
    towerDamage: Mapped[int] = mapped_column(Integer)
    heroHealing: Mapped[int] = mapped_column(Integer)
    isRadiant: Mapped[bool] = mapped_column(Boolean, index=True)
    isVictory: Mapped[bool] = mapped_column(Boolean, index=True)
    networth: Mapped[int] = mapped_column(Integer)
    level: Mapped[int] = mapped_column(Integer)
    position: Mapped[str] = mapped_column(String, index=True, nullable=True)
    partyId: Mapped[int] = mapped_column(Integer, nullable=True)
    items: Mapped[List["MatchItem"]] = relationship(
        "MatchItem",
        back_populates="player",
        cascade="all, delete-orphan",
    )
    match: Mapped["Match"] = relationship("Match", back_populates="players")


class Match(Base):
    __tablename__ = "matches"

    matchId: Mapped[int] = mapped_column(BigInteger, unique=True, primary_key=True)
    gameVersionId: Mapped[int] = mapped_column(Integer)
    midLaneOutcome: Mapped[str] = mapped_column(String, index=True, nullable=True)
    topLaneOutcome: Mapped[str] = mapped_column(String, index=True, nullable=True)
    bottomLaneOutcome: Mapped[str] = mapped_column(String, index=True, nullable=True)
    actualRank: Mapped[int] = mapped_column(Integer)
    durationSeconds: Mapped[int] = mapped_column(Integer)
    firstBloodTime: Mapped[int] = mapped_column(Integer)
    regionId: Mapped[int] = mapped_column(Integer)
    didRadiantWin: Mapped[bool] = mapped_column(Boolean, index=True)
    gameMode: Mapped[str] = mapped_column(String, index=True)
    rank: Mapped[int] = mapped_column(Integer)
    startDateTime: Mapped[datetime] = mapped_column(DateTime)
    parsedDateTime: Mapped[datetime] = mapped_column(DateTime,nullable=True)
    endDateTime: Mapped[datetime] = mapped_column(DateTime)
    statsDateTime: Mapped[datetime] = mapped_column(DateTime,nullable=True)
    averageImp: Mapped[int] = mapped_column(Integer,nullable=True)
    towerStatusDire: Mapped[int] = mapped_column(Integer)
    barracksStatusDire: Mapped[int] = mapped_column(Integer)
    towerStatusRadiant: Mapped[int] = mapped_column(Integer)
    barracksStatusRadiant: Mapped[int] = mapped_column(Integer)
    players: Mapped[List["PlayerStats"]] = relationship(
        "PlayerStats",
        back_populates="match",
        cascade="all, delete-orphan",
    )


class MatchItem(Base):
    __tablename__ = "matches_items"
    id: Mapped[int] = mapped_column(unique=True, primary_key=True)
    itemId: Mapped[int] = mapped_column(Integer)
    time: Mapped[int] = mapped_column(Integer)
    matchId: Mapped[int] = mapped_column(ForeignKey("matches.matchId"))
    steamAccountId: Mapped[int] = mapped_column(ForeignKey("players_stats.id"))
    player: Mapped["PlayerStats"] = relationship("PlayerStats", back_populates="items")


"""
class Player(Base):  # TODO complete
    __tablename__ = "players"
    pass
"""

"""class Items(Base):  # TODO complete
    __tablename__ = "items"
    pass
"""
