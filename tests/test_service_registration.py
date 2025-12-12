"""Test service registration fix for async context."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.jarolift import DOMAIN, _register_services


@pytest.mark.asyncio
async def test_register_services_is_async():
    """Test that _register_services is an async function."""
    import inspect
    
    assert inspect.iscoroutinefunction(_register_services), \
        "_register_services should be an async function"


@pytest.mark.asyncio
async def test_register_services_uses_async_register():
    """Test that _register_services uses async_register instead of register."""
    hass = MagicMock()
    hass.services.has_service = MagicMock(return_value=False)
    hass.services.async_register = MagicMock()
    
    # Call the async function
    await _register_services(
        hass,
        "remote.test_remote",
        0x12345678,
        0x87654321,
        0,
        "/tmp/counter_"
    )
    
    # Verify async_register was called for all services
    assert hass.services.async_register.call_count == 4
    
    # Verify it was called with correct service names
    service_names = [call[0][1] for call in hass.services.async_register.call_args_list]
    assert "send_raw" in service_names
    assert "send_command" in service_names
    assert "learn" in service_names
    assert "clear" in service_names


@pytest.mark.asyncio
async def test_register_services_skips_if_already_registered():
    """Test that _register_services skips registration if services already exist."""
    hass = MagicMock()
    hass.services.has_service = MagicMock(return_value=True)
    hass.services.async_register = MagicMock()
    
    # Call the async function
    await _register_services(
        hass,
        "remote.test_remote",
        0x12345678,
        0x87654321,
        0,
        "/tmp/counter_"
    )
    
    # Verify async_register was NOT called since service already exists
    assert hass.services.async_register.call_count == 0
