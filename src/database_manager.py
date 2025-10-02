from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    DataError,
    NoSuchTableError,
    NoResultFound,
)
from models import Base, Match , PlayerStats , MatchItem
from data_processor import StratzMatchDetail
from datetime import datetime
import os


class DatabaseManager:
    def __init__(
        self,
        database_type: str = "sqlite",
        database_path: str = "./database/mydatabase.db",
    ) -> None:
        path: str = os.path.abspath(database_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        engine = f"{database_type}:///{path}"
        engine = create_engine(engine)
        self.Session = sessionmaker(bind=engine, autoflush=True, expire_on_commit=True)
        Base.metadata.create_all(engine)

    def save_match_data(self, match_detail: StratzMatchDetail) -> None:
        with self.Session() as session:
            match = Match(
                matchId = match_detail.id,
                gameVersionId = match_detail.gameVersionId,
                midLaneOutcome = match_detail.midLaneOutcome,
                topLaneOutcome = match_detail.topLaneOutcome,
                bottomLaneOutcome = match_detail.bottomLaneOutcome,
                actualRank= match_detail.actualRank,
                durationSeconds= match_detail.durationSeconds,
                firstBloodTime= match_detail.firstBloodTime,
                regionId = match_detail.regionId,
                didRadiantWin = match_detail.didRadiantWin,
                gameMode= match_detail.gameMode,
                rank= match_detail.rank,
                startDateTime= match_detail.startDateTime,
                parsedDateTime= match_detail.parsedDateTime,
                endDateTime = match_detail.endDateTime,
                statsDateTime= match_detail.statsDateTime,
                averageImp= match_detail.averageImp,
                towerStatusDire= match_detail.towerStatusDire,
                barracksStatusDire= match_detail.barracksStatusDire,
                towerStatusRadiant= match_detail.towerStatusRadiant,
                barracksStatusRadiant= match_detail.barracksStatusRadiant,
                players=[
                    PlayerStats(
                        steamAccountId = p.steamAccountId,
                        matchId = p.matchId,
                        countryCode = p.countryCode,
                        seasonRank = p.seasonRank,
                        name = p.name,
                        realName = p.realName,
                        dotaAccountLevel = p.dotaAccountLevel,
                        hero= p.hero,
                        imp= p.imp,
                        kills = p.kills,
                        deaths = p.deaths,
                        assists = p.assists,
                        numLastHits= p.numLastHits,
                        numDenies= p.numDenies,
                        experiencePerMinute= p.experiencePerMinute,
                        goldPerMinute= p.goldPerMinute,
                        heroDamage= p.heroDamage,
                        towerDamage= p.towerDamage,
                        heroHealing= p.heroHealing,
                        isRadiant= p.isRadiant,
                        isVictory= p.isVictory,
                        networth= p.networth,
                        level= p.level,
                        position= p.position,
                        partyId= p.partyId,
                        items=[
                            MatchItem(
                                itemId = i.itemId,
                                time = i.time,
                                matchId = i.matchId,
                                steamAccountId = i.steamAccountId
                            )
                            for i in p.itemPurchases
                        ] if p.itemPurchases else []

                    )
                    for p in match_detail.players
                ],
            )
            try:
                session.add(match)
                session.commit()
                print(f"match:{match_detail.id} added in database successfully.")
            except IntegrityError as e  :
                session.rollback()
                print(
                    f"IntegrityError! : {e}"
                )
            except DataError as e:
                session.rollback()
                print(f"invalid data! : {e}")
            except NoSuchTableError as e:
                session.rollback()
                print(f"table not found !: {e}")
            except SQLAlchemyError as e:
                session.rollback()
                print(f"sqlalchemy error : {e}")

    def get_player_last_match_time(self, account_id: int) -> datetime | None:
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
        return None
