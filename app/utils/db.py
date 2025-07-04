import uuid

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.engine.url import make_url


def generate_test_db_name():
    return f'test_{uuid.uuid4().hex[:8]}'


def get_admin_url(database_url: str) -> str:
    url = make_url(database_url)
    url = url.set(drivername='postgresql', database='postgres')
    str_url = url.render_as_string(hide_password=False)
    return str_url


def get_test_db_url(database_url: str, test_db_name: str)  -> str:
    url = make_url(database_url)
    url = url.set(drivername='postgresql+asyncpg', database=test_db_name)
    str_url = url.render_as_string(hide_password=False)
    return str_url


def create_test_database(database_url: str, db_name: str):
    admin_url = get_admin_url(database_url)
    conn = psycopg2.connect(admin_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # DESLIGA transação automática

    with conn.cursor() as cur:
        cur.execute(f'CREATE DATABASE "{db_name}"')

    conn.close()


def drop_test_database(database_url: str, db_name: str):
    admin_url = get_admin_url(database_url)
    conn = psycopg2.connect(admin_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # DESLIGA transação automática

    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{db_name}' AND pid <> pg_backend_pid();
        """)
        cur.execute(f'DROP DATABASE IF EXISTS "{db_name}"')

    conn.close()
