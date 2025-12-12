"""Standalone tests for Jarolift core functions."""

import base64
import os
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def bitRead(value, bit):
    """Read a specific bit from a value."""
    return ((value) >> (bit)) & 0x01


def bitSet(value, bit):
    """Set a specific bit in a value."""
    return (value) | (1 << (bit))


def encrypt(x, keyHigh, keyLow):
    """Encrypt using KeeLoq algorithm."""
    KeeLoq_NLF = 0x3A5C742E
    for r in range(0, 528):
        keyBitNo = r & 63
        if keyBitNo < 32:
            keyBitVal = bitRead(keyLow, keyBitNo)
        else:
            keyBitVal = bitRead(keyHigh, keyBitNo - 32)
        index = (
            1 * bitRead(x, 1)
            + 2 * bitRead(x, 9)
            + 4 * bitRead(x, 20)
            + 8 * bitRead(x, 26)
            + 16 * bitRead(x, 31)
        )
        bitVal = bitRead(x, 0) ^ bitRead(x, 16) ^ bitRead(KeeLoq_NLF, index) ^ keyBitVal
        x = (x >> 1) ^ bitVal << 31
    return x


def decrypt(x, keyHigh, keyLow):
    """Decrypt using KeeLoq algorithm."""
    KeeLoq_NLF = 0x3A5C742E
    for r in range(0, 528):
        keyBitNo = (15 - r) & 63
        if keyBitNo < 32:
            keyBitVal = bitRead(keyLow, keyBitNo)
        else:
            keyBitVal = bitRead(keyHigh, keyBitNo - 32)
        index = (
            1 * bitRead(x, 0)
            + 2 * bitRead(x, 8)
            + 4 * bitRead(x, 19)
            + 8 * bitRead(x, 25)
            + 16 * bitRead(x, 30)
        )
        bitVal = (
            bitRead(x, 31) ^ bitRead(x, 15) ^ bitRead(KeeLoq_NLF, index) ^ keyBitVal
        )
        x = ((x << 1) & 0xFFFFFFFF) ^ bitVal
    return x


def BuildPacket(Grouping, Serial, Button, Counter, MSB, LSB, Hold):
    """Build a packet for transmission."""
    keylow = Serial | 0x20000000
    keyhigh = Serial | 0x60000000
    KeyLSB = decrypt(keylow, MSB, LSB)
    KeyMSB = decrypt(keyhigh, MSB, LSB)
    Decoded = Counter | ((Serial & 0xFF) << 16) | ((Grouping & 0xFF) << 24)
    Encoded = encrypt(Decoded, KeyMSB, KeyLSB)
    data = (
        (Encoded) | (Serial << 32) | (Button << 60) | (((Grouping >> 8) & 0xFF) << 64)
    )
    datastring = bin(data)[2:].zfill(72)[::-1]
    codedstring = ""
    for i in range(0, len(datastring)):
        if i == len(datastring) - 1:
            if datastring[i] == "1":
                codedstring = codedstring + "0c0005dc"
            else:
                codedstring = codedstring + "190005dc"
        else:
            if datastring[i] == "1":
                codedstring = codedstring + "0c19"
            else:
                codedstring = codedstring + "190c"
    codedstring = "190c1a0001e4310c0d0c0d0c0d0c0d0c0d0c0d0c0d0c0d7a" + codedstring
    slen = len(codedstring) / 2
    if Hold:
        codedstring = "b214" + hex(int(slen))[2:] + "00" + codedstring
    else:
        codedstring = "b200" + hex(int(slen))[2:] + "00" + codedstring
    import binascii

    packet = base64.b64encode(binascii.unhexlify(codedstring))
    return "b64:" + packet.decode("utf-8")


def ReadCounter(counter_file, serial):
    """Read counter from file."""
    filename = counter_file + hex(serial) + ".txt"
    if os.path.isfile(filename):
        with open(filename, encoding="utf-8") as fo:
            Counter = int(fo.readline())
        return Counter
    else:
        return 0


def WriteCounter(counter_file, serial, Counter):
    """Write counter to file."""
    filename = counter_file + hex(serial) + ".txt"
    with open(filename, "w", encoding="utf-8") as fo:
        fo.write(str(Counter))


def _parse_hex_config_value(value):
    """Parse a hex configuration value to integer."""
    return int(value, 16)


# ===== TESTS =====


def test_bit_read():
    """Test bitRead function."""
    print("Testing bitRead...")
    value = 0b10101010
    assert bitRead(value, 0) == 0
    assert bitRead(value, 1) == 1
    assert bitRead(value, 2) == 0
    assert bitRead(value, 3) == 1
    assert bitRead(value, 7) == 1
    print("✓ bitRead tests passed")


