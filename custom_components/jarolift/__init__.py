"""
Support a 'Jarolift' remote as a separate remote.
Basically a proxy adding Keeloq encryption to commands sent via another remote then.
"""

import base64
import binascii
import logging
import os.path
import threading
from time import sleep

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

DOMAIN = "jarolift"
_LOGGER = logging.getLogger(__name__)
mutex = threading.Lock()

PLATFORMS = [Platform.COVER]

# Configuration constants
CONF_REMOTE_ENTITY_ID = "remote_entity_id"
CONF_MSB = "MSB"
CONF_LSB = "LSB"
CONF_DELAY = "delay"
CONF_COVERS = "covers"
CONF_GROUP = "group"
CONF_SERIAL = "serial"
CONF_REP_COUNT = "repeat_count"
CONF_REP_DELAY = "repeat_delay"
CONF_REVERSE = "reverse"

# Button codes for Jarolift commands
BUTTON_LEARN = 0xA
BUTTON_STOP = 0x4
BUTTON_UP = 0x8

# Configuration schema for YAML setup (backward compatibility)
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_REMOTE_ENTITY_ID): cv.string,
                vol.Required(CONF_MSB): cv.string,
                vol.Required(CONF_LSB): cv.string,
                vol.Optional(CONF_DELAY, default=0): vol.Coerce(int),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def bitRead(value, bit):
    return ((value) >> (bit)) & 0x01


def bitSet(value, bit):
    return (value) | (1 << (bit))


def encrypt(x, keyHigh, keyLow):
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
    packet = base64.b64encode(binascii.unhexlify(codedstring))
    return "b64:" + packet.decode("utf-8")


def ReadCounter(counter_file, serial):
    filename = counter_file + hex(serial) + ".txt"
    if os.path.isfile(filename):
        # fo = open(filename, "r")
        # Counter = int(fo.readline())
        # fo.close()
        with open(filename, encoding="utf-8") as fo:
            Counter = int(fo.readline())
        return Counter
    else:
        return 0


def WriteCounter(counter_file, serial, Counter):
    filename = counter_file + hex(serial) + ".txt"
    # _LOGGER.warning("Writing to " + filename + ": " + str(Counter) )
    # fo = open(filename, "w")
    # fo.write(str(Counter))
    # fo.close()
    with open(filename, "w", encoding="utf-8") as fo:
        fo.write(str(Counter))


def get_counter_value(counter_file, serial, call_data_counter):
    """
    Get the counter value to use for a command.
    Returns the appropriate counter based on whether a specific counter was provided.
    """
    read_counter = ReadCounter(counter_file, serial)
    provided_counter = int(call_data_counter, 16)
    if provided_counter == 0:
        return read_counter
    else:
        return provided_counter


def parse_hex_param(call_data, param_name, default_value):
    """Parse a hex parameter from call data."""
    return int(call_data.get(param_name, default_value), 16)


def send_remote_command(hass, remote_entity_id, packet):
    """Send a command via the remote entity."""
    hass.services.call(
        "remote",
        "send_command",
        {"entity_id": remote_entity_id, "command": [packet]},
    )


def _parse_hex_config_value(value: str) -> int:
    """Parse a hex configuration value to integer."""
    return int(value, 16)


def setup(hass, config):
    """Set up the Jarolift integration from YAML (backward compatibility)."""
    if DOMAIN not in config:
        return True

    # Store YAML config temporarily for migration
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["yaml_config"] = config
    hass.data[DOMAIN]["yaml_covers"] = []  # Will be populated by setup_platform

    # Trigger import flow for migration (delayed to allow covers to be registered)
    async def schedule_import_after_covers_setup():
        """Trigger import after a delay to allow cover platform setup."""
        await hass.async_block_till_done()
        await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "import"},
            data=config,
        )

    hass.add_job(schedule_import_after_covers_setup())

    # Legacy setup for backward compatibility
    domain_config = config[DOMAIN]
    remote_entity_id = domain_config[CONF_REMOTE_ENTITY_ID]
    MSB = _parse_hex_config_value(domain_config[CONF_MSB])
    LSB = _parse_hex_config_value(domain_config[CONF_LSB])
    DELAY = domain_config.get(CONF_DELAY, 0)
    counter_file = hass.config.path("counter_")

    _register_services(hass, remote_entity_id, MSB, LSB, DELAY, counter_file)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Jarolift from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Convert hex strings to integers
    msb_value = _parse_hex_config_value(entry.data[CONF_MSB])
    lsb_value = _parse_hex_config_value(entry.data[CONF_LSB])

    # Store the config entry data
    hass.data[DOMAIN][entry.entry_id] = {
        CONF_REMOTE_ENTITY_ID: entry.data[CONF_REMOTE_ENTITY_ID],
        CONF_MSB: msb_value,
        CONF_LSB: lsb_value,
        CONF_DELAY: entry.data.get(CONF_DELAY, 0),
        CONF_COVERS: entry.options.get(CONF_COVERS, []),
    }

    # Set up services
    counter_file = hass.config.path("counter_")
    _register_services(
        hass,
        entry.data[CONF_REMOTE_ENTITY_ID],
        msb_value,
        lsb_value,
        entry.data.get(CONF_DELAY, 0),
        counter_file,
    )

    # Forward the setup to the cover platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


