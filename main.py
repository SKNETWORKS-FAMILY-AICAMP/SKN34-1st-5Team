"""
main.py

역할
- Streamlit 앱의 진입점입니다.
- 앱 화면을 렌더링하기 전에 DB bootstrap 과정을 먼저 실행합니다.

부팅 순서
1. DB 연결 상태를 확인한다.
    - 데이터베이스 연결을 확인한다.
    - 데이터베이스 생성이 안되어있으면 생성한다.
2. DB에 적용된 migration 상태를 확인한다.
3. 아직 적용되지 않은 migration 파일이 있으면 추가로 적용한다.
4. DB 준비가 완료되면 Streamlit 화면을 구성한다.
"""
from __future__ import annotations

import os
import hashlib
from pathlib import Path
from urllib.parse import quote_plus

import mysql.connector
import streamlit as st
from dotenv import load_dotenv
from mysql.connector import errorcode
from mysql.connector.connection import MySQLConnection, MySQLCursor
from yoyo import get_backend, read_migrations

load_dotenv()

# 개발 모드 활성화
IS_DEVELOP = True

# 경로 설정: macOS/Windows 모두 동작하도록 pathlib 사용
ROOT_DIR = Path(__file__).resolve().parent
MIGRATION_DIR = ROOT_DIR / "db" / "migration"
MIGRATION_CHECKSUM_TABLE = "migration_file_checksums"

# 데이터베이스 세팅
# 기존 DATABASE_* 이름과 .env.example의 DB_*/MYSQL_PORT 이름을 모두 지원합니다.
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DB_HOST", "127.0.0.1")
DATABASE_PORT = os.getenv("DATABASE_PORT") or os.getenv("MYSQL_PORT", "3306")
DATABASE_USER = os.getenv("DATABASE_USER") or os.getenv("DB_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD") or os.getenv("DB_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME") or os.getenv("DB_NAME")


# 데이터베이스 연결확인
def is_db_connected(db: MySQLConnection) -> bool:
    return db.is_connected()


def validate_database_config() -> None:
    required_values = {
        "DATABASE_URL/DB_HOST": DATABASE_URL,
        "DATABASE_PORT/MYSQL_PORT": DATABASE_PORT,
        "DATABASE_USER/DB_USER": DATABASE_USER,
        "DATABASE_PASSWORD/DB_PASSWORD": DATABASE_PASSWORD,
        "DATABASE_NAME/DB_NAME": DATABASE_NAME,
    }
    missing_keys = [key for key, value in required_values.items() if not value]

    if missing_keys:
        raise RuntimeError(f"DB 환경변수가 누락되었습니다: {', '.join(missing_keys)}")


# 데이터베이스 생성합니다.
def set_database(cursor: MySQLCursor) -> None:
    cursor.execute(
        f"""
        CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci
        """
    )


# 데이터베이스 연결 시도합니다.
def get_connection(database: str | None = None) -> MySQLConnection:
    validate_database_config()
    connection_options = {
        "host": DATABASE_URL,
        "port": int(DATABASE_PORT),
        "user": DATABASE_USER,
        "password": DATABASE_PASSWORD,
    }

    if database:
        connection_options["database"] = database

    return mysql.connector.connect(**connection_options)


def get_db_url() -> str:
    validate_database_config()
    user = quote_plus(DATABASE_USER)
    password = quote_plus(DATABASE_PASSWORD)

    return (
        "mysql://"
        f"{user}:{password}"
        f"@{DATABASE_URL}:{DATABASE_PORT}"
        f"/{DATABASE_NAME}"
    )


def get_migration_backend():
    return get_backend(get_db_url())


def close_migration_backend(backend) -> None:
    connection = getattr(backend, "_connection", None)

    if connection is not None:
        connection.close()


def get_migrations():
    if not MIGRATION_DIR.exists():
        return []

    return read_migrations(str(MIGRATION_DIR))


def get_migration_file_checksums() -> dict[str, str]:
    checksums = {}

    for migration in get_migrations():
        migration_path = Path(migration.path)
        digest = hashlib.sha256(migration_path.read_bytes()).hexdigest()
        checksums[migration.id] = digest

    return checksums


def ensure_migration_checksum_table(cursor: MySQLCursor) -> None:
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS `{MIGRATION_CHECKSUM_TABLE}` (
            migration_id VARCHAR(255) PRIMARY KEY,
            checksum CHAR(64) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
        )
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci
        """
    )


def validate_migration_checksums() -> None:
    current_checksums = get_migration_file_checksums()
    connection = get_connection(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        ensure_migration_checksum_table(cursor)
        cursor.execute(f"SELECT migration_id, checksum FROM `{MIGRATION_CHECKSUM_TABLE}`")

        for migration_id, recorded_checksum in cursor.fetchall():
            current_checksum = current_checksums.get(migration_id)

            if current_checksum is None:
                raise RuntimeError(f"이미 적용된 migration 파일이 삭제되었습니다: {migration_id}")

            if current_checksum != recorded_checksum:
                raise RuntimeError(f"이미 적용된 migration 파일이 수정되었습니다: {migration_id}")

        connection.commit()
    finally:
        cursor.close()
        connection.close()


def record_migration_checksums() -> None:
    current_checksums = get_migration_file_checksums()

    if not current_checksums:
        return

    connection = get_connection(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        ensure_migration_checksum_table(cursor)

        for migration_id, checksum in current_checksums.items():
            cursor.execute(
                f"""
                INSERT INTO `{MIGRATION_CHECKSUM_TABLE}` (migration_id, checksum)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE migration_id = migration_id
                """,
                (migration_id, checksum),
            )

        connection.commit()
    finally:
        cursor.close()
        connection.close()


def get_pending_migrations():
    backend = get_migration_backend()
    migrations = get_migrations()

    try:
        return backend.to_apply(migrations)
    finally:
        close_migration_backend(backend)


def check_migrations() -> bool:
    pending = get_pending_migrations()

    if pending:
        print("적용되지 않은 migration이 있습니다.")
        for migration in pending:
            print("-", migration.id)
        return False

    print("migration 상태가 최신입니다.")
    return True


def apply_migrations() -> None:
    backend = get_migration_backend()
    migrations = get_migrations()

    try:
        pending = backend.to_apply(migrations)

        if not pending:
            print("적용할 migration이 없습니다.")
            return

        with backend.lock():
            backend.apply_migrations(pending)

        print("migration 적용 완료")
    finally:
        close_migration_backend(backend)


def ensure_database() -> None:
    try:
        connection = get_connection(DATABASE_NAME)
    except mysql.connector.Error as error:
        if error.errno != errorcode.ER_BAD_DB_ERROR:
            raise
    else:
        try:
            if not is_db_connected(connection):
                raise RuntimeError("?곗씠?곕쿋?댁뒪 ?쒕쾭???곌껐?섏? ?딆븯?듬땲??")
            return
        finally:
            connection.close()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        if not is_db_connected(connection):
            raise RuntimeError("데이터베이스 서버에 연결되지 않았습니다.")

        set_database(cursor)
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def bootstrap_database() -> None:
    ensure_database()
    validate_migration_checksums()

    if not check_migrations():
        apply_migrations()

    record_migration_checksums()


# 시작함수
def run() -> None:
    dashboard = st.Page("src/pages/dashboard_page.py", title="대시보드",default=True)
    fqa = st.Page("src/pages/faq_page.py", title="FAQ")
    map = st.Page("src/pages/map_page.py", title="지도")

    page = st.navigation([dashboard, fqa, map])
    page.run()


if __name__ == "__main__":
    # bootstrap_database()
    run()

