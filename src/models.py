from typing import List
from sqlalchemy import DateTime, Integer, Boolean, ForeignKey, String, BigInteger, null
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy.schema import Index


class Base(DeclarativeBase):
    pass


# dim tables:
class DimPlayer(Base):
    __tablename__ = "dim_player"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, unique=True)
    steamAccountId: Mapped[int] = mapped_column(BigInteger)
    nickname: Mapped[str] = mapped_column(String)  #
    countryCode: Mapped[str] = mapped_column(String,nullable=True)
    realName: Mapped[str] = mapped_column(String,nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=True)  #
    validFrom: Mapped[datetime] = mapped_column(DateTime)
    validTo: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    __table_args__ = (
        Index(
            "idx_steamid_validto",
            "steamAccountId",
            unique=True,
            postgresql_where=(validTo.is_(null())),
        ),
    )


class DimHero(Base):
    __tablename__ = "dim_hero"
    heroId: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String)
    primaryAttr: Mapped[str] = mapped_column(String)
    attackType: Mapped[str] = mapped_column(String)


class DimItem(Base):
    __tablename__ = "dim_item"
    itemId: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String)
    cost: Mapped[int] = mapped_column(Integer)


# fact tables:


class FactMatch(Base):
    __tablename__ = "fact_match"

    matchId: Mapped[int] = mapped_column(BigInteger, unique=True, primary_key=True)

    didRadiantWin: Mapped[bool] = mapped_column(Boolean)
    midLaneOutcome: Mapped[str] = mapped_column(String, nullable=True)
    topLaneOutcome: Mapped[str] = mapped_column(String, nullable=True)
    bottomLaneOutcome: Mapped[str] = mapped_column(String, nullable=True)
    averageRank: Mapped[int] = mapped_column(Integer)
    durationSeconds: Mapped[int] = mapped_column(Integer)
    firstBloodTime: Mapped[int] = mapped_column(Integer)
    gameVersionId: Mapped[int] = mapped_column(Integer)
    regionId: Mapped[int] = mapped_column(Integer)
    gameMode: Mapped[str] = mapped_column(String)
    startDateTime: Mapped[datetime] = mapped_column(DateTime)
    endDateTime: Mapped[datetime] = mapped_column(DateTime)
    averageImp: Mapped[int] = mapped_column(Integer, nullable=True)
    towerStatusDire: Mapped[int] = mapped_column(Integer)
    barracksStatusDire: Mapped[int] = mapped_column(Integer)
    towerStatusRadiant: Mapped[int] = mapped_column(Integer)
    barracksStatusRadiant: Mapped[int] = mapped_column(Integer)

    players: Mapped[List["FactPlayerMatch"]] = relationship(
        "FactPlayerMatch",
        back_populates="match",
        cascade="all, delete-orphan",
    )


class FactPlayerMatch(Base):
    __tablename__ = "fact_player_match"

    id: Mapped[int] = mapped_column(unique=True, primary_key=True, autoincrement=True)
    playerId: Mapped[int] = mapped_column(ForeignKey("dim_player.id"))
    matchId: Mapped[int] = mapped_column(ForeignKey("fact_match.matchId"))
    heroId: Mapped[int] = mapped_column(ForeignKey("dim_hero.heroId"))

    imp: Mapped[int] = mapped_column(Integer, nullable=True)
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
    isRadiant: Mapped[bool] = mapped_column(Boolean)
    isVictory: Mapped[bool] = mapped_column(Boolean)
    networth: Mapped[int] = mapped_column(Integer)
    level: Mapped[int] = mapped_column(Integer)
    position: Mapped[str] = mapped_column(String, nullable=True)
    partyId: Mapped[int] = mapped_column(Integer, nullable=True)

    """player: Mapped[DimPlayer] = relationship("DimPlayer")
    hero: Mapped[DimHero] = relationship("DimHero")"""

    match: Mapped[FactMatch] = relationship("FactMatch", back_populates="players")
    items: Mapped[List["FactItemPurchase"]] = relationship(
        "FactItemPurchase",
        back_populates="player",
        cascade="all, delete-orphan",
    )


class FactItemPurchase(Base):
    __tablename__ = "fact_item_purchase"

    id: Mapped[int] = mapped_column(unique=True, primary_key=True, autoincrement=True)
    purchaseTime: Mapped[int] = mapped_column(Integer)

    itemId: Mapped[int] = mapped_column(ForeignKey("dim_item.itemId"))
    matchId: Mapped[int] = mapped_column(ForeignKey("fact_match.matchId"))
    MatchPlayerId: Mapped[int] = mapped_column(ForeignKey("fact_player_match.id"))

    item: Mapped[DimItem] = relationship("DimItem")
    player: Mapped[FactPlayerMatch] = relationship(
        "FactPlayerMatch", back_populates="items"
    )