def test_bit_set():
    """Test bitSet function."""
    print("Testing bitSet...")
    value = 0b00000000
    assert bitSet(value, 0) == 0b00000001
    assert bitSet(value, 1) == 0b00000010
    assert bitSet(value, 7) == 0b10000000
    print("✓ bitSet tests passed")


def test_encrypt():
    """Test encrypt function."""
    print("Testing encrypt...")
    x = 0x12345678
    keyHigh = 0xABCDEF01
    keyLow = 0x23456789

    result = encrypt(x, keyHigh, keyLow)
    assert isinstance(result, int)
    assert result != x
    assert result >= 0
    assert result <= 0xFFFFFFFF
    print(f"  Encrypted 0x{x:08X} to 0x{result:08X}")
    print("✓ encrypt tests passed")


def test_decrypt():
    """Test decrypt function."""
    print("Testing decrypt...")
    x = 0x12345678
    keyHigh = 0xABCDEF01
    keyLow = 0x23456789

    result = decrypt(x, keyHigh, keyLow)
    assert isinstance(result, int)
    assert result != x
    assert result >= 0
    assert result <= 0xFFFFFFFF
    print(f"  Decrypted 0x{x:08X} to 0x{result:08X}")
    print("✓ decrypt tests passed")


def test_build_packet():
    """Test BuildPacket function."""
    print("Testing BuildPacket...")
    grouping = 0x0001
    serial = 0x106AA01
    button = 0x2
    counter = 0
    msb = 0x12345678
    lsb = 0x87654321
    hold = False

    packet = BuildPacket(grouping, serial, button, counter, msb, lsb, hold)

    assert isinstance(packet, str)
    assert packet.startswith("b64:")

    # Verify it's valid base64
    try:
        base64.b64decode(packet[4:])
    except Exception as e:
        raise AssertionError(f"Packet is not valid base64: {e}") from e

    print(f"  Generated packet: {packet[:50]}...")
    print("✓ BuildPacket tests passed")


def test_build_packet_different_buttons():
    """Test BuildPacket with different button codes."""
    print("Testing BuildPacket with different buttons...")
    grouping = 0x0001
    serial = 0x106AA01
    counter = 0
    msb = 0x12345678
    lsb = 0x87654321
    hold = False

    packet_down = BuildPacket(grouping, serial, 0x2, counter, msb, lsb, hold)
    packet_stop = BuildPacket(grouping, serial, 0x4, counter, msb, lsb, hold)
    packet_up = BuildPacket(grouping, serial, 0x8, counter, msb, lsb, hold)

    assert packet_down != packet_stop
    assert packet_stop != packet_up
    assert packet_down != packet_up
    print("  Generated 3 different packets for down/stop/up")
    print("✓ Different button tests passed")


def test_counter_operations():
    """Test counter file operations."""
    print("Testing counter operations...")
    with tempfile.TemporaryDirectory() as tmpdir:
        counter_file = os.path.join(tmpdir, "counter_")
        serial = 0x106AA01

        # Test reading non-existent counter
        result = ReadCounter(counter_file, serial)
        assert result == 0
        print("  ✓ Non-existent counter returns 0")

        # Test writing and reading
        WriteCounter(counter_file, serial, 42)
        result = ReadCounter(counter_file, serial)
        assert result == 42
        print("  ✓ Write and read counter works")

        # Test incrementing
        WriteCounter(counter_file, serial, 1)
        assert ReadCounter(counter_file, serial) == 1
        WriteCounter(counter_file, serial, 2)
        assert ReadCounter(counter_file, serial) == 2
        WriteCounter(counter_file, serial, 100)
        assert ReadCounter(counter_file, serial) == 100
        print("  ✓ Counter increment works")

        # Test multiple serials
        serial2 = 0x106AA02
        WriteCounter(counter_file, serial, 10)
        WriteCounter(counter_file, serial2, 20)
        assert ReadCounter(counter_file, serial) == 10
        assert ReadCounter(counter_file, serial2) == 20
        print("  ✓ Multiple serials work")

    print("✓ Counter operations tests passed")


def test_parse_hex_config_value():
    """Test _parse_hex_config_value function."""
    print("Testing _parse_hex_config_value...")
    assert _parse_hex_config_value("0x1234") == 0x1234
    assert _parse_hex_config_value("0xABCD") == 0xABCD
    assert _parse_hex_config_value("0xFF") == 0xFF
    assert _parse_hex_config_value("0x12345678") == 0x12345678
    assert _parse_hex_config_value("0xabcd") == 0xABCD
    print("✓ Hex parsing tests passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running Jarolift Core Functions Tests")
    print("=" * 60 + "\n")

    tests = [
        test_bit_read,
        test_bit_set,
        test_encrypt,
        test_decrypt,
        test_build_packet,
        test_build_packet_different_buttons,
        test_counter_operations,
        test_parse_hex_config_value,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
