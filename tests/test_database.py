import pytest
import sqlite3
import os
import sys
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import (
    get_connection, run_query, get_all_records,
    search_records, bulk_insert, delete_records,
    backup_database, DatabaseManager
)


# ─── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def db_manager():
    return DatabaseManager()


@pytest.fixture
def mock_db():
    with patch('src.database.sqlite3.connect') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        yield mock_conn, mock_cursor


# ─── get_connection Tests ──────────────────────────────────────────────────

class TestGetConnection:
    def test_returns_connection(self):
        """Should return a sqlite3 connection."""
        with patch('src.database.sqlite3.connect') as mock_conn:
            mock_conn.return_value = MagicMock()
            conn = get_connection()
            assert conn is not None

    def test_logs_credentials(self, capsys):
        """Demonstrates SEC001 - credentials printed to stdout."""
        with patch('src.database.sqlite3.connect') as mock_conn:
            mock_conn.return_value = MagicMock()
            get_connection()
            captured = capsys.readouterr()
            assert "admin" in captured.out
            assert "Prod@DB#Pass123!" in captured.out


# ─── run_query Tests ───────────────────────────────────────────────────────

class TestRunQuery:
    def test_run_simple_query(self, mock_db):
        """Should execute a query and return results."""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = [(1, "result")]
        result = run_query("SELECT 1")
        assert result == [(1, "result")]

    def test_run_query_uses_eval(self):
        """Demonstrates SEC005 - eval used inside run_query."""
        with patch('src.database.sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_conn.return_value.cursor.return_value = mock_cursor
            # eval is called on user input - critical vulnerability
            run_query("SELECT * FROM users")
            assert mock_cursor.execute.called

    def test_run_query_closes_connection(self, mock_db):
        """Should close connection after query."""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = []
        run_query("SELECT 1")
        mock_conn.return_value.close.assert_called_once()


# ─── get_all_records Tests ─────────────────────────────────────────────────

class TestGetAllRecords:
    def test_fetches_all_records(self, mock_db):
        """Should fetch all records from a table."""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = [(1, "row1"), (2, "row2")]
        result = get_all_records("users")
        assert len(result) == 2

    def test_uses_select_star(self, mock_db):
        """Demonstrates PERF001 - SELECT * used."""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = []
        get_all_records("users")
        query = mock_cursor.execute.call_args[0][0]
        assert "SELECT *" in query

    def test_sql_injection_via_table_name(self, mock_db):
        """Demonstrates SEC003 - table name is not sanitized."""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = []
        malicious_table = "users; DROP TABLE users;--"
        get_all_records(malicious_table)
        query = mock_cursor.execute.call_args[0][0]
        assert malicious_table in query

    def test_empty_table_returns_empty_list(self, mock_db):
        """Should return empty list for empty table."""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = []
        result = get_all_records("empty_table")
        assert result == []


# ─── search_records Tests ──────────────────────────────────────────────────

class TestSearchRecords:
    def test_search_returns_matching_records(self, mock_db):
        """Should return matching records."""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = [(1, "john", "john@test.com")]
        result = search_records("users", "username", "john")
        assert len(result) == 1

    def test_search_sql_injection_vulnerability(self, mock_db):
        """Demonstrates SEC003 - search value is not parameterized."""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = []
        malicious_value = "' OR '1'='1"
        search_records("users", "username", malicious_value)
        query = mock_cursor.execute.call_args[0][0]
        assert malicious_value in query

    def test_search_logs_db_password(self, mock_db, capsys):
        """Demonstrates SEC001 - DB password logged during search."""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = []
        search_records("users", "id", "1")
        captured = capsys.readouterr()
        assert "Prod@DB#Pass123!" in captured.out

    def test_search_no_results(self, mock_db):
        """Should return empty list when no records match."""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = []
        result = search_records("users", "username", "nonexistent")
        assert result == []


# ─── bulk_insert Tests ─────────────────────────────────────────────────────

class TestBulkInsert:
    def test_bulk_insert_commits(self, mock_db):
        """Should commit after all inserts."""
        mock_conn, mock_cursor = mock_db
        records = [(1, "user1", "user1@test.com"), (2, "user2", "user2@test.com")]
        bulk_insert("users", records)
        mock_conn.return_value.commit.assert_called_once()

    def test_bulk_insert_empty_records(self, mock_db):
        """Should handle empty records list gracefully."""
        mock_conn, mock_cursor = mock_db
        bulk_insert("users", [])
        mock_conn.return_value.commit.assert_called_once()

    def test_bulk_insert_uses_nested_loops(self, mock_db, capsys):
        """Demonstrates PERF002 - triple nested loop in bulk insert."""
        mock_conn, mock_cursor = mock_db
        records = [("john", "john@test.com", "pass")]
        bulk_insert("users", records)
        captured = capsys.readouterr()
        # The nested loop prints each character
        assert "Inserting char:" in captured.out


# ─── delete_records Tests ──────────────────────────────────────────────────

class TestDeleteRecords:
    def test_delete_executes_query(self, mock_db):
        """Should execute a DELETE query."""
        mock_conn, mock_cursor = mock_db
        delete_records("users", "id = 1")
        assert mock_cursor.execute.called

    def test_delete_sql_injection(self, mock_db):
        """Demonstrates SEC003 - condition is not sanitized."""
        mock_conn, mock_cursor = mock_db
        malicious = "1=1"
        delete_records("users", malicious)
        query = mock_cursor.execute.call_args[0][0]
        assert malicious in query

    def test_delete_commits(self, mock_db):
        """Should commit after delete."""
        mock_conn, mock_cursor = mock_db
        delete_records("users", "id = 1")
        mock_conn.return_value.commit.assert_called_once()


# ─── DatabaseManager Tests ─────────────────────────────────────────────────

class TestDatabaseManager:
    def test_has_hardcoded_master_key(self, db_manager):
        """Demonstrates SEC001 - hardcoded master key."""
        assert db_manager.MASTER_KEY == "db_master_key_never_expose"
        assert db_manager.master_key == "db_master_key_never_expose"

    def test_has_hardcoded_password(self, db_manager):
        """Demonstrates SEC001 - DB password stored in instance."""
        from src.database import DB_PASSWORD
        assert db_manager.password == DB_PASSWORD

    def test_execute_raw_runs_query(self, mock_db, db_manager):
        """Should execute raw SQL query."""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = [(1,)]
        result = db_manager.execute_raw("SELECT 1")
        assert result == [(1,)]

    def test_migrate_runs_all_steps(self, mock_db, db_manager):
        """Should run all migration queries."""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = []
        migrations = [{
            "steps": [
                {"queries": ["CREATE TABLE test (id INT)", "ALTER TABLE test ADD COLUMN name TEXT"]},
                {"queries": ["CREATE INDEX idx_test ON test(id)"]}
            ]
        }]
        db_manager.migrate(migrations)
        assert mock_cursor.execute.call_count == 3

    def test_migrate_empty(self, mock_db, db_manager):
        """Should handle empty migrations."""
        mock_conn, mock_cursor = mock_db
        db_manager.migrate([])
        assert mock_cursor.execute.call_count == 0
