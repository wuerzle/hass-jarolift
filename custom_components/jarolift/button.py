"""Jarolift Button Platform.

This module implements Home Assistant button entities for Jarolift covers.
Each configured cover gets a learning mode button that allows users to
pair/learn the cover without using the services directly.

The learning button triggers the existing jarolift.learn service for the
specific cover's serial and group.
"""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import (
    CONF_COVERS,
    CONF_GROUP,
    CONF_SERIAL,
    DEVICE_MANUFACTURER,
    DEVICE_MODEL,
    DEVICE_NAME,
    DEVICE_SW_VERSION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Jarolift buttons from a config entry."""
    buttons = []
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    covers_conf = entry_data.get(CONF_COVERS, [])

    for cover in covers_conf:
        buttons.append(
            JaroliftLearnButton(
                cover["name"],
                cover[CONF_GROUP],
                cover[CONF_SERIAL],
                hass,
                config_entry.entry_id,
            )
        )

    async_add_entities(buttons)


class JaroliftLearnButton(ButtonEntity):
    """Representation of a Jarolift learning mode button.

    This button entity allows users to trigger the learning mode for a specific
    Jarolift cover from the Home Assistant UI. When pressed, it calls the
    jarolift.learn service with the cover's serial and group.

    Attributes:
        _name: Display name for the button
        _group: Group identifier (hex string)
        _serial: Serial number (hex string)
        _hass: Home Assistant instance
        _entry_id: Config entry ID
    """

    def __init__(
        self,
        cover_name: str,
        group: str,
        serial: str,
        hass: HomeAssistant,
        entry_id: str,
    ):
        """Initialize the Jarolift learning button entity.

        Args:
            cover_name: Display name of the cover this button is for
            group: Group identifier (hex string)
            serial: Serial number (hex string)
            hass: Home Assistant instance
            entry_id: Config entry ID
        """
        self._cover_name = cover_name
        self._group = group
        self._serial = serial
        self._hass = hass
        self._entry_id = entry_id
        self._attr_unique_id = f"jarolift_{serial}_{group}_learn"
        self._attr_name = f"{cover_name} Learn"

        # Add device info to group with the hub device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=DEVICE_NAME,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
            sw_version=DEVICE_SW_VERSION,
        )

    async def async_press(self) -> None:
        """Handle the button press - trigger learning mode for this cover."""
        _LOGGER.info(
            "Learning mode button pressed for %s (serial: %s, group: %s)",
            self._cover_name,
            self._serial,
            self._group,
        )

        # Call the existing jarolift.learn service
        await self._hass.services.async_call(
            DOMAIN,
            "learn",
            {
                "serial": self._serial,
                "group": self._group,
            },
        )
