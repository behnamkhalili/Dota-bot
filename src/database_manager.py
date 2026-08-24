from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Insert,
    Integer,
    Row,
    Select,
    String,
    Update,
    cast,
    column,
    create_engine,
    or_,
    select,
    update,
    values,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import (
    DataError,
    IntegrityError,
    NoSuchTableError,
    SQLAlchemyError,
)
from sqlalchemy.orm import Session, sessionmaker

from config import get_settings
from data_processor import HeroesData, ItemsData, StratzMatchDetail
from logging_config import get_logger
from models import (
    DimHero,
    DimItem,
    DimPlayer,
    FactItemPurchase,
    FactMatch,
    FactPlayerMatch,
)

log = get_logger()
settings = get_settings()


class DatabaseManager:
    def __init__(self) -> None:
        try:
            engine = create_engine(
                settings.database_url, pool_pre_ping=True, echo=False
            )
            self.Session = sessionmaker(
                bind=engine, autoflush=True, expire_on_commit=True
            )
            log.info(
                msg="Database connected: {}:{}/{}".format(
                    settings.db_connect_host,
                    settings.db_connect_port,
                    settings.db_connect_name,
                )
            )
        except Exception:
            log.error(
                msg="cant connect to database! url:{}:{}/{}".format(
                    settings.db_connect_host,
                    settings.db_connect_port,
                    settings.db_connect_name,
                )
            )

    def add_match(self, match_detail: StratzMatchDetail) -> None:
        with self.Session() as session:
            res = session.get(FactMatch, match_detail.id)
        if res:
            log.info(msg=f"match:{match_detail.id} already is in the database")
            return

        with self.Session() as session:
            players_steamid_id_dict: Dict[int, int] = {}
            if match_detail.players:
                upserted_players_list = self._upsert_players(match_detail, session)

                if upserted_players_list:
                    for player in upserted_players_list:
                        players_steamid_id_dict[player[1]] = player[0]
                else:
                    log.error(
                        msg=f"No player returned from DB for match{match_detail.id}"
                    )
                    return
                log.debug(
                    msg=f"Players map {match_detail.id}:{players_steamid_id_dict}"
                )
            else:
                log.warning(msg=f"match:{match_detail.id} has no players!")

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
                        playerId=players_steamid_id_dict.get(player.steamAccountId),
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
                lastmatch_res = self._add_last_match_id(
                    data=match_detail, session=session
                )
                if lastmatch_res is None:
                    session.rollback()
                    log.error(f"lastMatchId update failed for {match_detail.id}")
                    return
                session.commit()
                log.info(msg=f"match:{match_detail.id} added in database successfully.")
            except IntegrityError as e:
                session.rollback()
                log.error(msg=f"IntegrityError saving match {match_detail.id}: {e}")
            except DataError as e:
                session.rollback()
                log.error(msg=f"invalid data for match {match_detail.id} : {e}")
            except NoSuchTableError as e:
                session.rollback()
                log.error(msg=f"Table not found for match {match_detail.id}!: {e}")
            except SQLAlchemyError as e:
                session.rollback()
                log.error(msg=f"sqlalchemy error saving match {match_detail.id} : {e}")

    def add_items(self, items: list[ItemsData]):
        table = DimItem.__table__
        stmt = insert(table).values(  # pyright: ignore[reportArgumentType]
            [
                {"itemId": item.id, "name": item.name, "cost": item.cost}
                for item in items
            ]
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["itemId"],
            set_={"name": stmt.excluded.name, "cost": stmt.excluded.cost},
        ).returning(table)
        self._exec_stmt([stmt])

    def add_heroes(self, heroes: list[HeroesData]):
        table = DimHero.__table__
        stmt = insert(table).values(  # type: ignore
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
        self._exec_stmt([stmt])

    def _upsert_players(
        self, data: StratzMatchDetail, session: Session | None = None
    ) -> List[Row[Any]] | None:
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
            update(table=table)  # type: ignore
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
        insert_stmt = insert(table).values(  # type: ignore
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

        added_players = self._exec_stmt(
            [update_stmt, insert_stmt], session=session, commit=False
        )
        if (
            isinstance(added_players, list) and len(added_players) == 2
        ):  # if both update and insert stmt worked
            updated_players = added_players[0]
            if updated_players:
                row = [(p[1], p[7], p[8]) for p in updated_players]
                vp = values(
                    column("steamAccountId", BigInteger),
                    column("lastMatchTime", DateTime),
                    column("trackMatches", Boolean),
                    name="temp_updated_players_table",
                ).data(row)
                stmt = (
                    update(table=table)  # type: ignore
                    .where(  # type: ignore
                        table.c.validTo.is_(None),
                        table.c.steamAccountId == vp.c.steamAccountId,
                        vp.c.trackMatches,
                    )
                    .values(
                        trackMatches=True,
                        lastMatchTime=cast(vp.c.lastMatchTime, DateTime),
                    )
                    .returning(table)
                )
                result = self._exec_stmt([stmt], session=session, commit=False)
                if result is None:
                    return None
            return added_players[1]
        return None

    def _add_last_match_id(
        self, data: StratzMatchDetail, session: Session | None
    ):  # add last match time to compare
        table = DimPlayer.__table__
        players = data.players
        update_stmt = (
            update(table=table)  # type: ignore
            .where(
                table.c.validTo.is_(None),
                table.c.trackMatches,
                table.c.steamAccountId.in_([p.steamAccountId for p in players]),
                or_(
                    table.c.lastMatchTime < data.startDateTime,
                    table.c.lastMatchTime.is_(None),
                ),
            )
            .values(lastMatchId=data.id, lastMatchTime=data.startDateTime)
        ).returning(table)
        return self._exec_stmt([update_stmt], commit=False, session=session)

    def set_player_track_status(self, player_steam_id: int, status: bool):
        table = DimPlayer.__table__
        stmt = (
            update(table)  # type: ignore
            .where(table.c.validTo.is_(None), table.c.steamAccountId == player_steam_id)
            .values(trackMatches=status)
        ).returning(table)
        res = self._exec_stmt([stmt])
        if res and res[0]:
            log.info(msg=f"player {player_steam_id}'s status changed to {status}")
            log.debug(msg=res[0])

    def get_tracked_players(self) -> List[Row[Any]] | None:
        table = DimPlayer.__table__
        stmt = select(  # never ever change the order of this list. indexes are hardcoded in etl  # noqa: E501
            table.c.steamAccountId,  # hardcoded index in etl dont change
            table.c.nickname,  # hardcoded index in etl dont change
            table.c.trackMatches,  # hardcoded index in etl dont change
            table.c.lastMatchId,  # hardcoded index in etl dont change
        ).where(table.c.validTo.is_(None), table.c.trackMatches.is_(True))
        res = self._exec_stmt([stmt])
        if res:
            return res[0]

    def _exec_stmt(
        self,
        stmt_list: List[Insert | Update | Select],
        session: Session | None = None,
        commit: bool = True,
    ) -> List[List[Row[Any]]] | None:
        owns_session = session is None
        if owns_session:
            session = self.Session()
        try:
            res_list = []
            for stmt in stmt_list:
                res = session.execute(
                    stmt, execution_options={"populate_existing": True}
                ).fetchall()
                res_list.append(list(res))
            if commit:
                session.commit()
            log.debug(msg=f"{len(res_list)} statements executed.")
            return res_list
        except IntegrityError as e:
            session.rollback()
            log.error(msg=f"IntegrityError! in statement : {e}")
        except DataError as e:
            session.rollback()
            log.error(msg=f"Data error in statement! : {e}")
        except NoSuchTableError as e:
            session.rollback()
            log.error(msg=f"table not found in statement!: {e}")
        except SQLAlchemyError as e:
            session.rollback()
            log.error(msg=f"sqlalchemy error  : {e}")
        finally:
            if owns_session:
                session.close()

        return None
