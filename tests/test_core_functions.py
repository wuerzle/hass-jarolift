"""Simple tests for Jarolift core functions that don't require Home Assistant."""
import os
import tempfile

import pytest

# Add the custom_components directory to the path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from custom_components.jarolift import (
    BuildPacket,
    ReadCounter,
    WriteCounter,
    _parse_hex_config_value,
    bitRead,
    bitSet,
    decrypt,
    encrypt,
)


class TestBitOperations:
    """Test bit operations."""

    def test_bit_read(self):
        """Test bitRead function."""
        value = 0b10101010
        assert bitRead(value, 0) == 0
        assert bitRead(value, 1) == 1
        assert bitRead(value, 2) == 0
        assert bitRead(value, 3) == 1
        assert bitRead(value, 7) == 1

    def test_bit_set(self):
        """Test bitSet function."""
        value = 0b00000000
        assert bitSet(value, 0) == 0b00000001
        assert bitSet(value, 1) == 0b00000010
        assert bitSet(value, 7) == 0b10000000


class TestKeeLoqEncryption:
    """Test KeeLoq encryption functions."""

    def test_encrypt(self):
        """Test encrypt function produces valid output."""
        x = 0x12345678
        keyHigh = 0xABCDEF01
        keyLow = 0x23456789
        
        result = encrypt(x, keyHigh, keyLow)
        assert isinstance(result, int)
        assert result != x  # Should be different after encryption
        assert result >= 0  # Should be non-negative
        assert result <= 0xFFFFFFFF  # Should fit in 32 bits

    def test_decrypt(self):
        """Test decrypt function produces valid output."""
        x = 0x12345678
        keyHigh = 0xABCDEF01
        keyLow = 0x23456789
        
        result = decrypt(x, keyHigh, keyLow)
        assert isinstance(result, int)
        assert result != x  # Should be different after decryption
        assert result >= 0
        assert result <= 0xFFFFFFFF

    def test_encrypt_deterministic(self):
        """Test that encryption is deterministic."""
        x = 0x12345678
        keyHigh = 0xABCDEF01
        keyLow = 0x23456789
        
        result1 = encrypt(x, keyHigh, keyLow)
        result2 = encrypt(x, keyHigh, keyLow)
        assert result1 == result2


class TestPacketBuilding:
    """Test packet building functions."""

    def test_build_packet_format(self):
        """Test BuildPacket produces correct format."""
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
        # The packet should be base64 encoded
        import base64
        try:
            base64.b64decode(packet[4:])
            assert True
        except Exception:
            assert False, "Packet is not valid base64"

    def test_build_packet_with_hold(self):
        """Test BuildPacket with hold flag."""
        grouping = 0x0001
        serial = 0x106aa01
        button = 0x2
        counter = 0
        msb = 0x12345678
        lsb = 0x87654321
        hold = True
        
        packet = BuildPacket(grouping, serial, button, counter, msb, lsb, hold)
        
        assert isinstance(packet, str)
        assert packet.startswith("b64:")

    def test_build_packet_different_buttons(self):
        """Test BuildPacket with different button codes."""
        grouping = 0x0001
        serial = 0x106aa01
        counter = 0
        msb = 0x12345678
        lsb = 0x87654321
        hold = False
        
        packet_down = BuildPacket(grouping, serial, 0x2, counter, msb, lsb, hold)
        packet_stop = BuildPacket(grouping, serial, 0x4, counter, msb, lsb, hold)
        packet_up = BuildPacket(grouping, serial, 0x8, counter, msb, lsb, hold)
        
        # All should be valid but different
        assert packet_down != packet_stop
        assert packet_stop != packet_up
        assert packet_down != packet_up


class TestCounterOperations:
    """Test counter file operations."""

    def test_read_counter_nonexistent(self):
        """Test ReadCounter with non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            counter_file = os.path.join(tmpdir, "counter_")
            serial = 0x106aa01
            
            result = ReadCounter(counter_file, serial)
            assert result == 0

    def test_write_and_read_counter(self):
        """Test WriteCounter and ReadCounter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            counter_file = os.path.join(tmpdir, "counter_")
            serial = 0x106aa01
            counter_value = 42
            
            WriteCounter(counter_file, serial, counter_value)
            result = ReadCounter(counter_file, serial)
            
            assert result == counter_value

    def test_write_counter_increment(self):
        """Test writing incremented counter values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            counter_file = os.path.join(tmpdir, "counter_")
            serial = 0x106aa01
            
            WriteCounter(counter_file, serial, 1)
            assert ReadCounter(counter_file, serial) == 1
            
            WriteCounter(counter_file, serial, 2)
            assert ReadCounter(counter_file, serial) == 2
            
            WriteCounter(counter_file, serial, 100)
            assert ReadCounter(counter_file, serial) == 100

    def test_multiple_serials(self):
        """Test counter operations with multiple serials."""
        with tempfile.TemporaryDirectory() as tmpdir:
            counter_file = os.path.join(tmpdir, "counter_")
            serial1 = 0x106aa01
            serial2 = 0x106aa02
            
            WriteCounter(counter_file, serial1, 10)
            WriteCounter(counter_file, serial2, 20)
            
            assert ReadCounter(counter_file, serial1) == 10
            assert ReadCounter(counter_file, serial2) == 20


class TestConfigHelpers:
    """Test configuration helper functions."""

    def test_parse_hex_config_value(self):
        """Test _parse_hex_config_value function."""
        assert _parse_hex_config_value("0x1234") == 0x1234
        assert _parse_hex_config_value("0xABCD") == 0xABCD
        assert _parse_hex_config_value("0xFF") == 0xFF
        assert _parse_hex_config_value("0x12345678") == 0x12345678
        assert _parse_hex_config_value("0x87654321") == 0x87654321

    def test_parse_hex_config_value_lowercase(self):
        """Test parsing lowercase hex values."""
        assert _parse_hex_config_value("0xabcd") == 0xABCD
        assert _parse_hex_config_value("0xff") == 0xFF


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
