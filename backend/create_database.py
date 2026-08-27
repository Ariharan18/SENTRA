"""Idempotently initialize the local MySQL database and application account."""

import os
import re
from pathlib import Path

import pymysql
from dotenv import load_dotenv


def _load_environment() -> None:
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / ".env", override=False)


def _identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        raise ValueError(f"{label} must contain only letters, numbers, and underscores")
    return f"`{value}`"


def initialize_database() -> None:
    _load_environment()
    database = os.getenv("MYSQL_DATABASE", "traffic_db")
    app_user = os.getenv("MYSQL_USER", "traffic_user")
    app_password = os.getenv("MYSQL_PASSWORD")
    root_password = os.getenv("MYSQL_ROOT_PASSWORD")
    if not root_password:
        raise RuntimeError("MYSQL_ROOT_PASSWORD is required in D:\\traffic\\.env")
    if not app_password:
        raise RuntimeError("MYSQL_PASSWORD is required in D:\\traffic\\.env")

    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    database_sql = _identifier(database, "MYSQL_DATABASE")
    user_sql = _identifier(app_user, "MYSQL_USER")
    connection = pymysql.connect(
        host=host,
        port=port,
        user=os.getenv("MYSQL_ROOT_USER", "root"),
        password=root_password,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {database_sql} "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.execute(
                f"CREATE USER IF NOT EXISTS %s@%s IDENTIFIED BY %s",
                (app_user, host, app_password),
            )
            cursor.execute(
                f"ALTER USER %s@%s IDENTIFIED BY %s",
                (app_user, host, app_password),
            )
            cursor.execute(
                f"GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES "
                f"ON {database_sql}.* TO {user_sql}@%s",
                (host,),
            )
            cursor.execute("FLUSH PRIVILEGES")
    finally:
        connection.close()

    check = pymysql.connect(
        host=host,
        port=port,
        user=app_user,
        password=app_password,
        database=database,
        charset="utf8mb4",
    )
    check.close()
    print(f"MySQL database and application account are ready: {database}")


if __name__ == "__main__":
    initialize_database()
