#!/usr/bin/env python3
"""
Demonstration of how button entities are created for Jarolift covers.

This script shows what button entities will be created for a sample configuration.
"""

import sys
from pathlib import Path

# Add parent directory to path to import custom_components
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.jarolift.button import JaroliftLearnButton

# Example configuration with multiple covers
sample_covers = [
    {
        "name": "Living Room Cover",
        "group": "0x0001",
        "serial": "0x106aa01",
    },
    {
        "name": "Bedroom Cover",
        "group": "0x0002",
        "serial": "0x106aa02",
    },
    {
        "name": "Kitchen Blind",
        "group": "0x0004",
        "serial": "0x106aa03",
    },
]

print("=" * 70)
print("Jarolift Button Entities - What Users Will See")
print("=" * 70)
print()
print("After adding covers via the Jarolift integration UI, each cover")
print("will automatically get a learning mode button in Home Assistant:")
print()

entry_id = "jarolift_hub_123"

for cover in sample_covers:
    button = JaroliftLearnButton(
        cover_name=cover["name"],
        group=cover["group"],
        serial=cover["serial"],
        hass=None,
        entry_id=entry_id,
    )
    
    print(f"Cover: {cover['name']}")
    print(f"  └─ Button Entity Name: {button._attr_name}")
    print(f"     Unique ID: {button._attr_unique_id}")
    print(f"     Serial: {button._serial}, Group: {button._group}")
    print()

print("=" * 70)
print("How to Use the Learning Buttons:")
print("=" * 70)
print()
print("1. Go to Settings → Devices & Services → Jarolift")
print("2. Click on the Jarolift device card")
print("3. You'll see all your covers AND their learning buttons")
print("4. Put your physical Jarolift cover into learning mode")
print("5. Press the corresponding learning button in Home Assistant")
print("6. The cover will confirm it has learned the remote")
print()
print("Benefits:")
print("  • No need to use Developer Tools or write service calls")
print("  • Each cover has its own independent learning button")
print("  • Clear visual indication of which button controls which cover")
print("  • All entities grouped together under the Jarolift device")
print()
