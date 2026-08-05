from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy import (
    BigInteger,
    Insert,
    Integer,
    Row,
    String,
    Update,
    create_engine,
    or_,
    update,
    values,
    column,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    DataError,
    NoSuchTableError,
)
from models import (
    Base,
    DimHero,
    DimItem,
    DimPlayer,
    FactItemPurchase,
    FactMatch,
    FactPlayerMatch,
)

from data_processor import StratzMatchDetail, ItemsData, HeroesData
import os
from dotenv import load_dotenv


load_dotenv()


class DatabaseManager:
    def __init__(self) -> None:
        user = os.getenv("DB_CONNECT_USER")
        password = os.getenv("DB_CONNECT_PASS")
        db_name = os.getenv("DB_CONNECT_NAME")
        db_host = os.getenv("DB_CONNECT_HOST")
        db_port = os.getenv("DB_CONNECT_PORT")
        database_url = (
            f"postgresql+psycopg2://{user}:{password}@{db_host}:{db_port}/{db_name}"
        )
        engine = create_engine(database_url, pool_pre_ping=True, echo=False)
        self.Session = sessionmaker(bind=engine, autoflush=True, expire_on_commit=True)
        Base.metadata.create_all(engine)

    def add_match(self, match_detail: StratzMatchDetail) -> None:

        upserted_players_list = self._upsert_players(match_detail)
        players_steamid_id_dict: Dict[int, int] = {}

        if upserted_players_list:
            for player in upserted_players_list:
                players_steamid_id_dict[player[1]] = player[0]
        else:
            raise Exception("no player returned from database")

        print(players_steamid_id_dict)

        with self.Session() as session:
            data = FactMatch(
                matchId=match_detail.id,
                didRadiantWin=match_detail.didRadiantWin,
                midLaneOutcome=match_detail.midLaneOutcome,
                topLaneOutcome=match_detail.topLaneOutcome,
                bottomLaneOutcome=match_detail.bottomLaneOutcome,
                averageRank=match_detail.actualRank,
                durationSeconds=match_detail.durationSeconds,
                firstBloodTime=match_detail.firstBloodTime,
                gameVersionId=match_detail.gameVersionId,
                regionId=match_detail.regionId,
                gameMode=match_detail.gameMode,
                startDateTime=match_detail.startDateTime,
                endDateTime=match_detail.endDateTime,
                averageImp=match_detail.averageImp,
                towerStatusDire=match_detail.towerStatusDire,
                barracksStatusDire=match_detail.barracksStatusDire,
                towerStatusRadiant=match_detail.towerStatusRadiant,
                barracksStatusRadiant=match_detail.barracksStatusRadiant,
                players=[
                    FactPlayerMatch(
                        playerId=players_steamid_id_dict[player.steamAccountId],
                        matchId=player.matchId,
                        heroId=player.heroId,
                        imp=player.imp,
                        kills=player.kills,
                        deaths=player.deaths,
                        assists=player.assists,
                        numLastHits=player.numLastHits,
                        numDenies=player.numDenies,
                        experiencePerMinute=player.experiencePerMinute,
                        goldPerMinute=player.goldPerMinute,
                        heroDamage=player.heroDamage,
                        towerDamage=player.towerDamage,
                        heroHealing=player.heroHealing,
                        isRadiant=player.isRadiant,
                        isVictory=player.isVictory,
                        networth=player.networth,
                        level=player.level,
                        position=player.position,
                        partyId=player.partyId,
                        items=[
                            FactItemPurchase(
                                purchaseTime=item.time,
                                itemId=item.itemId,
                                matchId=item.matchId,
                            )
                            for item in (player.itemPurchases or [])
                        ],
                    )
                    for player in match_detail.players
                ],
            )
            try:
                session.add(data)
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

    def add_items(self, items: list[ItemsData]):
        table = DimItem.__table__
        stmt = insert(table).values(
            [
                {"itemId": item.id, "name": item.name, "cost": item.cost}
                for item in items
            ]
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["itemId"],
            set_={"name": stmt.excluded.name, "cost": stmt.excluded.cost},
        ).returning(table)
        self._exec_stmt(stmt)

    def add_heroes(self, heroes: list[HeroesData]):
        table = DimHero.__table__
        stmt = insert(table).values(
            [
                {
                    "heroId": hero.id,
                    "name": hero.localized_name,
                    "primaryAttr": hero.primary_attr,
                    "attackType": hero.attack_type,
                }
                for hero in heroes
            ]
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["heroId"],
            set_={
                "heroId": stmt.excluded.heroId,
                "name": stmt.excluded.name,
                "primaryAttr": stmt.excluded.primaryAttr,
                "attackType": stmt.excluded.attackType,
            },
        ).returning(table)
        self._exec_stmt(stmt)

    def _upsert_players(self, data: StratzMatchDetail):
        table = DimPlayer.__table__
        players = data.players
        row_data = [(p.steamAccountId, p.name, p.seasonRank) for p in players]
        match_time = datetime.now()
        v = values(
            column("steamAccountId", BigInteger),
            column("nickname", String),
            column("rank", Integer),
            name="temp_table",
        ).data(row_data)

        # update the old records.
        update_stmt = (
            update(table=table)
            .where(
                table.c.validTo.is_(None),
                table.c.steamAccountId == v.c.steamAccountId,
                or_(
                    table.c.rank.is_distinct_from(v.c.rank),
                    table.c.nickname.is_distinct_from(v.c.nickname),
                ),
            )
            .values(validTo=match_time)
        ).returning(table)
        # insert new rows and skip the existed ones. ps: i used update for returning.
        insert_stmt = insert(table).values(
            [
                {
                    "steamAccountId": p.steamAccountId,
                    "nickname": p.name,
                    "countryCode": p.countryCode,
                    "realName": p.realName,
                    "rank": p.seasonRank,
                    "validFrom": match_time,
                    "validTo": None,
                }
                for p in players
            ]
        )
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["steamAccountId"],
            index_where=(table.c.validTo.is_(None)),
            set_={
                "steamAccountId": insert_stmt.excluded.steamAccountId,
            },
        ).returning(table)
        self._exec_stmt(update_stmt)
        added_players = self._exec_stmt(insert_stmt)
        if added_players:
            return added_players
        return None

    def _exec_stmt(self, stmt: Insert | Update) -> List[Row[Any]] | None:
        with self.Session() as session:
            try:
                res = session.execute(
                    stmt, execution_options={"populate_existing": True}
                ).fetchall()
                session.commit()
                print("executed")
                return list(res)
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
            return None
