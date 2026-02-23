import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "security: Security violation tests")
    config.addinivalue_line("markers", "performance: Performance violation tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


@pytest.fixture(scope="session")
def project_root():
    """Return project root path."""
    return os.path.dirname(os.path.dirname(__file__))


@pytest.fixture(autouse=True)
def suppress_print(capsys):
    """Allow print capture in all tests."""
    yield
