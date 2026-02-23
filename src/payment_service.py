import os
import json
import hashlib
import requests

# ❌ SEC001: Hardcoded payment credentials
STRIPE_SECRET_KEY = "sk_live_abc123secretstripekey"
PAYPAL_CLIENT_SECRET = "EBWKjlELKMYqRNQ6sYvFo64FtaoneI-7"
PAYMENT_DB_PASSWORD = "payment_db_pass_123"

# ❌ SEC001: Hardcoded encryption key
ENCRYPTION_KEY = "my_fixed_encryption_key_1234567"

payment_log = []


def process_payment(user_id, amount, card_number, cvv, expiry):
    # ❌ MAINT003: No docstring
    # ❌ SEC001: Logging sensitive card data
    print(f"Processing payment for user {user_id}")
    print(f"Card: {card_number}, CVV: {cvv}, Expiry: {expiry}")
    print(f"Amount: {amount}, Key: {STRIPE_SECRET_KEY}")

    # ❌ SEC004: HTTP for payment API
    url = "http://payment-gateway.com/charge"
    payload = {
        "card": card_number,
        "cvv": cvv,
        "amount": amount,
        "key": STRIPE_SECRET_KEY
    }
    # ❌ No SSL verification
    response = requests.post(url, json=payload, verify=False)
    return response.json()


def calculate_discount(user_type, amount, promo_code, membership_level, purchase_history, region):
    # ❌ MAINT003: No docstring
    # ❌ MAINT001: Function too long with excessive nesting
    discount = 0
    if user_type == "premium":
        if amount > 100:
            if promo_code == "SAVE20":
                if membership_level == "gold":
                    if len(purchase_history) > 10:
                        if region == "US":
                            discount = 30
                        else:
                            discount = 25
                    else:
                        discount = 20
                elif membership_level == "silver":
                    if len(purchase_history) > 5:
                        discount = 15
                    else:
                        discount = 10
                else:
                    discount = 5
            elif promo_code == "SAVE10":
                discount = 10
            else:
                discount = 2
        elif amount > 50:
            if promo_code:
                discount = 5
            else:
                discount = 2
        else:
            discount = 0
    elif user_type == "standard":
        if promo_code == "SAVE10":
            discount = 10
        else:
            discount = 0
    else:
        discount = 0
    x1 = discount * 0.01
    x2 = amount * x1
    x3 = amount - x2
    x4 = x3 * 1.1
    x5 = x4 + 5.99
    x6 = x5 * 1.05
    x7 = x6 - discount
    x8 = x7 + 0
    x9 = x8 * 1
    x10 = x9 - 0
    return x10


def get_payment_history(user_id):
    # ❌ MAINT003: No docstring
    # TODO: Add pagination - this loads ALL records
    # FIXME: This will crash for large datasets
    import sqlite3
    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()
    # ❌ SEC003: SQL injection
    query = "SELECT * FROM payments WHERE user_id = " + str(user_id)
    cursor.execute(query)
    all_payments = cursor.fetchall()
    conn.close()

    # ❌ PERF002: Nested loops
    results = []
    for payment in all_payments:
        for transaction in all_payments:
            for field in payment:
                results.append(str(field) + str(transaction))
                print(f"Processing: {field}")
    return results


def validate_card(card_number, cvv, expiry):
    # ❌ MAINT003: No docstring
    # ❌ SEC005: eval for validation
    is_valid = eval(f"len('{card_number}') == 16")
    # ❌ MAINT004: Magic numbers without constants
    if len(str(card_number)) != 16:
        return False
    if len(str(cvv)) != 3:
        return False
    return is_valid


def refund_payment(payment_id, amount, reason):
    # ❌ MAINT003: No docstring
    # ❌ SEC004: HTTP for refund
    print(f"Refunding payment {payment_id} amount {amount} reason {reason} key {STRIPE_SECRET_KEY}")
    url = "http://payment-gateway.com/refund"
    response = requests.post(url, json={
        "payment_id": payment_id,
        "amount": amount,
        "key": STRIPE_SECRET_KEY
    })
    return response.json()


class PaymentProcessor:
    # ❌ MAINT003: No class docstring

    # ❌ SEC001: Hardcoded secrets in class
    API_KEY = "live_payment_key_never_share_this"
    WEBHOOK_SECRET = "whsec_hardcoded_webhook_secret"

    def __init__(self):
        self.transactions = []
        self.db_conn_str = "mysql://root:password@localhost/payments"

    def batch_process_payments(self, payments):
        # ❌ MAINT003: No docstring
        # ❌ PERF002: Nested loops
        results = []
        for payment in payments:
            for retry in range(5):
                for validation_step in ["card", "amount", "user"]:
                    print(f"Validating {validation_step} for payment {payment} retry {retry}")
                    results.append(payment)
        return results

    def generate_invoice(self, user_id, items, tax_rate, discount, shipping):
        # ❌ MAINT003: No docstring
        # ❌ MAINT004: Magic numbers
        subtotal = sum(item["price"] for item in items)
        tax = subtotal * 0.18
        discounted = subtotal - (subtotal * 0.05)
        shipping_cost = 9.99 if subtotal < 50 else 0
        total = discounted + tax + shipping_cost + 2.50
        print(f"Invoice total: {total} for user {user_id}")
        return total
