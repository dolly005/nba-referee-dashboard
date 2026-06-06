from __future__ import annotations

import os
from datetime import date, datetime, timezone
from typing import Any

import pandas as pd
import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is missing. Please check backend/.env")
    return database_url


def get_connection():
    return psycopg.connect(get_database_url())


def get_table_columns(conn, table_name: str) -> set[str]:
    sql = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
    """

    with conn.cursor() as cur:
        cur.execute(sql, (table_name,))
        return {row[0] for row in cur.fetchall()}


def upsert_dataframe(
    conn,
    table_name: str,
    df: pd.DataFrame,
    conflict_columns: list[str],
) -> int:
    """
    只寫入資料表實際存在的欄位。
    這樣可以避免 DataFrame 有多餘欄位導致錯誤。
    """
    if df.empty:
        return 0

    table_columns = get_table_columns(conn, table_name)

    usable_columns = [
        col for col in df.columns
        if col in table_columns
    ]

    if not usable_columns:
        print(f"[upsert_dataframe] No usable columns for {table_name}")
        return 0

    for conflict_col in conflict_columns:
        if conflict_col not in usable_columns:
            raise ValueError(
                f"{table_name} missing conflict column: {conflict_col}"
            )

    insert_columns_sql = ", ".join(usable_columns)
    placeholders_sql = ", ".join([f"%({col})s" for col in usable_columns])
    conflict_sql = ", ".join(conflict_columns)

    update_columns = [
        col for col in usable_columns
        if col not in conflict_columns
    ]

    if update_columns:
        update_sql = ", ".join([
            f"{col} = EXCLUDED.{col}"
            for col in update_columns
        ])
        conflict_action_sql = f"DO UPDATE SET {update_sql}"
    else:
        conflict_action_sql = "DO NOTHING"

    sql = f"""
        INSERT INTO {table_name} ({insert_columns_sql})
        VALUES ({placeholders_sql})
        ON CONFLICT ({conflict_sql}) {conflict_action_sql}
    """

    clean_df = df[usable_columns].where(pd.notna(df[usable_columns]), None)
    records = clean_df.to_dict("records")

    with conn.cursor() as cur:
        cur.executemany(sql, records)

    return len(records)


def create_update_log(conn, target_date: date, source: str = "nba_api") -> int:
    sql = """
        INSERT INTO update_logs (
            target_date,
            source,
            status,
            started_at
        )
        VALUES (%s, %s, 'running', %s)
        RETURNING id
    """

    with conn.cursor() as cur:
        cur.execute(sql, (target_date, source, datetime.now(timezone.utc)))
        return cur.fetchone()[0]


def finish_update_log(
    conn,
    log_id: int,
    status: str,
    games_count: int = 0,
    referees_count: int = 0,
    game_referees_count: int = 0,
    error_message: str | None = None,
):
    sql = """
        UPDATE update_logs
        SET finished_at = %s,
            status = %s,
            games_count = %s,
            referees_count = %s,
            game_referees_count = %s,
            error_message = %s
        WHERE id = %s
    """

    with conn.cursor() as cur:
        cur.execute(
            sql,
            (
                datetime.now(timezone.utc),
                status,
                games_count,
                referees_count,
                game_referees_count,
                error_message,
                log_id,
            ),
        )


def load_daily_data(
    transformed: dict[str, pd.DataFrame],
    target_date: date,
) -> dict[str, Any]:
    """
    符合你目前資料庫的 Load 流程：

    1. UPSERT games
    2. UPSERT game_officials
    3. 寫 update_logs
    """
    with get_connection() as conn:
        log_id = create_update_log(conn, target_date)
        conn.commit()

        try:
            games_count = upsert_dataframe(
                conn=conn,
                table_name="games",
                df=transformed["games"],
                conflict_columns=["game_id"],
            )

            game_officials_count = upsert_dataframe(
                conn=conn,
                table_name="game_officials",
                df=transformed["game_officials"],
                conflict_columns=["game_id", "official_id"],
            )

            finish_update_log(
                conn=conn,
                log_id=log_id,
                status="success",
                games_count=games_count,
                referees_count=0,
                game_referees_count=game_officials_count,
            )

            conn.commit()

            return {
                "status": "success",
                "log_id": log_id,
                "games_count": games_count,
                "game_officials_count": game_officials_count,
                "target_date": str(target_date),
            }

        except Exception as exc:
            conn.rollback()

            with get_connection() as error_conn:
                finish_update_log(
                    conn=error_conn,
                    log_id=log_id,
                    status="failed",
                    error_message=str(exc),
                )
                error_conn.commit()

            raise