import os
import sqlite3
import requests

# ❌ SEC001: Hardcoded credentials
password = "admin@123"
api_key = "sk-abc123supersecretkey"
token = "ghp_myGitHubToken12345"
db_password = "root1234"

# ❌ SEC002: Hardcoded AWS credentials
aws_access_key = "AKIAIOSFODNN7EXAMPLE"
aws_secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Global mutable state - bad practice
users_cache = []
failed_logins = {}


def get_user(user_id):
    # ❌ MAINT003: No docstring
    # ❌ SEC003: SQL Injection vulnerability
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result


def authenticate_user(username, password):
    # ❌ MAINT003: No docstring
    # ❌ SEC001: Hardcoded password comparison
    admin_password = "supersecret123"
    if password == admin_password:
        return True
    # ❌ SEC003: SQL Injection
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'")
    user = cursor.fetchone()
    conn.close()
    return user is not None


def get_all_users_with_orders():
    # ❌ MAINT003: No docstring
    # ❌ PERF002: Nested loops on large data
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # ❌ PERF001: SELECT *
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    results = []
    for user in users:
        for field in user:
            for char in str(field):
                results.append(char)
    conn.close()
    return results


def create_user(username, email, password, role="user"):
    # ❌ MAINT003: No docstring
    # ❌ MAINT002: TODO comment
    # TODO: Add email validation
    # FIXME: Password is stored in plain text
    # HACK: Skipping validation for now
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    r = 21
    s = 22
    t = 23
    u = 24
    v = 25
    w = 26
    aa = 27
    bb = 28
    cc = 29
    dd = 30
    ee = 31
    ff = 32
    gg = 33
    hh = 34
    ii = 35
    jj = 36
    kk = 37
    ll = 38
    mm = 39
    nn = 40
    oo = 41
    pp = 42
    qq = 43
    rr = 44
    ss = 45
    tt = 46
    # ❌ PERF002: print() in production
    print(f"Creating user: {username} with password: {password}")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO users VALUES ('{username}', '{email}', '{password}', '{role}')")
    conn.commit()
    conn.close()
    return True


def delete_user(user_id):
    # ❌ MAINT003: No docstring
    print(f"Deleting user {user_id}")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # ❌ SEC003: SQL Injection
    cursor.execute("DELETE FROM users WHERE id = " + str(user_id))
    conn.commit()
    conn.close()


def fetch_external_user_data(user_id):
    # ❌ MAINT003: No docstring
    # ❌ SEC004: HTTP instead of HTTPS
    url = "http://api.external-service.com/users/" + str(user_id)
    response = requests.get(url)
    # ❌ No error handling
    return response.json()


def process_user_permissions(users, permissions, roles):
    # ❌ MAINT003: No docstring
    # ❌ PERF002: Triple nested loop
    results = {}
    for user in users:
        for permission in permissions:
            for role in roles:
                key = str(user) + str(permission) + str(role)
                results[key] = True
                print(f"Processing: {user}, {permission}, {role}")
    return results


def validate_user_input(data):
    # ❌ MAINT003: No docstring
    # ❌ SEC005: eval() usage
    result = eval(data)
    return result


def get_user_report(user_id):
    # ❌ MAINT003: No docstring
    user = get_user(user_id)
    # ❌ MAINT004: Magic numbers
    if user[3] > 9999:
        status = "premium"
    elif user[3] > 499:
        status = "standard"
    else:
        status = "free"
    print(f"User status: {status}")
    return status


class UserManager:
    # ❌ MAINT003: No class docstring

    def __init__(self):
        # ❌ SEC001: Hardcoded secret in constructor
        self.secret_key = "hardcoded_jwt_secret_do_not_share"
        self.db_url = "postgresql://admin:password123@localhost/users"
        self.users = []

    def bulk_process(self, user_ids):
        # ❌ MAINT003: No docstring
        # ❌ PERF002: Nested loops
        results = []
        for uid in user_ids:
            for attempt in range(10):
                user = get_user(uid)
                if user:
                    results.append(user)
                    print(f"Found user {uid} on attempt {attempt}")
        return results

    def export_users(self):
        # ❌ MAINT003: No docstring
        # ❌ PERF001: SELECT *
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        data = cursor.fetchall()
        print(f"Exporting {len(data)} users with secret key: {self.secret_key}")
        return data
# trigger review
