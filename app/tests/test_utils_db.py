import re
from unittest.mock import MagicMock, patch

from app.utils.db import (
    create_test_database,
    drop_test_database,
    generate_test_db_name,
    get_admin_url,
    get_test_db_url,
)


def test_generate_test_db_name():
    """
    Checks if the generated test database name starts with 'test_'
    and has exactly 8 hexadecimal characters after the prefix.
    """
    db_name = generate_test_db_name()
    assert db_name.startswith('test_')
    assert re.match(r'^test_[0-9a-f]{8}$', db_name)


def test_get_admin_url():
    """
    Verifies that the admin URL is correctly generated from the given
    database URL, replacing the database name with 'postgres' and switching to the
    'postgresql' driver.
    """
    base_url = 'postgresql+asyncpg://user:pass@localhost/testdb'
    result = get_admin_url(base_url)
    assert result.startswith('postgresql://user:pass@localhost')
    assert 'testdb' not in result
    assert 'postgres' in result


def test_get_test_db_url():
    """
    Ensures the test database URL is correctly built with the given
    database name and uses the 'postgresql+asyncpg' driver.
    """
    base_url = 'postgresql://user:pass@localhost/dbname'
    test_db = 'test_abc123'
    result = get_test_db_url(base_url, test_db)
    assert result.startswith('postgresql+asyncpg://user:pass@localhost')
    assert test_db in result


@patch('app.utils.db.psycopg2.connect')
def test_create_test_database(mock_connect):
    """
    Mocks psycopg2 to verify that the create_test_database function
    connects to the database, creates a new test database, and closes the connection.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    create_test_database('postgresql://user:pass@localhost/dbname', 'test_xyz')

    mock_connect.assert_called_once()
    mock_cursor.execute.assert_called_once_with('CREATE DATABASE "test_xyz"')
    mock_conn.close.assert_called_once()


@patch('app.utils.db.psycopg2.connect')
def test_drop_test_database(mock_connect):
    """
    Verifies that drop_test_database properly connects, terminates active connections,
    drops the test database, and closes the connection.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    drop_test_database('postgresql://user:pass@localhost/dbname', 'test_xyz')

    actual_calls = mock_cursor.execute.call_args_list
    assert len(actual_calls) == 2
    assert actual_calls[0][0][0].strip().startswith('SELECT pg_terminate_backend')
    assert actual_calls[1][0][0] == 'DROP DATABASE IF EXISTS "test_xyz"'

    mock_conn.close.assert_called_once()
