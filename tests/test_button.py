"""Test button entities for Jarolift integration."""

import sys
from pathlib import Path

# Add parent directory to path to import custom_components
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.jarolift import DOMAIN
from custom_components.jarolift.button import JaroliftLearnButton


def test_button_has_device_info():
    """Test that button has device_info."""
    entry_id = "test_entry_123"
    button = JaroliftLearnButton(
        cover_name="Test Cover",
        group="0x0001",
        serial="0x116ea01",
        hass=None,
        entry_id=entry_id,
    )

    assert hasattr(button, "_attr_device_info")
    device_info = button._attr_device_info

    # Verify device_info structure
    assert device_info is not None
    assert isinstance(device_info, dict)
    assert device_info["identifiers"] == {(DOMAIN, entry_id)}
    assert device_info["name"] == "Jarolift"
    assert device_info["manufacturer"] == "Jarolift"
    assert device_info["model"] == "KeeLoq RF Controller"
    assert device_info["sw_version"] == "2.0.5"


def test_button_unique_id():
    """Test that button has correct unique ID."""
    button = JaroliftLearnButton(
        cover_name="Test Cover",
        group="0x0001",
        serial="0x116ea01",
        hass=None,
        entry_id="test_entry",
    )

    assert button._attr_unique_id == "jarolift_0x116ea01_0x0001_learn"


def test_button_name():
    """Test that button has correct name."""
    button = JaroliftLearnButton(
        cover_name="Living Room Cover",
        group="0x0001",
        serial="0x116ea01",
        hass=None,
        entry_id="test_entry",
    )

    assert button._attr_name == "Living Room Cover Learn"


def test_multiple_buttons_same_device():
    """Test that multiple buttons share the same device identifier."""
    entry_id = "test_entry_123"

    button1 = JaroliftLearnButton(
        cover_name="Cover 1",
        group="0x0001",
        serial="0x116ea01",
        hass=None,
        entry_id=entry_id,
    )

    button2 = JaroliftLearnButton(
        cover_name="Cover 2",
        group="0x0002",
        serial="0x116ea02",
        hass=None,
        entry_id=entry_id,
    )

    # Both buttons should reference the same device
    assert (
        button1._attr_device_info["identifiers"]
        == button2._attr_device_info["identifiers"]
    )


def test_button_attributes():
    """Test that button stores correct attributes."""
    button = JaroliftLearnButton(
        cover_name="Test Cover",
        group="0x0001",
        serial="0x116ea01",
        hass=None,
        entry_id="test_entry",
    )

    assert button._cover_name == "Test Cover"
    assert button._group == "0x0001"
    assert button._serial == "0x116ea01"
    assert button._entry_id == "test_entry"


if __name__ == "__main__":
    print("Testing button entities...")

    try:
        test_button_has_device_info()
        print("✓ Button has correct device_info")
    except Exception as e:
        print(f"✗ test_button_has_device_info failed: {e}")
        sys.exit(1)

    try:
        test_button_unique_id()
        print("✓ Button has correct unique ID")
    except Exception as e:
        print(f"✗ test_button_unique_id failed: {e}")
        sys.exit(1)

    try:
        test_button_name()
        print("✓ Button has correct name")
    except Exception as e:
        print(f"✗ test_button_name failed: {e}")
        sys.exit(1)

    try:
        test_multiple_buttons_same_device()
        print("✓ Multiple buttons share same device identifier")
    except Exception as e:
        print(f"✗ test_multiple_buttons_same_device failed: {e}")
        sys.exit(1)

    try:
        test_button_attributes()
        print("✓ Button stores correct attributes")
    except Exception as e:
        print(f"✗ test_button_attributes failed: {e}")
        sys.exit(1)

    print("\nAll button tests passed!")
