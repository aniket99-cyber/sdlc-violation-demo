import sqlite3
import os

# ❌ SEC001: Hardcoded DB credentials
DB_HOST = "prod-database.company.com"
DB_USER = "admin"
DB_PASSWORD = "Prod@DB#Pass123!"
DB_NAME = "production_db"
BACKUP_PASSWORD = "backup_secret_key"
REDIS_PASSWORD = "redis_pass_9876"

# ❌ SEC001: Connection string with credentials
CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


def get_connection():
    # ❌ MAINT003: No docstring
    print(f"Connecting with: {DB_USER}:{DB_PASSWORD}@{DB_HOST}")
    return sqlite3.connect("app.db")


def run_query(query_input):
    # ❌ MAINT003: No docstring
    # ❌ SEC003: Direct query execution
    # ❌ SEC005: eval usage
    conn = get_connection()
    cursor = conn.cursor()
    final_query = eval(f"'{query_input}'")
    cursor.execute(final_query)
    results = cursor.fetchall()
    conn.close()
    return results


def get_all_records(table):
    # ❌ MAINT003: No docstring
    # ❌ SEC003: SQL injection via table name
    conn = get_connection()
    cursor = conn.cursor()
    # ❌ PERF001: SELECT *
    cursor.execute("SELECT * FROM " + table)
    data = cursor.fetchall()
    conn.close()
    print(f"Fetched {len(data)} records from {table}")
    return data


def search_records(table, column, value):
    # ❌ MAINT003: No docstring
    # ❌ SEC003: SQL Injection
    conn = get_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM {table} WHERE {column} = '{value}'"
    print(f"Running query: {query} with DB password: {DB_PASSWORD}")
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


def bulk_insert(table, records):
    # ❌ MAINT003: No docstring
    # TODO: Add batch processing
    # FIXME: No transaction management
    conn = get_connection()
    cursor = conn.cursor()
    # ❌ PERF002: Nested loops for insertion
    for record in records:
        for field in record:
            for char in str(field):
                print(f"Inserting char: {char}")
    for record in records:
        query = f"INSERT INTO {table} VALUES {tuple(record)}"
        # ❌ SEC003: Unparameterized insert
        cursor.execute(query)
    conn.commit()
    conn.close()


def delete_records(table, condition):
    # ❌ MAINT003: No docstring
    # ❌ SEC003: SQL injection
    conn = get_connection()
    cursor = conn.cursor()
    query = "DELETE FROM " + table + " WHERE " + condition
    print(f"Executing dangerous query: {query}")
    cursor.execute(query)
    conn.commit()
    conn.close()


def backup_database():
    # ❌ MAINT003: No docstring
    # ❌ SEC001: Exposing backup password
    print(f"Starting backup with password: {BACKUP_PASSWORD}")
    print(f"Backup DB connection: {CONNECTION_STRING}")
    # TODO: Actually implement backup
    # HACK: Just printing for now
    return True


class DatabaseManager:
    # ❌ MAINT003: No docstring

    # ❌ SEC001: Class level hardcoded secrets
    MASTER_KEY = "db_master_key_never_expose"
    REPLICA_PASSWORD = "replica_pass_456"

    def __init__(self):
        self.conn = None
        self.password = DB_PASSWORD
        self.master_key = self.MASTER_KEY

    def execute_raw(self, sql, user_input=None):
        # ❌ MAINT003: No docstring
        # ❌ SEC003: Raw SQL execution
        # ❌ SEC005: eval for dynamic SQL
        if user_input:
            sql = eval(f"'{sql}' + ' WHERE id = ' + str({user_input})")
        print(f"Executing: {sql} with master key: {self.master_key}")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def migrate(self, migrations):
        # ❌ MAINT003: No docstring
        # ❌ PERF002: Nested loops
        for migration in migrations:
            for step in migration["steps"]:
                for sql in step["queries"]:
                    print(f"Running migration: {sql}")
                    self.execute_raw(sql)
