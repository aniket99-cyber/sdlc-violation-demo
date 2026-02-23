# SDLC Violation Demo Project

A Python project intentionally containing **SDLC rule violations** for testing the AI Code Reviewer system.

## Project Structure

```
sdlc-violation-project/
├── src/
│   ├── user_service.py        # User management (12+ violations)
│   ├── payment_service.py     # Payment processing (10+ violations)
│   ├── api_routes.py          # API layer (8+ violations)
│   ├── database.py            # DB handler (10+ violations)
│   └── notification_service.py # Notifications (8+ violations)
├── config/
│   └── settings.py            # Config (20+ hardcoded secrets)
├── tests/
│   ├── test_user_service.py   # Unit tests - user service
│   ├── test_payment_service.py # Unit tests - payment service
│   ├── test_database.py       # Unit tests - database
│   ├── test_notification_service.py # Unit tests - notifications
│   └── test_integration.py    # Integration tests - full flows
├── pytest.ini
└── requirements.txt
```

## Violations Coverage

| Rule ID | Category | Description | Files |
|---------|----------|-------------|-------|
| SEC001 | Security | Hardcoded credentials | All files |
| SEC002 | Security | Hardcoded AWS credentials | settings.py |
| SEC003 | Security | SQL Injection | user_service, database |
| SEC004 | Security | HTTP instead of HTTPS | payment, notification |
| SEC005 | Security | eval() usage | user_service, database, notification |
| PERF001 | Performance | SELECT * queries | database, user_service |
| PERF002 | Performance | Nested loops (O(n²/n³)) | All files |
| MAINT001 | Maintainability | Functions too long (50+ lines) | user_service, payment |
| MAINT002 | Maintainability | TODO/FIXME/HACK comments | All files |
| MAINT003 | Maintainability | Missing docstrings | All files |
| MAINT004 | Maintainability | Magic numbers | payment, config |

## Setup & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest tests/test_user_service.py tests/test_payment_service.py tests/test_database.py tests/test_notification_service.py

# Run only integration tests
pytest tests/test_integration.py

# Run with verbose output
pytest -v
```

## Using with AI Code Reviewer

```bash
# Initialize git repo
git init
git add .
git commit -m "initial: add baseline code"

# Make a change to trigger diff
echo "# reviewed" >> src/user_service.py
git add .
git commit -m "feat: add review marker"
```

Then point the Code Reviewer UI at this project path.
