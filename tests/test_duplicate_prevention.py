"""Tests for duplicate entity prevention after YAML migration."""

from homeassistant import config_entries

from custom_components.jarolift import (
    CONF_DELAY,
    CONF_LSB,
    CONF_MSB,
    CONF_REMOTE_ENTITY_ID,
    DOMAIN,
    setup,
)
from custom_components.jarolift.cover import setup_platform


async def test_yaml_setup_skipped_when_config_entry_exists(hass, mock_remote_entity):
    """Test that YAML setup is skipped when a config entry already exists."""
    # Create a config entry first (simulating completed migration)
    entry = config_entries.ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Jarolift",
        data={
            CONF_REMOTE_ENTITY_ID: mock_remote_entity,
            CONF_MSB: "0x12345678",
            CONF_LSB: "0x87654321",
            CONF_DELAY: 0,
        },
        source=config_entries.SOURCE_IMPORT,
        unique_id=DOMAIN,
        options={},
    )
    entry.add_to_hass(hass)

    # Mock the remote entity
    hass.states.async_set(mock_remote_entity, "idle")

    # Try to set up via YAML (this should be skipped)
    yaml_config = {
        DOMAIN: {
            CONF_REMOTE_ENTITY_ID: mock_remote_entity,
            CONF_MSB: "0x12345678",
            CONF_LSB: "0x87654321",
            CONF_DELAY: 0,
        }
    }

    # Call setup with YAML config
    result = setup(hass, yaml_config)

    # Setup should return True but skip creating duplicate entities
    assert result is True

    # Verify that only one config entry exists
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1


async def test_cover_platform_skipped_when_config_entry_exists(
    hass, mock_remote_entity
):
    """Test that cover platform setup is skipped when a config entry exists."""
    # Create a config entry first
    entry = config_entries.ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Jarolift",
        data={
            CONF_REMOTE_ENTITY_ID: mock_remote_entity,
            CONF_MSB: "0x12345678",
            CONF_LSB: "0x87654321",
            CONF_DELAY: 0,
        },
        source=config_entries.SOURCE_IMPORT,
        unique_id=DOMAIN,
        options={},
    )
    entry.add_to_hass(hass)

    # Mock the remote entity
    hass.states.async_set(mock_remote_entity, "idle")

    # Try to set up cover platform via YAML
    cover_config = {
        "covers": [
            {
                "name": "Test Cover",
                "group": "0x0001",
                "serial": "0x106aa01",
                "repeat_count": 0,
                "repeat_delay": 0.2,
                "reverse": False,
            }
        ]
    }

    # Mock add_devices callback
    added_devices = []

    def mock_add_devices(devices):
        added_devices.extend(devices)

    # Call setup_platform
    setup_platform(hass, cover_config, mock_add_devices)

    # No devices should be added because config entry exists
    assert len(added_devices) == 0
