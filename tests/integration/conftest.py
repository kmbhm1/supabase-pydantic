"""Configuration and fixtures for integration tests."""

import pytest


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "singular_names: mark test as related to singular names functionality"
    )


@pytest.fixture
def integration_test_marker():
    """Marker to identify integration tests."""
    return pytest.mark.integration


@pytest.fixture
def singular_names_marker():
    """Marker to identify singular names tests."""
    return pytest.mark.singular_names
