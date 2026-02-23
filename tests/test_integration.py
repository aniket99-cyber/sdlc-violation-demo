import pytest
import sqlite3
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.user_service import create_user, get_user, authenticate_user, delete_user, UserManager
from src.payment_service import process_payment, validate_card, PaymentProcessor
from src.api_routes import handle_login, handle_get_user, handle_create_user, handle_payment, APIRouter
from src.notification_service import NotificationService


# ─── Integration: User + Auth Flow ─────────────────────────────────────────

class TestUserAuthFlow:
    """Integration tests for full user authentication flow."""

    def test_create_and_authenticate_user(self):
        """Should create user and authenticate successfully."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1, "int_user", "int@test.com", "pass123", "user")
            mock_conn.return_value.cursor.return_value = mock_cursor

            create_result = create_user("int_user", "int@test.com", "pass123")
            assert create_result is True

            auth_result = authenticate_user("int_user", "pass123")
            assert auth_result is True

    def test_login_and_get_user_flow(self):
        """Should login and retrieve user data."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (1, "test_user", "test@test.com", "pass", "user")
            mock_conn.return_value.cursor.return_value = mock_cursor

            from src.api_routes import JWT_SECRET
            login_result = handle_login({"username": "test_user", "password": "pass"})
            assert "authenticated" in login_result

            user_result = handle_get_user("1", JWT_SECRET)
            assert user_result is not None

    def test_create_user_via_api(self):
        """Should create user through API handler."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor

            from src.api_routes import JWT_SECRET
            result = handle_create_user({
                "username": "new_api_user",
                "email": "api@test.com",
                "password": "apipass123"
            }, JWT_SECRET)
            assert result is True

    def test_unauthorized_access_returns_error(self):
        """Should reject requests with invalid token."""
        result = handle_get_user("1", "invalid_token_xyz")
        assert "error" in result
        assert result["error"] == "unauthorized"

    def test_admin_bypass_vulnerability(self):
        """Demonstrates admin bypass token vulnerability."""
        from src.api_routes import ADMIN_TOKEN
        result = handle_login({"username": "any_user", "password": ADMIN_TOKEN})
        assert "token" in result
        assert result["role"] == "admin"


# ─── Integration: Payment Flow ─────────────────────────────────────────────

class TestPaymentFlow:
    """Integration tests for full payment processing flow."""

    def test_validate_and_process_payment(self):
        """Should validate card then process payment."""
        with patch('src.payment_service.requests') as mock_req:
            mock_req.post.return_value.json.return_value = {"status": "success", "id": "pay_123"}

            card_valid = validate_card("4111111111111111", "123", "12/25")
            assert card_valid is True

            result = process_payment("user_1", 100.0, "4111111111111111", "123", "12/25")
            assert result["status"] == "success"

    def test_payment_via_api_handler(self):
        """Should process payment through API handler."""
        with patch('src.payment_service.requests') as mock_req:
            mock_req.post.return_value.json.return_value = {"status": "success"}

            from src.api_routes import JWT_SECRET
            result = handle_payment({
                "user_id": "user_1",
                "amount": 150.0,
                "card_number": "4111111111111111",
                "cvv": "123",
                "expiry": "12/25"
            }, JWT_SECRET)
            assert result["status"] == "success"

    def test_invalid_card_blocks_payment(self):
        """Should fail validation for invalid card."""
        card_valid = validate_card("123", "12", "12/25")
        assert card_valid is False

    def test_batch_payment_processing(self):
        """Should process multiple payments in batch."""
        processor = PaymentProcessor()
        payments = [
            {"id": "pay_1", "amount": 50.0, "user": "user_1"},
            {"id": "pay_2", "amount": 75.0, "user": "user_2"},
            {"id": "pay_3", "amount": 25.0, "user": "user_3"},
        ]
        results = processor.batch_process_payments(payments)
        assert isinstance(results, list)
        assert len(results) > 0


# ─── Integration: API Router ───────────────────────────────────────────────

class TestAPIRouterIntegration:
    """Integration tests for API routing."""

    def test_router_initialization(self):
        """Should initialize with hardcoded credentials (violation)."""
        router = APIRouter()
        assert router.INTERNAL_API_KEY == "internal_service_key_abc123"
        assert "password" in router.DATABASE_URL

    def test_system_status_exposes_secrets(self):
        """Demonstrates system status endpoint exposing secrets."""
        from src.api_routes import get_system_status, JWT_SECRET, ADMIN_TOKEN
        status = get_system_status()
        assert "jwt_secret" in status
        assert status["jwt_secret"] == JWT_SECRET
        assert status["admin_token"] == ADMIN_TOKEN

    def test_router_handles_unknown_path(self):
        """Should return error for unknown routes."""
        router = APIRouter()
        router.routes = {}
        result = router.route_request("/unknown", "GET", {}, {})
        assert "error" in result


# ─── Integration: User + Notification Flow ─────────────────────────────────

class TestUserNotificationFlow:
    """Integration tests for user + notification flow."""

    def test_create_user_and_send_notification(self):
        """Should create user and send welcome notification."""
        with patch('sqlite3.connect') as mock_db:
            mock_cursor = MagicMock()
            mock_db.return_value.cursor.return_value = mock_cursor

            with patch('src.notification_service.smtplib.SMTP') as mock_smtp:
                mock_smtp_instance = MagicMock()
                mock_smtp.return_value = mock_smtp_instance

                user_created = create_user("notify_user", "notify@test.com", "pass123")
                assert user_created is True

                from src.notification_service import send_email
                email_sent = send_email("notify@test.com", "Welcome!", "Welcome to our platform!")
                assert email_sent is True

    def test_notification_service_hardcoded_credentials(self):
        """Demonstrates hardcoded credentials in notification service."""
        service = NotificationService()
        assert service.FIREBASE_KEY == "firebase_server_key_hardcoded"
        assert service.PUSH_SECRET == "push_notification_secret_123"

    def test_bulk_notification_to_multiple_users(self):
        """Should send notifications to multiple users."""
        service = NotificationService()
        with patch('src.notification_service.requests') as mock_req:
            mock_req.post.return_value.json.return_value = {"success": True}
            result = service.send_push_notification(
                ["token_1", "token_2"],
                "Test Title",
                "Test Body",
                {"key": "value"}
            )
            assert isinstance(result, list)


# ─── Integration: Full SDLC Violation Showcase ─────────────────────────────

class TestSDLCViolationShowcase:
    """Showcase tests that highlight all major SDLC violations."""

    def test_sec001_hardcoded_credentials_everywhere(self):
        """SEC001: Hardcoded credentials found across all modules."""
        from src.user_service import UserManager
        from src.payment_service import STRIPE_SECRET_KEY, PAYPAL_CLIENT_SECRET
        from src.api_routes import JWT_SECRET, ADMIN_TOKEN
        from src.database import DB_PASSWORD, CONNECTION_STRING
        from src.notification_service import SMTP_PASSWORD, TWILIO_TOKEN

        assert len(STRIPE_SECRET_KEY) > 0
        assert len(JWT_SECRET) > 0
        assert len(DB_PASSWORD) > 0
        assert len(SMTP_PASSWORD) > 0

    def test_sec003_sql_injection_vulnerability(self):
        """SEC003: SQL injection via string concatenation."""
        with patch('sqlite3.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_conn.return_value.cursor.return_value = mock_cursor

            # This would be injectable in real DB
            malicious_id = "1 OR 1=1"
            get_user(malicious_id)
            execute_call = mock_cursor.execute.call_args[0][0]
            assert malicious_id in execute_call

    def test_perf002_nested_loops_detected(self):
        """PERF002: Nested loops cause O(n³) complexity."""
        from src.user_service import process_user_permissions
        users = ["u1", "u2"]
        perms = ["read", "write"]
        roles = ["admin", "user"]
        result = process_user_permissions(users, perms, roles)
        # 2 * 2 * 2 = 8 combinations due to nested loops
        assert len(result) == 8

    def test_maint003_no_docstrings(self):
        """MAINT003: Functions missing docstrings."""
        import inspect
        from src.user_service import get_user, create_user, authenticate_user
        assert get_user.__doc__ is None
        assert create_user.__doc__ is None
        assert authenticate_user.__doc__ is None

    def test_sdlc002_config_hardcoded_secrets(self):
        """SDLC: Config file contains all secrets hardcoded."""
        from config.settings import (
            DATABASE_PASSWORD, JWT_SECRET_KEY,
            STRIPE_SECRET_KEY, AWS_ACCESS_KEY_ID
        )
        assert "Pass" in DATABASE_PASSWORD
        assert len(JWT_SECRET_KEY) > 10
        assert STRIPE_SECRET_KEY.startswith("sk_live_")
        assert AWS_ACCESS_KEY_ID.startswith("AKIA")
