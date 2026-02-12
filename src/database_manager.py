from dataclasses import dataclass
from typing import Optional
from sqlalchemy import create_engine, select, func, case
from sqlalchemy.orm import sessionmaker, Mapped
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    DataError,
    NoSuchTableError,
    NoResultFound,
)
from models import Base, Match, PlayerStats, MatchItem
from data_processor import StratzMatchDetail
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()


@dataclass
class PlayerMaxStat:
    value: int
    matchid: int
    playername: str
    heroname: str


@dataclass
class MatchDurationDetails:
    longest: int
    shortest: int
    avg: int


class DatabaseManager:
    def __init__(
        self,
        user: str | None = os.getenv("DB_USER"),
        password: str | None = os.getenv("DB_PASS"),
        db_name: str | None = os.getenv("DB_NAME"),
        db_host: str | None = os.getenv("DB_HOST"),
        db_port: str | None = os.getenv("DB_PORT"),
    ) -> None:
        engine = f"postgresql+psycopg2://{user}:{password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(engine)
        self.Session = sessionmaker(bind=engine, autoflush=True, expire_on_commit=True)
        Base.metadata.create_all(engine)

    def save_match_data(self, match_detail: StratzMatchDetail) -> None:
        with self.Session() as session:
            match = Match(
                matchId=match_detail.id,
                gameVersionId=match_detail.gameVersionId,
                midLaneOutcome=match_detail.midLaneOutcome,
                topLaneOutcome=match_detail.topLaneOutcome,
                bottomLaneOutcome=match_detail.bottomLaneOutcome,
                actualRank=match_detail.actualRank,
                durationSeconds=match_detail.durationSeconds,
                firstBloodTime=match_detail.firstBloodTime,
                regionId=match_detail.regionId,
                didRadiantWin=match_detail.didRadiantWin,
                gameMode=match_detail.gameMode,
                rank=match_detail.rank,
                startDateTime=match_detail.startDateTime,
                parsedDateTime=match_detail.parsedDateTime,
                endDateTime=match_detail.endDateTime,
                statsDateTime=match_detail.statsDateTime,
                averageImp=match_detail.averageImp,
                towerStatusDire=match_detail.towerStatusDire,
                barracksStatusDire=match_detail.barracksStatusDire,
                towerStatusRadiant=match_detail.towerStatusRadiant,
                barracksStatusRadiant=match_detail.barracksStatusRadiant,
                players=[
                    PlayerStats(
                        steamAccountId=p.steamAccountId,
                        matchId=p.matchId,
                        countryCode=p.countryCode,
                        seasonRank=p.seasonRank,
                        name=p.name,
                        realName=p.realName,
                        dotaAccountLevel=p.dotaAccountLevel,
                        hero=p.hero,
                        imp=p.imp,
                        kills=p.kills,
                        deaths=p.deaths,
                        assists=p.assists,
                        numLastHits=p.numLastHits,
                        numDenies=p.numDenies,
                        experiencePerMinute=p.experiencePerMinute,
                        goldPerMinute=p.goldPerMinute,
                        heroDamage=p.heroDamage,
                        towerDamage=p.towerDamage,
                        heroHealing=p.heroHealing,
                        isRadiant=p.isRadiant,
                        isVictory=p.isVictory,
                        networth=p.networth,
                        level=p.level,
                        position=p.position,
                        partyId=p.partyId,
                        items=[
                            MatchItem(
                                itemId=i.itemId,
                                time=i.time,
                                matchId=i.matchId,
                                steamAccountId=i.steamAccountId,
                            )
                            for i in p.itemPurchases
                        ]
                        if p.itemPurchases
                        else [],
                    )
                    for p in match_detail.players
                ],
            )
            try:
                session.add(match)
                session.commit()
                print(f"match:{match_detail.id} added in database successfully.")
            except IntegrityError as e:
                session.rollback()
                print(f"IntegrityError! : {e}")
            except DataError as e:
                session.rollback()
                print(f"invalid data! : {e}")
            except NoSuchTableError as e:
                session.rollback()
                print(f"table not found !: {e}")
            except SQLAlchemyError as e:
                session.rollback()
                print(f"sqlalchemy error : {e}")

    def get_player_last_match_time(self, account_id: int) -> Optional[datetime]:
        last_match_time_query = (
            select(func.max(Match.startDateTime))
            .join(PlayerStats, PlayerStats.matchId == Match.matchId)
            .where(PlayerStats.steamAccountId == account_id)
        )
        try:
            with self.Session() as session:
                last_match_time = session.execute(last_match_time_query).scalar_one()
                return last_match_time
        except NoResultFound as e:
            print(f"no result found ! : {e}")
        except SQLAlchemyError as e:
            print(f"sqlalchemy error : {e}")

    def get_player_max_stats_in_ranked(self, stats_var: Mapped[int]) -> PlayerMaxStat:
        max_stat_query = (
            select(
                func.coalesce(func.max(stats_var), 0),
                func.coalesce(PlayerStats.matchId, 0),
                func.coalesce(PlayerStats.name, "No data"),
                func.coalesce(PlayerStats.hero, "No data"),
            )
            .join(PlayerStats.match)
            .where(Match.gameMode == "ALL_PICK_RANKED")
        )
        try:
            with self.Session() as session:
                max_stat = session.execute(max_stat_query).one()
                if max_stat:
                    return PlayerMaxStat(
                        value=max_stat[0],
                        matchid=max_stat[1],
                        playername=max_stat[2],
                        heroname=max_stat[3],
                    )
        except NoResultFound as e:
            print(f"no result found ! : {e}")
        except SQLAlchemyError as e:
            print(f"sqlalchemy error : {e}")
        return PlayerMaxStat(
            value=0,
            matchid=0,
            playername="No data",
            heroname="No data",
        )

    def get_match_duration_details(self) -> MatchDurationDetails:
        match_duration_details_query = select(
            func.coalesce(func.max(Match.durationSeconds), 0),
            func.coalesce(func.min(Match.durationSeconds), 0),
            func.coalesce(func.avg(Match.durationSeconds), 0),
        ).where(Match.gameMode == "ALL_PICK_RANKED")
        try:
            with self.Session() as session:
                match_duration_details = session.execute(
                    match_duration_details_query
                ).one()
                if match_duration_details:
                    return MatchDurationDetails(
                        longest=match_duration_details[0],
                        shortest=match_duration_details[1],
                        avg=match_duration_details[2],
                    )
        except NoResultFound as e:
            print(f"No result found! : {e}")
        except SQLAlchemyError as e:
            print(f"sqlalchemy error : {e}")
        return MatchDurationDetails(
            longest=0,
            shortest=0,
            avg=0,
        )

    def get_most_bloody_match(self):  # TODO must get teams total kill from api
        pass

    def get_biggest_comeback_match(self):  # TODO must get teams total kill from api
        pass

    def get_radiant_dire_wins(self, limit: int = 1000) -> dict[str, int]:
        radiant_dire_wins_query = (
            select(
                func.sum(case((Match.didRadiantWin, 1), else_=0)),
                func.sum(case((Match.didRadiantWin == False, 1), else_=0)),  # noqa: E712
            )
            .select_from(Match)
            .where(
                Match.startDateTime.in_(
                    select(Match.startDateTime)
                    .order_by(Match.startDateTime.desc())
                    .limit(limit)
                )
            )
        )

        try:
            with self.Session() as session:
                radiant_dire_wins_count = session.execute(radiant_dire_wins_query).one()
                if radiant_dire_wins_count:
                    return {
                        "Radiant": radiant_dire_wins_count[0],
                        "Dire": radiant_dire_wins_count[1],
                    }
        except NoResultFound as e:
            print(f"No result found! : {e}")
        except SQLAlchemyError as e:
            print(f"sqlalchemy error : {e}")
        return {"Radiant": 0, "Dire": 0}
