import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.notification_service import (
    send_email, send_bulk_notifications, send_sms,
    notify_admin, process_notification_templates,
    NotificationService
)


@pytest.fixture
def notification_service():
    return NotificationService()


@pytest.fixture
def mock_smtp():
    with patch('src.notification_service.smtplib.SMTP') as mock:
        mock.return_value.__enter__ = mock.return_value
        mock.return_value.__exit__ = MagicMock(return_value=False)
        yield mock


@pytest.fixture
def mock_requests():
    with patch('src.notification_service.requests') as mock:
        mock.post.return_value.json.return_value = {"status": "sent"}
        yield mock


# ─── send_email Tests ──────────────────────────────────────────────────────

class TestSendEmail:
    def test_send_email_success(self, mock_smtp):
        """Should return True on successful email send."""
        result = send_email("test@test.com", "Subject", "Body")
        assert result is True

    def test_send_email_failure_returns_false(self):
        """Should return False when SMTP raises exception."""
        with patch('src.notification_service.smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = Exception("Connection refused")
            result = send_email("test@test.com", "Subject", "Body")
            assert result is False

    def test_send_email_logs_credentials(self, mock_smtp, capsys):
        """Demonstrates SEC001 - SMTP credentials logged."""
        send_email("test@test.com", "Subject", "Body")
        captured = capsys.readouterr()
        assert "company_gmail_password_123" in captured.out

    def test_send_email_logs_user_password(self, mock_smtp, capsys):
        """Demonstrates SEC001 - user password logged in notification."""
        send_email("test@test.com", "Subject", "Body", user_password="userpass123")
        captured = capsys.readouterr()
        assert "userpass123" in captured.out

    def test_send_email_to_empty_address(self, mock_smtp):
        """Should attempt to send even with empty address."""
        result = send_email("", "Subject", "Body")
        assert result is True


# ─── send_sms Tests ────────────────────────────────────────────────────────

class TestSendSms:
    def test_send_sms_returns_response(self, mock_requests):
        """Should return response from SMS gateway."""
        result = send_sms("+1234567890", "Test message")
        assert result == {"status": "sent"}

    def test_send_sms_uses_http(self, mock_requests):
        """Demonstrates SEC004 - HTTP used for SMS API."""
        send_sms("+1234567890", "Test")
        url = mock_requests.post.call_args[0][0]
        assert url.startswith("http://")

    def test_send_sms_logs_token(self, mock_requests, capsys):
        """Demonstrates SEC001 - Twilio token logged."""
        send_sms("+1234567890", "Test")
        captured = capsys.readouterr()
        assert "hardcoded_twilio_auth_token" in captured.out

    def test_send_sms_calls_gateway(self, mock_requests):
        """Should call the SMS gateway."""
        send_sms("+1234567890", "Test")
        assert mock_requests.post.called


# ─── send_bulk_notifications Tests ─────────────────────────────────────────

class TestSendBulkNotifications:
    def test_bulk_notifications_returns_list(self):
        """Should return list of notification results."""
        result = send_bulk_notifications(
            ["user1", "user2"],
            "Test message",
            ["email", "sms"]
        )
        assert isinstance(result, list)

    def test_bulk_notifications_triple_nested_loop(self):
        """Demonstrates PERF002 - O(n³) nested loops."""
        users = ["u1", "u2"]
        types = ["email", "sms"]
        result = send_bulk_notifications(users, "msg", types)
        # 2 users × 2 types × 3 retries = 12 items
        assert len(result) == 12

    def test_bulk_notifications_empty_users(self):
        """Should return empty list for no users."""
        result = send_bulk_notifications([], "msg", ["email"])
        assert result == []

    def test_bulk_notifications_logs_api_key(self, capsys):
        """Demonstrates SEC001 - SendGrid key logged."""
        send_bulk_notifications(["user1"], "msg", ["email"])
        captured = capsys.readouterr()
        assert "SG.hardcoded_sendgrid_api_key" in captured.out


# ─── process_notification_templates Tests ──────────────────────────────────

class TestProcessNotificationTemplates:
    def test_processes_simple_template(self):
        """Should process a simple template."""
        result = process_notification_templates(
            ["Hello {name}"],
            ["user1"],
            {"name": "John"}
        )
        assert isinstance(result, list)
        assert len(result) > 0

    def test_uses_eval_for_processing(self):
        """Demonstrates SEC005 - eval used for template processing."""
        # eval is called inside process_notification_templates
        result = process_notification_templates(
            ["Template"],
            ["user1"],
            {"key": "value"}
        )
        assert isinstance(result, list)

    def test_empty_templates(self):
        """Should return empty list for no templates."""
        result = process_notification_templates([], ["user1"], {"key": "val"})
        assert result == []


# ─── NotificationService Tests ─────────────────────────────────────────────

class TestNotificationService:
    def test_has_hardcoded_firebase_key(self, notification_service):
        """Demonstrates SEC001 - Firebase key hardcoded."""
        assert notification_service.FIREBASE_KEY == "firebase_server_key_hardcoded"

    def test_has_hardcoded_push_secret(self, notification_service):
        """Demonstrates SEC001 - push secret hardcoded."""
        assert notification_service.PUSH_SECRET == "push_notification_secret_123"

    def test_send_push_uses_http(self, mock_requests, notification_service):
        """Demonstrates SEC004 - HTTP used for FCM."""
        notification_service.send_push_notification(
            ["token_1"], "Title", "Body", {"key": "val"}
        )
        url = mock_requests.post.call_args[0][0]
        assert url.startswith("http://")

    def test_send_push_triple_nested_loop(self, mock_requests, notification_service):
        """Demonstrates PERF002 - triple nested loop."""
        results = notification_service.send_push_notification(
            ["token_1", "token_2"],
            "Title", "Body",
            {"k1": "v1", "k2": "v2"}
        )
        # 2 tokens × 3 retries × 2 data keys = 12 calls
        assert len(results) == 12

    def test_send_push_logs_firebase_key(self, mock_requests, notification_service, capsys):
        """Demonstrates SEC001 - Firebase key logged in push notification."""
        notification_service.send_push_notification(
            ["token_1"], "Title", "Body", {"key": "val"}
        )
        captured = capsys.readouterr()
        assert "firebase_server_key_hardcoded" in captured.out

    def test_send_push_empty_tokens(self, mock_requests, notification_service):
        """Should return empty list for no tokens."""
        results = notification_service.send_push_notification([], "Title", "Body", {})
        assert results == []
