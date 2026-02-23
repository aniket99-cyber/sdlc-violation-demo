import pytest
import sqlite3
import os
from unittest.mock import patch, MagicMock, call
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.user_service import (
    get_user, authenticate_user, create_user,
    delete_user, get_all_users_with_orders,
    validate_user_input, get_user_report, UserManager
)


# ─── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def test_db(tmp_path):
    """Create a temporary test database."""
    db_path = str(tmp_path / "users.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            password TEXT,
            role TEXT,
            balance REAL
        )
    """)
    cursor.execute("INSERT INTO users VALUES (1, 'john_doe', 'john@test.com', 'pass123', 'user', 150.0)")
    cursor.execute("INSERT INTO users VALUES (2, 'jane_doe', 'jane@test.com', 'pass456', 'admin', 5500.0)")
    cursor.execute("INSERT INTO users VALUES (3, 'bob', 'bob@test.com', 'bob_pass', 'user', 9.99)")
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def user_manager():
    """Return a UserManager instance."""
    return UserManager()


# ─── get_user Tests ────────────────────────────────────────────────────────

class TestGetUser:
    def test_get_user_returns_none_for_nonexistent_user(self, test_db):
        """Should return None when user does not exist."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_conn.return_value.cursor.return_value = mock_cursor
            result = get_user("999")
            assert result is None

    def test_get_user_executes_query(self, test_db):
        """Should execute a SELECT query with the given user_id."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1, 'john_doe', 'john@test.com', 'pass123', 'user')
            mock_conn.return_value.cursor.return_value = mock_cursor
            result = get_user("1")
            assert result is not None
            assert result[1] == 'john_doe'

    def test_get_user_closes_connection(self):
        """Should always close the DB connection."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_conn.return_value.cursor.return_value = mock_cursor
            get_user("1")
            mock_conn.return_value.close.assert_called_once()


# ─── authenticate_user Tests ───────────────────────────────────────────────

class TestAuthenticateUser:
    def test_admin_bypass_with_hardcoded_password(self):
        """Demonstrates the hardcoded admin password vulnerability."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_conn.return_value.cursor.return_value = mock_cursor
            # This passes due to hardcoded password - a security violation
            result = authenticate_user("any_user", "supersecret123")
            assert result is True

    def test_authenticate_valid_user(self):
        """Should return True for valid credentials."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1, 'john', 'john@test.com', 'pass', 'user')
            mock_conn.return_value.cursor.return_value = mock_cursor
            result = authenticate_user("john", "pass")
            assert result is True

    def test_authenticate_invalid_user(self):
        """Should return False for invalid credentials."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_conn.return_value.cursor.return_value = mock_cursor
            result = authenticate_user("wrong", "wrong")
            assert result is False

    def test_authenticate_empty_credentials(self):
        """Should handle empty username and password."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_conn.return_value.cursor.return_value = mock_cursor
            result = authenticate_user("", "")
            assert result is False


# ─── create_user Tests ────────────────────────────────────────────────────

class TestCreateUser:
    def test_create_user_returns_true_on_success(self):
        """Should return True when user is created successfully."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            result = create_user("new_user", "new@test.com", "password123")
            assert result is True

    def test_create_user_with_default_role(self):
        """Should default role to 'user' when not specified."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            result = create_user("new_user", "new@test.com", "pass")
            assert result is True

    def test_create_user_with_admin_role(self):
        """Should allow creating user with admin role."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            result = create_user("admin_user", "admin@test.com", "pass", "admin")
            assert result is True

    def test_create_user_commits_transaction(self):
        """Should commit the transaction after creation."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            create_user("test", "test@test.com", "pass")
            mock_conn.return_value.commit.assert_called_once()


# ─── delete_user Tests ─────────────────────────────────────────────────────

class TestDeleteUser:
    def test_delete_user_executes_delete_query(self):
        """Should execute a DELETE query."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            delete_user(1)
            assert mock_cursor.execute.called

    def test_delete_user_commits(self):
        """Should commit after deletion."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            delete_user(1)
            mock_conn.return_value.commit.assert_called_once()

    def test_delete_nonexistent_user(self):
        """Should not raise error when deleting non-existent user."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            try:
                delete_user(99999)
            except Exception as e:
                pytest.fail(f"delete_user raised an exception: {e}")


# ─── validate_user_input Tests ─────────────────────────────────────────────

class TestValidateUserInput:
    def test_validate_simple_expression(self):
        """Should evaluate simple expressions (demonstrates eval vulnerability)."""
        result = validate_user_input("1 + 1")
        assert result == 2

    def test_validate_string_input(self):
        """Should evaluate string expressions."""
        result = validate_user_input("'hello'")
        assert result == "hello"


# ─── UserManager Tests ─────────────────────────────────────────────────────

class TestUserManager:
    def test_user_manager_initializes_with_hardcoded_secret(self, user_manager):
        """Demonstrates hardcoded secret in constructor violation."""
        assert user_manager.secret_key == "hardcoded_jwt_secret_do_not_share"

    def test_user_manager_has_hardcoded_db_url(self, user_manager):
        """Demonstrates hardcoded DB URL violation."""
        assert "password123" in user_manager.db_url

    def test_bulk_process_returns_results(self, user_manager):
        """Should return results for given user IDs."""
        with patch('src.user_service.get_user') as mock_get:
            mock_get.return_value = (1, "john", "john@test.com", "pass", "user")
            results = user_manager.bulk_process(["1", "2"])
            assert isinstance(results, list)

    def test_bulk_process_empty_list(self, user_manager):
        """Should return empty list for empty input."""
        results = user_manager.bulk_process([])
        assert results == []

    def test_export_users_returns_list(self, user_manager):
        """Should return list of users."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [(1, "john", "john@test.com", "pass", "user")]
            mock_conn.return_value.cursor.return_value = mock_cursor
            result = user_manager.export_users()
            assert isinstance(result, list)
