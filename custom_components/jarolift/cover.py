"""
Support for Jarolift cover
"""

import logging

from homeassistant.components.cover import (
    PLATFORM_SCHEMA,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from . import DOMAIN

CONF_COVERS = "covers"
CONF_GROUP = "group"
CONF_SERIAL = "serial"
CONF_REP_COUNT = "repeat_count"
CONF_REP_DELAY = "repeat_delay"
CONF_REVERSE = "reverse"

_COVERS_SCHEMA = vol.All(
    cv.ensure_list,
    [
        vol.Schema(
            {
                vol.Required(CONF_NAME): cv.string,
                vol.Required(CONF_GROUP): cv.string,
                vol.Required(CONF_SERIAL): cv.string,
                vol.Optional(CONF_REP_COUNT, default=0): cv.positive_int,
                vol.Optional(CONF_REP_DELAY, default=0.2): cv.positive_float,
                vol.Optional(CONF_REVERSE, default=False): cv.boolean,
            }
        )
    ],
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_COVERS): _COVERS_SCHEMA,
    }
)

DEPENDENCIES = ["jarolift"]

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Jarolift covers from YAML (backward compatibility)."""
    covers = []
    covers_conf = config.get(CONF_COVERS)

    for cover in covers_conf:
        covers.append(
            JaroliftCover(
                cover[CONF_NAME],
                cover[CONF_GROUP],
                cover[CONF_SERIAL],
                cover[CONF_REP_COUNT],
                cover[CONF_REP_DELAY],
                cover[CONF_REVERSE],
                hass,
            )
        )
    add_devices(covers)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Jarolift covers from a config entry."""
    covers = []
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    covers_conf = entry_data.get(CONF_COVERS, [])

    for cover in covers_conf:
        covers.append(
            JaroliftCover(
                cover[CONF_NAME],
                cover[CONF_GROUP],
                cover[CONF_SERIAL],
                cover.get(CONF_REP_COUNT, 0),
                cover.get(CONF_REP_DELAY, 0.2),
                cover.get(CONF_REVERSE, False),
                hass,
            )
        )
    async_add_entities(covers)


class JaroliftCover(CoverEntity):
    """Representation a jarolift Cover."""

    code_down = "0x2"
    code_stop = "0x4"
    code_up = "0x8"

    def __init__(self, name, group, serial, rep_count, rep_delay, reversed, hass):
        """Initialize the jarolift device."""
        self._name = name
        self._group = group
        self._serial = serial
        self._rep_count = rep_count
        self._rep_delay = rep_delay
        self._reversed = reversed
        self._hass = hass
        supported_features = 0
        supported_features |= CoverEntityFeature.OPEN
        supported_features |= CoverEntityFeature.CLOSE
        supported_features |= CoverEntityFeature.STOP
        self._attr_supported_features = supported_features
        self._attr_device_class = CoverDeviceClass.BLIND
        self._attr_unique_id = f"jarolift_{serial}_{group}"

    @property
    def serial(self):
        """Return the serial of this cover."""
        return self._serial

    @property
    def name(self):
        """Return the name of the cover if any."""
        return self._name

    @property
    def group(self):
        """Return the name of the group if any."""
        return self._group

    @property
    def should_poll(self):
        """No polling available in Jarolift cover."""
        return False

    @property
    def is_closed(self):
        """Return true if cover is closed, None if unknown."""
        return None

    @property
    def current_cover_position(self):
        """Return the current position of the cover.
        None is unknown, 0 is closed, 100 is fully open.
        """
        return None

    async def async_close_cover(self, **kwargs):
        """Close the cover."""
        actual_code = type(self).code_up if self._reversed else type(self).code_down
        _LOGGER.debug(
            "closing cover, sending %s (reversed=%s)", actual_code, self._reversed
        )
        await self.async_push_button(actual_code)

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        actual_code = type(self).code_down if self._reversed else type(self).code_up
        _LOGGER.debug(
            "opening cover, sending %s (reversed=%s)", actual_code, self._reversed
        )
        await self.async_push_button(actual_code)

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        _LOGGER.debug("stopping cover")
        await self.async_push_button(type(self).code_stop)

    async def async_push_button(self, value):
        await self._hass.services.async_call(
            "jarolift",
            "send_command",
            {
                "group": self._group,
                "serial": self._serial,
                "rep_count": self._rep_count,
                "rep_delay": self._rep_delay,
                "button": value,
            },
        )
        self.async_schedule_update_ha_state(True)
