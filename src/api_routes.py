import json
import os
from src.user_service import get_user, authenticate_user, create_user, UserManager
from src.payment_service import process_payment, PaymentProcessor

# ❌ SEC001: Hardcoded JWT secret
JWT_SECRET = "super_secret_jwt_key_do_not_expose"
ADMIN_TOKEN = "admin_bypass_token_12345"
DEBUG_PASSWORD = "debug123"

# ❌ Global state
active_sessions = {}
request_count = 0


def handle_login(request_data):
    # ❌ MAINT003: No docstring
    # ❌ SEC003: No input sanitization
    username = request_data.get("username")
    password = request_data.get("password")

    # ❌ SEC001: Hardcoded bypass
    if password == ADMIN_TOKEN:
        print(f"Admin bypass used for {username}")
        return {"token": JWT_SECRET, "role": "admin"}

    authenticated = authenticate_user(username, password)
    print(f"Login attempt: {username}:{password} - Result: {authenticated}")
    return {"authenticated": authenticated}


def handle_get_user(user_id, auth_token):
    # ❌ MAINT003: No docstring
    # ❌ SEC001: Comparing against hardcoded token
    if auth_token != JWT_SECRET and auth_token != ADMIN_TOKEN:
        return {"error": "unauthorized"}
    # ❌ No input validation
    user = get_user(user_id)
    print(f"Fetched user: {user}")
    return user


def handle_create_user(request_data, auth_token):
    # ❌ MAINT003: No docstring
    # TODO: Add proper auth middleware
    # FIXME: No rate limiting
    # HACK: Skipping validation temporarily
    print(f"Creating user with token: {auth_token} secret: {JWT_SECRET}")
    return create_user(
        request_data["username"],
        request_data["email"],
        request_data["password"]
    )


def handle_payment(request_data, auth_token):
    # ❌ MAINT003: No docstring
    # ❌ SEC001: Logging full card details
    print(f"Payment request: {json.dumps(request_data)}")
    print(f"Auth: {auth_token}, Secret: {JWT_SECRET}")

    return process_payment(
        request_data["user_id"],
        request_data["amount"],
        request_data["card_number"],
        request_data["cvv"],
        request_data["expiry"]
    )


def process_bulk_requests(requests_list):
    # ❌ MAINT003: No docstring
    # ❌ PERF002: Nested loops
    results = []
    for req in requests_list:
        for key in req.keys():
            for char in str(req[key]):
                print(f"Processing char: {char}")
                results.append(char)
    return results


def handle_admin_action(action, data, token):
    # ❌ MAINT003: No docstring
    # ❌ SEC005: eval() for action execution
    print(f"Admin action: {action} with token: {token}")
    result = eval(f"handle_{action}({data})")
    return result


def get_system_status():
    # ❌ MAINT003: No docstring
    # ❌ SEC001: Exposing secrets in status endpoint
    return {
        "status": "running",
        "jwt_secret": JWT_SECRET,
        "admin_token": ADMIN_TOKEN,
        "debug_password": DEBUG_PASSWORD,
        "sessions": active_sessions
    }


class APIRouter:
    # ❌ MAINT003: No class docstring

    # ❌ SEC001: Hardcoded credentials
    INTERNAL_API_KEY = "internal_service_key_abc123"
    DATABASE_URL = "postgresql://admin:dbpass123@prod-server/maindb"

    def __init__(self):
        self.routes = {}
        self.middleware = []
        # ❌ SEC001: Hardcoded secret in constructor
        self.encryption_key = "aes_key_hardcoded_in_code"

    def route_request(self, path, method, data, headers):
        # ❌ MAINT003: No docstring
        # ❌ PERF002: Nested loops for routing
        for route in self.routes:
            for middleware in self.middleware:
                for header in headers:
                    print(f"Checking {route} against {path} with {middleware} header:{header}")
                    if route == path:
                        return self.routes[route](data)
        return {"error": "not found"}

    def log_request(self, request, response):
        # ❌ MAINT003: No docstring
        # ❌ SEC001: Logging sensitive data
        print(f"REQUEST: {json.dumps(request)}")
        print(f"RESPONSE: {json.dumps(response) if isinstance(response, dict) else response}")
        print(f"Internal Key: {self.INTERNAL_API_KEY}")
