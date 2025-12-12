"""Common test fixtures for Jarolift tests."""

import pytest


@pytest.fixture
def mock_remote_entity():
    """Mock a remote entity."""
    return "remote.test_remote"


@pytest.fixture
def mock_jarolift_config():
    """Mock Jarolift configuration."""
    return {
        "remote_entity_id": "remote.test_remote",
        "MSB": "0x12345678",
        "LSB": "0x87654321",
        "delay": 0,
    }


@pytest.fixture
def mock_cover_config():
    """Mock cover configuration."""
    return {
        "name": "Test Cover",
        "group": "0x0001",
        "serial": "0x106aa01",
        "repeat_count": 0,
        "repeat_delay": 0.2,
        "reverse": False,
    }


@pytest.fixture
def mock_yaml_config(mock_jarolift_config):
    """Mock YAML configuration."""
    return {
        "jarolift": mock_jarolift_config,
    }
