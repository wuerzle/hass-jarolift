"""Tests for Jarolift config flow."""
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_NAME

from custom_components.jarolift import DOMAIN
from custom_components.jarolift.config_flow import (
    CONF_COVERS,
    CONF_DELAY,
    CONF_GROUP,
    CONF_LSB,
    CONF_MSB,
    CONF_REMOTE_ENTITY_ID,
    CONF_REP_COUNT,
    CONF_REP_DELAY,
    CONF_REVERSE,
    CONF_SERIAL,
)


async def test_user_form_valid_input(hass, mock_remote_entity):
    """Test user form with valid input."""
    # Mock the remote entity existence
    hass.states.async_set(mock_remote_entity, "idle")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # Test with valid input
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_REMOTE_ENTITY_ID: mock_remote_entity,
            CONF_MSB: "0x12345678",
            CONF_LSB: "0x87654321",
            CONF_DELAY: 0,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Jarolift"
    assert result["data"] == {
        CONF_REMOTE_ENTITY_ID: mock_remote_entity,
        CONF_MSB: "0x12345678",
        CONF_LSB: "0x87654321",
        CONF_DELAY: 0,
    }
    assert result["options"] == {CONF_COVERS: []}


async def test_user_form_invalid_remote_entity(hass):
    """Test user form with invalid remote entity."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Test with non-existent remote entity
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_REMOTE_ENTITY_ID: "remote.nonexistent",
            CONF_MSB: "0x12345678",
            CONF_LSB: "0x87654321",
            CONF_DELAY: 0,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {CONF_REMOTE_ENTITY_ID: "invalid_remote_entity"}


async def test_user_form_already_configured(hass, mock_remote_entity):
    """Test user form when already configured."""
    # Mock the remote entity existence
    hass.states.async_set(mock_remote_entity, "idle")

    # Create an existing entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        data={
            CONF_REMOTE_ENTITY_ID: mock_remote_entity,
            CONF_MSB: "0x12345678",
            CONF_LSB: "0x87654321",
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_REMOTE_ENTITY_ID: mock_remote_entity,
            CONF_MSB: "0x12345678",
            CONF_LSB: "0x87654321",
            CONF_DELAY: 0,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_import_from_yaml(hass, mock_yaml_config, mock_remote_entity):
    """Test importing configuration from YAML."""
    # Mock the remote entity
    hass.states.async_set(mock_remote_entity, "idle")

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_IMPORT},
        data=mock_yaml_config,
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Jarolift"
    assert result["data"][CONF_REMOTE_ENTITY_ID] == mock_remote_entity
    assert result["data"][CONF_MSB] == "0x12345678"
    assert result["data"][CONF_LSB] == "0x87654321"


async def test_import_with_covers(hass, mock_yaml_config, mock_remote_entity, mock_cover_config):
    """Test importing configuration with covers from YAML."""
    # Mock the remote entity
    hass.states.async_set(mock_remote_entity, "idle")

    # Store covers in hass.data as would be done by setup_platform
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["yaml_covers"] = [mock_cover_config]

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_IMPORT},
        data=mock_yaml_config,
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["options"][CONF_COVERS] == [mock_cover_config]


async def test_import_missing_configuration(hass):
    """Test importing with missing configuration."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_IMPORT},
        data={},
    )

    assert result["type"] == data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == "missing_configuration"


async def test_options_flow_add_cover(hass, mock_remote_entity):
    """Test adding a cover through options flow."""
    hass.states.async_set(mock_remote_entity, "idle")

    # Create a config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        data={
            CONF_REMOTE_ENTITY_ID: mock_remote_entity,
            CONF_MSB: "0x12345678",
            CONF_LSB: "0x87654321",
        },
        options={CONF_COVERS: []},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "manage_covers"

    # Select add action
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"action": "add"},
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "add_cover"

    # Add a cover
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_NAME: "Test Cover",
            CONF_GROUP: "0x0001",
            CONF_SERIAL: "0x106aa01",
            CONF_REP_COUNT: 0,
            CONF_REP_DELAY: 0.2,
            CONF_REVERSE: False,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "manage_covers"


async def test_options_flow_add_duplicate_cover(hass, mock_remote_entity, mock_cover_config):
    """Test adding a duplicate cover through options flow."""
    hass.states.async_set(mock_remote_entity, "idle")

    # Create a config entry with existing cover
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        data={
            CONF_REMOTE_ENTITY_ID: mock_remote_entity,
            CONF_MSB: "0x12345678",
            CONF_LSB: "0x87654321",
        },
        options={CONF_COVERS: [mock_cover_config]},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"action": "add"},
    )

    # Try to add duplicate cover
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=mock_cover_config,
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "duplicate_cover"}


async def test_options_flow_edit_cover(hass, mock_remote_entity, mock_cover_config):
    """Test editing a cover through options flow."""
    hass.states.async_set(mock_remote_entity, "idle")

    # Create a config entry with existing cover
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        data={
            CONF_REMOTE_ENTITY_ID: mock_remote_entity,
            CONF_MSB: "0x12345678",
            CONF_LSB: "0x87654321",
        },
        options={CONF_COVERS: [mock_cover_config]},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    
    # Select edit action
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"action": "edit"},
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "select_cover_to_edit"

    # Select the cover to edit
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"cover_index": "0"},
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "edit_cover"

    # Edit the cover
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_NAME: "Updated Cover",
            CONF_GROUP: "0x0001",
            CONF_SERIAL: "0x106aa01",
            CONF_REP_COUNT: 4,
            CONF_REP_DELAY: 0.3,
            CONF_REVERSE: True,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "manage_covers"


async def test_options_flow_remove_cover(hass, mock_remote_entity, mock_cover_config):
    """Test removing a cover through options flow."""
    hass.states.async_set(mock_remote_entity, "idle")

    # Create a config entry with existing cover
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        data={
            CONF_REMOTE_ENTITY_ID: mock_remote_entity,
            CONF_MSB: "0x12345678",
            CONF_LSB: "0x87654321",
        },
        options={CONF_COVERS: [mock_cover_config]},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    
    # Select remove action
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"action": "remove"},
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "select_cover_to_remove"

    # Select the cover to remove
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"cover_index": "0"},
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "manage_covers"


async def test_options_flow_finish(hass, mock_remote_entity):
    """Test finishing options flow."""
    hass.states.async_set(mock_remote_entity, "idle")

    # Create a config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        data={
            CONF_REMOTE_ENTITY_ID: mock_remote_entity,
            CONF_MSB: "0x12345678",
            CONF_LSB: "0x87654321",
        },
        options={CONF_COVERS: []},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    
    # Select finish action
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"action": "finish"},
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY


# Mock ConfigEntry class for testing
class MockConfigEntry:
    """Mock ConfigEntry for testing."""

    def __init__(self, domain, unique_id, data, options=None):
        """Initialize mock config entry."""
        self.domain = domain
        self.unique_id = unique_id
        self.data = data
        self.options = options or {}
        self.entry_id = "test_entry_id"

    def add_to_hass(self, hass):
        """Add to hass."""
        hass.config_entries._entries[self.entry_id] = self
