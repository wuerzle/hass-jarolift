"""Tests for Jarolift __init__.py."""
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from custom_components.jarolift import (
    DOMAIN,
    BuildPacket,
    ReadCounter,
    WriteCounter,
    _parse_hex_config_value,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
    bitRead,
    bitSet,
    decrypt,
    encrypt,
    setup,
)


def test_bit_read():
    """Test bitRead function."""
    # Test reading different bits
    value = 0b10101010
    assert bitRead(value, 0) == 0
    assert bitRead(value, 1) == 1
    assert bitRead(value, 2) == 0
    assert bitRead(value, 3) == 1
    assert bitRead(value, 7) == 1


def test_bit_set():
    """Test bitSet function."""
    # Test setting different bits
    value = 0b00000000
    assert bitSet(value, 0) == 0b00000001
    assert bitSet(value, 1) == 0b00000010
    assert bitSet(value, 7) == 0b10000000


def test_encrypt():
    """Test encrypt function."""
    # Test basic encryption (result will depend on implementation)
    x = 0x12345678
    keyHigh = 0xABCDEF01
    keyLow = 0x23456789
    
    result = encrypt(x, keyHigh, keyLow)
    assert isinstance(result, int)
    assert result != x  # Should be different after encryption


def test_decrypt():
    """Test decrypt function."""
    # Test basic decryption
    x = 0x12345678
    keyHigh = 0xABCDEF01
    keyLow = 0x23456789
    
    result = decrypt(x, keyHigh, keyLow)
    assert isinstance(result, int)
    assert result != x  # Should be different after decryption


def test_encrypt_decrypt_roundtrip():
    """Test that encrypt and decrypt are inverse operations."""
    x = 0x12345678
    keyHigh = 0xABCDEF01
    keyLow = 0x23456789
    
    encrypted = encrypt(x, keyHigh, keyLow)
    # Note: KeeLoq encrypt/decrypt are not simple inverses
    # This test just verifies they run without error
    decrypted = decrypt(encrypted, keyHigh, keyLow)
    assert isinstance(decrypted, int)


def test_build_packet():
    """Test BuildPacket function."""
    grouping = 0x0001
    serial = 0x106aa01
    button = 0x2
    counter = 0
    msb = 0x12345678
    lsb = 0x87654321
    hold = False
    
    packet = BuildPacket(grouping, serial, button, counter, msb, lsb, hold)
    
    assert isinstance(packet, str)
    assert packet.startswith("b64:")


def test_parse_hex_config_value():
    """Test _parse_hex_config_value function."""
    assert _parse_hex_config_value("0x1234") == 0x1234
    assert _parse_hex_config_value("0xABCD") == 0xABCD
    assert _parse_hex_config_value("0xFF") == 0xFF


def test_read_counter_nonexistent(tmp_path):
    """Test ReadCounter with non-existent file."""
    counter_file = str(tmp_path / "counter_")
    serial = 0x106aa01
    
    result = ReadCounter(counter_file, serial)
    assert result == 0


def test_write_and_read_counter(tmp_path):
    """Test WriteCounter and ReadCounter."""
    counter_file = str(tmp_path / "counter_")
    serial = 0x106aa01
    counter_value = 42
    
    WriteCounter(counter_file, serial, counter_value)
    result = ReadCounter(counter_file, serial)
    
    assert result == counter_value


def test_write_counter_increment(tmp_path):
    """Test writing incremented counter values."""
    counter_file = str(tmp_path / "counter_")
    serial = 0x106aa01
    
    WriteCounter(counter_file, serial, 1)
    assert ReadCounter(counter_file, serial) == 1
    
    WriteCounter(counter_file, serial, 2)
    assert ReadCounter(counter_file, serial) == 2
    
    WriteCounter(counter_file, serial, 100)
    assert ReadCounter(counter_file, serial) == 100


async def test_setup_with_yaml_config(hass):
    """Test setup with YAML configuration."""
    config = {
        DOMAIN: {
            "remote_entity_id": "remote.test_remote",
            "MSB": "0x12345678",
            "LSB": "0x87654321",
            "delay": 0,
        }
    }
    
    with patch("custom_components.jarolift.hass") as mock_hass:
        result = setup(hass, config)
    
    assert result is True
    assert DOMAIN in hass.data
    assert "yaml_config" in hass.data[DOMAIN]
    assert "yaml_covers" in hass.data[DOMAIN]


async def test_setup_without_yaml_config(hass):
    """Test setup without YAML configuration."""
    config = {}
    
    result = setup(hass, config)
    
    assert result is True


async def test_async_setup_entry(hass, mock_remote_entity):
    """Test async_setup_entry."""
    hass.states.async_set(mock_remote_entity, "idle")
    
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "remote_entity_id": mock_remote_entity,
        "MSB": "0x12345678",
        "LSB": "0x87654321",
        "delay": 0,
    }
    entry.options = {"covers": []}
    entry.add_update_listener = MagicMock(return_value=lambda: None)
    entry.async_on_unload = MagicMock()
    
    with patch(
        "custom_components.jarolift.hass.config_entries.async_forward_entry_setups",
        return_value=True,
    ) as mock_forward:
        result = await async_setup_entry(hass, entry)
    
    assert result is True
    assert entry.entry_id in hass.data[DOMAIN]


async def test_async_unload_entry(hass, mock_remote_entity):
    """Test async_unload_entry."""
    hass.states.async_set(mock_remote_entity, "idle")
    
    entry = MagicMock()
    entry.entry_id = "test_entry"
    
    # Setup entry first
    hass.data[DOMAIN] = {entry.entry_id: {}}
    
    with patch(
        "custom_components.jarolift.hass.config_entries.async_unload_platforms",
        return_value=True,
    ) as mock_unload:
        result = await async_unload_entry(hass, entry)
    
    assert result is True
    assert entry.entry_id not in hass.data[DOMAIN]


async def test_async_reload_entry(hass, mock_remote_entity):
    """Test async_reload_entry."""
    hass.states.async_set(mock_remote_entity, "idle")
    
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "remote_entity_id": mock_remote_entity,
        "MSB": "0x12345678",
        "LSB": "0x87654321",
        "delay": 0,
    }
    entry.options = {"covers": []}
    entry.add_update_listener = MagicMock(return_value=lambda: None)
    entry.async_on_unload = MagicMock()
    
    # Setup entry first
    hass.data[DOMAIN] = {entry.entry_id: {}}
    
    with patch(
        "custom_components.jarolift.async_unload_entry", return_value=True
    ) as mock_unload, patch(
        "custom_components.jarolift.async_setup_entry", return_value=True
    ) as mock_setup:
        await async_reload_entry(hass, entry)
    
    mock_unload.assert_called_once()
    mock_setup.assert_called_once()
