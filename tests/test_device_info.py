"""Test device info for Jarolift integration."""

import sys
from pathlib import Path

# Add parent directory to path to import custom_components
sys.path.insert(0, str(Path(__file__).parent.parent))


from custom_components.jarolift import DOMAIN
from custom_components.jarolift.cover import JaroliftCover


def test_cover_without_entry_id_no_device_info():
    """Test that cover without entry_id doesn't have device_info (YAML mode)."""
    cover = JaroliftCover(
        name="Test Cover",
        group="0x0001",
        serial="0x116ea01",
        rep_count=0,
        rep_delay=0.2,
        reversed=False,
        hass=None,
        entry_id=None,
    )

    # Device info should be None for YAML mode
    assert cover._attr_device_info is None or cover._attr_device_info == {}


def test_cover_with_entry_id_has_device_info():
    """Test that cover with entry_id has device_info (config entry mode)."""
    entry_id = "test_entry_123"
    cover = JaroliftCover(
        name="Test Cover",
        group="0x0001",
        serial="0x116ea01",
        rep_count=0,
        rep_delay=0.2,
        reversed=False,
        hass=None,
        entry_id=entry_id,
    )

    assert hasattr(cover, "_attr_device_info")
    device_info = cover._attr_device_info

    # Verify device_info structure (it's a dict, not a class instance)
    assert device_info is not None
    assert isinstance(device_info, dict)
    assert device_info["identifiers"] == {(DOMAIN, entry_id)}
    assert device_info["name"] == "Jarolift"
    assert device_info["manufacturer"] == "Jarolift"
    assert device_info["model"] == "KeeLoq RF Controller"
    assert device_info["sw_version"] == "2.0.5"


def test_multiple_covers_same_device():
    """Test that multiple covers share the same device identifier."""
    entry_id = "test_entry_123"

    cover1 = JaroliftCover(
        name="Cover 1",
        group="0x0001",
        serial="0x116ea01",
        rep_count=0,
        rep_delay=0.2,
        reversed=False,
        hass=None,
        entry_id=entry_id,
    )

    cover2 = JaroliftCover(
        name="Cover 2",
        group="0x0002",
        serial="0x116ea02",
        rep_count=0,
        rep_delay=0.2,
        reversed=False,
        hass=None,
        entry_id=entry_id,
    )

    # Both covers should reference the same device
    assert (
        cover1._attr_device_info["identifiers"]
        == cover2._attr_device_info["identifiers"]
    )


if __name__ == "__main__":
    print("Testing device info...")
    try:
        test_cover_without_entry_id_no_device_info()
        print("✓ Cover without entry_id has no device_info")
    except Exception as e:
        print(f"✗ test_cover_without_entry_id_no_device_info failed: {e}")
        sys.exit(1)

    try:
        test_cover_with_entry_id_has_device_info()
        print("✓ Cover with entry_id has correct device_info")
    except Exception as e:
        print(f"✗ test_cover_with_entry_id_has_device_info failed: {e}")
        sys.exit(1)

    try:
        test_multiple_covers_same_device()
        print("✓ Multiple covers share same device identifier")
    except Exception as e:
        print(f"✗ test_multiple_covers_same_device failed: {e}")
        sys.exit(1)

    print("\nAll device info tests passed!")