def _register_services(hass, remote_entity_id, MSB, LSB, DELAY, counter_file):
    """Register Jarolift services."""
    # Only register services once
    if hass.services.has_service(DOMAIN, "send_raw"):
        return

    def handle_send_raw(call):
        with mutex:
            packet = call.data.get("packet", "")
            send_remote_command(hass, remote_entity_id, packet)

    def handle_send_command(call):
        Grouping = parse_hex_param(call.data, "group", "0x0001")
        Serial = parse_hex_param(call.data, "serial", "0x106aa01")
        rep_count = call.data.get("rep_count", 0)
        rep_delay = call.data.get("rep_delay", 0.2)
        Button = parse_hex_param(call.data, "button", "0x2")
        Hold = call.data.get("hold", False)
        Counter = parse_hex_param(call.data, "counter", "0x0000")

        # Mutex used so that only one cover will be set when having rep_count > 0
        with mutex:
            # We want to send at least once. so rep_count 0 means range(1)
            send_count = rep_count + 1

            if Counter == 0:
                # Use and increment the stored counter
                RCounter = ReadCounter(counter_file, Serial)
                for i in range(send_count):
                    # Build packet with incrementing counter for each transmission
                    packet = BuildPacket(
                        Grouping, Serial, Button, RCounter + i, MSB, LSB, Hold
                    )
                    _LOGGER.debug(
                        f"Sending: {Button} group: 0x{Grouping:04X} Serial: 0x{Serial:08X} counter: {RCounter + i} repeat: {i}"
                    )
                    send_remote_command(hass, remote_entity_id, packet)
                    if i < send_count - 1:
                        # Only sleep when an additional command comes afterwards
                        sleep(rep_delay)
                # Increment counter by the number of packets sent
                WriteCounter(counter_file, Serial, RCounter + send_count)
            else:
                # User provided explicit counter, send same packet multiple times
                for i in range(send_count):
                    packet = BuildPacket(
                        Grouping, Serial, Button, Counter, MSB, LSB, Hold
                    )
                    _LOGGER.debug(
                        f"Sending: {Button} group: 0x{Grouping:04X} Serial: 0x{Serial:08X} counter: {Counter} repeat: {i}"
                    )
                    send_remote_command(hass, remote_entity_id, packet)
                    if i < send_count - 1:
                        # Only sleep when an additional command comes afterwards
                        sleep(rep_delay)

            # This is the minimum delay between multiple different covers
            sleep(DELAY)

    def handle_learn(call):
        Grouping = parse_hex_param(call.data, "group", "0x0001")
        Serial = parse_hex_param(call.data, "serial", "0x106aa01")
        Counter = parse_hex_param(call.data, "counter", "0x0000")
        UsedCounter = get_counter_value(
            counter_file, Serial, call.data.get("counter", "0x0000")
        )
        packet = BuildPacket(
            Grouping, Serial, BUTTON_LEARN, UsedCounter, MSB, LSB, False
        )

        with mutex:
            send_remote_command(hass, remote_entity_id, packet)
            sleep(1)
            packet = BuildPacket(
                Grouping, Serial, BUTTON_STOP, UsedCounter + 1, MSB, LSB, False
            )
            send_remote_command(hass, remote_entity_id, packet)
            if Counter == 0:
                RCounter = ReadCounter(counter_file, Serial)
                WriteCounter(counter_file, Serial, RCounter + 2)

    def handle_clear(call):
        Grouping = parse_hex_param(call.data, "group", "0x0001")
        Serial = parse_hex_param(call.data, "serial", "0x106aa01")
        Counter = parse_hex_param(call.data, "counter", "0x0000")
        UsedCounter = get_counter_value(
            counter_file, Serial, call.data.get("counter", "0x0000")
        )
        packet = BuildPacket(
            Grouping, Serial, BUTTON_LEARN, UsedCounter, MSB, LSB, False
        )

        with mutex:
            send_remote_command(hass, remote_entity_id, packet)
            sleep(1)
            for i in range(0, 6):
                packet = BuildPacket(
                    Grouping, Serial, BUTTON_STOP, UsedCounter + 1 + i, MSB, LSB, False
                )
                send_remote_command(hass, remote_entity_id, packet)
                sleep(0.5)
            sleep(1)
            packet = BuildPacket(
                Grouping, Serial, BUTTON_UP, UsedCounter + 7, MSB, LSB, False
            )
            send_remote_command(hass, remote_entity_id, packet)
            if Counter == 0:
                RCounter = ReadCounter(counter_file, Serial)
                WriteCounter(counter_file, Serial, RCounter + 8)

    hass.services.register(DOMAIN, "send_raw", handle_send_raw)
    hass.services.register(DOMAIN, "send_command", handle_send_command)
    hass.services.register(DOMAIN, "learn", handle_learn)
    hass.services.register(DOMAIN, "clear", handle_clear)

    return True
