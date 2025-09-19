from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from models import Base, Match as MatchModel, PlayerStats as PlayerStatsModel
from data_processor import Match as MatchParser
from datetime import datetime


class DatabaseManager:
    def __init__(self, database_path: str = "sqlite:///database/mydatabase.db") -> None:
        engine = create_engine(database_path)
        self.session = Session(engine)
        Base.metadata.create_all(engine)

    def save_match_data(self, match_detail: MatchParser) -> None:
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
                )
                for p in match_detail.players
            ],
        )
        self.session.add(match)
        try:
            self.session.commit()
            print(f"match:{match_detail.match_id} added in database successfully.")
        except Exception :
            self.session.rollback()
            print (f"the match:{match_detail.match_id} already saved in database !")

    def get_player_last_match_time(self, account_id: int) ->datetime:
        last_match_time_query = select(func.max(MatchModel.start_time)).join(
            PlayerStatsModel, PlayerStatsModel.match_id == MatchModel.match_id
        ).where(PlayerStatsModel.account_id == account_id)
        last_match_time = self.session.execute(last_match_time_query).fetchall()[0][0]
        return last_match_time
