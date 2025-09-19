from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    DataError,
    NoSuchTableError,
    NoResultFound,
)
from models import Base, Match as MatchModel, PlayerStats as PlayerStatsModel
from data_processor import Match as MatchParser
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

    def save_match_data(self, match_detail: MatchParser) -> None:
        with self.Session() as session:
            match = MatchModel(
                match_id=match_detail.match_id,
                start_time=match_detail.start_time,
                duration=match_detail.duration,
                radiant_win=match_detail.radiant_win,
                game_mode=match_detail.game_mode,
                lobby_type=match_detail.lobby_type,
                first_blood_time=match_detail.first_blood_time,
                dire_score=match_detail.dire_score,
                radiant_score=match_detail.radiant_score,
                tower_status_dire=match_detail.tower_status_dire,
                tower_status_radiant=match_detail.tower_status_radiant,
                barracks_status_dire=match_detail.barracks_status_dire,
                barracks_status_radiant=match_detail.barracks_status_radiant,
                patch=match_detail.patch,
                region=match_detail.region,
                has_parsed=match_detail.has_parsed,
                players=[
                    PlayerStatsModel(
                        account_id=p.account_id,
                        match_id=p.match_id,
                        hero_id=p.hero_id,
                        kills=p.kills,
                        deaths=p.deaths,
                        assists=p.assists,
                        level=p.level,
                        gold_per_min=p.gold_per_min,
                        xp_per_min=p.xp_per_min,
                        last_hits=p.last_hits,
                        denies=p.denies,
                        net_worth=p.net_worth,
                        hero_damage=p.hero_damage,
                        tower_damage=p.tower_damage,
                        hero_healing=p.hero_healing,
                        is_win=p.is_win,
                        is_radiant=p.is_radiant,
                        rank_tier=p.rank_tier,
                        personaname = p.personaname
                    )
                    for p in match_detail.players
                ],
            )
            try:
                session.add(match)
                session.commit()
                print(f"match:{match_detail.match_id} added in database successfully.")
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
            select(func.max(MatchModel.start_time))
            .join(PlayerStatsModel, PlayerStatsModel.match_id == MatchModel.match_id)
            .where(PlayerStatsModel.account_id == account_id)
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
