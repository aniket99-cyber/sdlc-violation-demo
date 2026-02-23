import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.payment_service import (
    process_payment, calculate_discount, get_payment_history,
    validate_card, refund_payment, PaymentProcessor
)


# ─── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def payment_processor():
    """Return a PaymentProcessor instance."""
    return PaymentProcessor()


@pytest.fixture
def mock_requests():
    """Mock requests library."""
    with patch('src.payment_service.requests') as mock_req:
        mock_req.post.return_value.json.return_value = {"status": "success", "id": "pay_123"}
        yield mock_req


# ─── process_payment Tests ─────────────────────────────────────────────────

class TestProcessPayment:
    def test_process_payment_returns_response(self, mock_requests):
        """Should return payment response from gateway."""
        result = process_payment("user_1", 100.0, "4111111111111111", "123", "12/25")
        assert result is not None
        assert result["status"] == "success"

    def test_process_payment_calls_gateway(self, mock_requests):
        """Should call the payment gateway URL."""
        process_payment("user_1", 100.0, "4111111111111111", "123", "12/25")
        assert mock_requests.post.called

    def test_process_payment_exposes_stripe_key(self, mock_requests):
        """Demonstrates hardcoded Stripe key vulnerability."""
        from src.payment_service import STRIPE_SECRET_KEY
        assert STRIPE_SECRET_KEY.startswith("sk_live_")

    def test_process_payment_uses_http(self, mock_requests):
        """Demonstrates insecure HTTP usage for payment."""
        process_payment("user_1", 50.0, "4111111111111111", "123", "12/25")
        call_args = mock_requests.post.call_args
        url = call_args[0][0]
        assert url.startswith("http://")  # Violation: should be https://

    def test_process_payment_zero_amount(self, mock_requests):
        """Should handle zero amount payment."""
        result = process_payment("user_1", 0, "4111111111111111", "123", "12/25")
        assert result is not None

    def test_process_payment_negative_amount(self, mock_requests):
        """Should handle negative amount (no validation in place - violation)."""
        result = process_payment("user_1", -100, "4111111111111111", "123", "12/25")
        assert result is not None  # No validation = violation


# ─── calculate_discount Tests ──────────────────────────────────────────────

class TestCalculateDiscount:
    def test_premium_user_with_gold_membership_save20(self):
        """Premium gold user with SAVE20 and 15 purchases in US."""
        result = calculate_discount(
            "premium", 150, "SAVE20", "gold",
            ["p"] * 15, "US"
        )
        assert isinstance(result, float)

    def test_standard_user_save10_promo(self):
        """Standard user with SAVE10 promo."""
        result = calculate_discount("standard", 100, "SAVE10", "bronze", [], "US")
        assert isinstance(result, float)

    def test_unknown_user_type_no_discount(self):
        """Unknown user type should get no discount."""
        result = calculate_discount("unknown", 100, "SAVE20", "gold", [], "US")
        assert isinstance(result, float)

    def test_zero_amount(self):
        """Should handle zero amount."""
        result = calculate_discount("premium", 0, "SAVE20", "gold", [], "US")
        assert isinstance(result, float)

    def test_no_promo_code(self):
        """Should work without promo code."""
        result = calculate_discount("premium", 200, "", "silver", ["p"] * 3, "UK")
        assert isinstance(result, float)


# ─── validate_card Tests ───────────────────────────────────────────────────

class TestValidateCard:
    def test_valid_card_number(self):
        """Should return True for valid 16-digit card."""
        result = validate_card("4111111111111111", "123", "12/25")
        assert result is True

    def test_invalid_card_length(self):
        """Should return False for card with wrong length."""
        result = validate_card("411111", "123", "12/25")
        assert result is False

    def test_invalid_cvv_length(self):
        """Should return False for CVV with wrong length."""
        result = validate_card("4111111111111111", "12", "12/25")
        assert result is False

    def test_valid_cvv(self):
        """Should return True for valid 3-digit CVV."""
        result = validate_card("4111111111111111", "456", "12/25")
        assert result is True

    def test_empty_card_number(self):
        """Should handle empty card number."""
        result = validate_card("", "123", "12/25")
        assert result is False


# ─── PaymentProcessor Tests ────────────────────────────────────────────────

class TestPaymentProcessor:
    def test_processor_has_hardcoded_api_key(self, payment_processor):
        """Demonstrates hardcoded API key violation."""
        assert payment_processor.API_KEY == "live_payment_key_never_share_this"

    def test_processor_has_hardcoded_webhook_secret(self, payment_processor):
        """Demonstrates hardcoded webhook secret violation."""
        assert payment_processor.WEBHOOK_SECRET == "whsec_hardcoded_webhook_secret"

    def test_batch_process_empty_payments(self, payment_processor):
        """Should return empty list for empty payments."""
        result = payment_processor.batch_process_payments([])
        assert result == []

    def test_batch_process_single_payment(self, payment_processor):
        """Should process a single payment."""
        result = payment_processor.batch_process_payments([{"id": "pay_1", "amount": 100}])
        assert isinstance(result, list)
        assert len(result) > 0

    def test_generate_invoice_returns_float(self, payment_processor):
        """Should return a float total."""
        items = [{"price": 10.0}, {"price": 20.0}, {"price": 30.0}]
        result = payment_processor.generate_invoice("user_1", items, 0.18, 0.05, 9.99)
        assert isinstance(result, float)

    def test_generate_invoice_empty_items(self, payment_processor):
        """Should handle empty items list."""
        result = payment_processor.generate_invoice("user_1", [], 0.18, 0.05, 9.99)
        assert isinstance(result, float)


# ─── refund_payment Tests ──────────────────────────────────────────────────

class TestRefundPayment:
    def test_refund_calls_gateway(self):
        """Should call the refund gateway."""
        with patch('src.payment_service.requests') as mock_req:
            mock_req.post.return_value.json.return_value = {"status": "refunded"}
            result = refund_payment("pay_123", 50.0, "duplicate")
            assert mock_req.post.called

    def test_refund_uses_http(self):
        """Demonstrates HTTP violation in refund."""
        with patch('src.payment_service.requests') as mock_req:
            mock_req.post.return_value.json.return_value = {"status": "refunded"}
            refund_payment("pay_123", 50.0, "error")
            url = mock_req.post.call_args[0][0]
            assert url.startswith("http://")

    def test_refund_returns_response(self):
        """Should return response from gateway."""
        with patch('src.payment_service.requests') as mock_req:
            mock_req.post.return_value.json.return_value = {"status": "refunded", "id": "ref_123"}
            result = refund_payment("pay_123", 50.0, "customer_request")
            assert result["status"] == "refunded"
