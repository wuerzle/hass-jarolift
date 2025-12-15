"""Jarolift Home Assistant Integration.

This integration provides support for Jarolift motorized covers (blinds/shutters)
by adding KeeLoq encryption to commands sent via an RF remote entity (e.g., Broadlink).

The integration:
- Encrypts commands using the proprietary KeeLoq algorithm
- Manages rolling counters for replay attack prevention
- Supports multiple covers with individual configurations
- Provides services for learning and controlling covers

For more information, see: https://github.com/wuerzle/hass-jarolift
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
from homeassistant.helpers import device_registry as dr

DOMAIN = "jarolift"
_LOGGER = logging.getLogger(__name__)
mutex = threading.Lock()

PLATFORMS = [Platform.COVER, Platform.BUTTON]

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

# Device information constants
DEVICE_NAME = "Jarolift"
DEVICE_MANUFACTURER = "Jarolift"
DEVICE_MODEL = "KeeLoq RF Controller"
DEVICE_SW_VERSION = "2.0.5"

# Button codes for Jarolift commands
BUTTON_LEARN = 0xA
BUTTON_STOP = 0x4
BUTTON_UP = 0x8

# KeeLoq packet building constants
KEELOQ_KEY_LOW_MASK = 0x20000000
KEELOQ_KEY_HIGH_MASK = 0x60000000
KEELOQ_PACKET_BITS = 72
KEELOQ_PREAMBLE = "190c1a0001e4310c0d0c0d0c0d0c0d0c0d0c0d0c0d0c0d7a"
KEELOQ_BIT_ONE_LAST = "0c0005dc"
KEELOQ_BIT_ZERO_LAST = "190005dc"
KEELOQ_BIT_ONE = "0c19"
KEELOQ_BIT_ZERO = "190c"
KEELOQ_HOLD_PREFIX = "b214"
KEELOQ_NORMAL_PREFIX = "b200"

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


def bitRead(value: int, bit: int) -> int:
    """Read a specific bit from a value."""
    return ((value) >> (bit)) & 0x01


def bitSet(value: int, bit: int) -> int:
    """Set a specific bit in a value."""
    return (value) | (1 << (bit))


def encrypt(x: int, keyHigh: int, keyLow: int) -> int:
    """Encrypt a value using the KeeLoq algorithm.

    KeeLoq is a proprietary cipher used in RF remote controls. This implementation
    performs 528 rounds of encryption using a 64-bit key and a non-linear function.

    Args:
        x: 32-bit value to encrypt
        keyHigh: High 32 bits of the 64-bit key
        keyLow: Low 32 bits of the 64-bit key

    Returns:
        Encrypted 32-bit value
    """
    KeeLoq_NLF = 0x3A5C742E  # Non-linear function lookup table
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


def decrypt(x: int, keyHigh: int, keyLow: int) -> int:
    """Decrypt a value using the KeeLoq algorithm.

    This is the inverse operation of the encrypt function, performing 528 rounds
    of decryption in reverse order.

    Args:
        x: 32-bit value to decrypt
        keyHigh: High 32 bits of the 64-bit key
        keyLow: Low 32 bits of the 64-bit key

    Returns:
        Decrypted 32-bit value
    """
    KeeLoq_NLF = 0x3A5C742E  # Non-linear function lookup table
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


def BuildPacket(
    Grouping: int,
    Serial: int,
    Button: int,
    Counter: int,
    MSB: int,
    LSB: int,
    Hold: bool,
) -> str:
    """Build a KeeLoq encrypted packet for RF transmission.

    This function creates a complete packet that can be sent to a Jarolift cover:
    1. Derives device-specific keys from the serial number
    2. Encrypts the counter and device information using KeeLoq
    3. Assembles the complete 72-bit packet
    4. Encodes it in the Jarolift RF format
    5. Returns a base64-encoded string for transmission

    Args:
        Grouping: Group number for the cover (0x0000-0xFFFF)
        Serial: Serial number of the cover (unique identifier)
        Button: Button code (0x2=down, 0x4=stop, 0x8=up, 0xA=learn)
        Counter: Rolling counter value for replay protection
        MSB: Manufacturer key (high 32 bits)
        LSB: Manufacturer key (low 32 bits)
        Hold: If True, button is held down (for programming)

    Returns:
        Base64-encoded packet string prefixed with "b64:"
    """
    # Generate device keys from serial
    keylow = Serial | KEELOQ_KEY_LOW_MASK
    keyhigh = Serial | KEELOQ_KEY_HIGH_MASK
    KeyLSB = decrypt(keylow, MSB, LSB)
    KeyMSB = decrypt(keyhigh, MSB, LSB)

    # Build the decoded packet with counter, serial, and grouping
    Decoded = Counter | ((Serial & 0xFF) << 16) | ((Grouping & 0xFF) << 24)
    Encoded = encrypt(Decoded, KeyMSB, KeyLSB)

    # Assemble the complete data packet
    data = Encoded | (Serial << 32) | (Button << 60) | (((Grouping >> 8) & 0xFF) << 64)

    # Convert to binary string and encode
    datastring = bin(data)[2:].zfill(KEELOQ_PACKET_BITS)[::-1]
    codedstring = _encode_keeloq_bits(datastring)

    # Add preamble and packet wrapper
    codedstring = KEELOQ_PREAMBLE + codedstring
    packet_prefix = KEELOQ_HOLD_PREFIX if Hold else KEELOQ_NORMAL_PREFIX
    packet_length = hex(len(codedstring) // 2)[2:]
    codedstring = packet_prefix + packet_length + "00" + codedstring

    # Encode to base64
    packet = base64.b64encode(binascii.unhexlify(codedstring))
    return "b64:" + packet.decode("utf-8")


def _encode_keeloq_bits(datastring: str) -> str:
    """Encode a binary string into KeeLoq format.

    Args:
        datastring: Binary string to encode

    Returns:
        Hex-encoded string in KeeLoq format
    """
    codedstring = ""
    last_bit_index = len(datastring) - 1

    for i, bit in enumerate(datastring):
        is_last_bit = i == last_bit_index
        is_one = bit == "1"

        if is_last_bit:
            codedstring += KEELOQ_BIT_ONE_LAST if is_one else KEELOQ_BIT_ZERO_LAST
        else:
            codedstring += KEELOQ_BIT_ONE if is_one else KEELOQ_BIT_ZERO

    return codedstring


def ReadCounter(counter_file: str, serial: int) -> int:
    """Read the counter value for a serial from file.

    Args:
        counter_file: Base path for counter files
        serial: Serial number of the device

    Returns:
        Current counter value, or 0 if file doesn't exist
    """
    filename = f"{counter_file}{hex(serial)}.txt"
    if os.path.isfile(filename):
        with open(filename, encoding="utf-8") as fo:
            return int(fo.readline().strip())
    return 0


def WriteCounter(counter_file: str, serial: int, Counter: int) -> None:
    """Write the counter value for a serial to file.

    Args:
        counter_file: Base path for counter files
        serial: Serial number of the device
        Counter: Counter value to write
    """
    filename = f"{counter_file}{hex(serial)}.txt"
    with open(filename, "w", encoding="utf-8") as fo:
        fo.write(str(Counter))


def get_counter_value(counter_file: str, serial: int, call_data_counter: str) -> int:
    """
    Get the counter value to use for a command.
    Returns the appropriate counter based on whether a specific counter was provided.
    """
    provided_counter = int(call_data_counter, 16)
    return (
        ReadCounter(counter_file, serial) if provided_counter == 0 else provided_counter
    )


def parse_hex_param(call_data: dict, param_name: str, default_value: str) -> int:
    """Parse a hex parameter from call data."""
    return int(call_data.get(param_name, default_value), 16)


def send_remote_command(
    hass: HomeAssistant, remote_entity_id: str, packet: str
) -> None:
    """Send a command via the remote entity."""
    hass.services.call(
        "remote",
        "send_command",
        {"entity_id": remote_entity_id, "command": [packet]},
    )


def _send_packets_with_counter(
    hass: HomeAssistant,
    remote_entity_id: str,
    counter_file: str,
    Grouping: int,
    Serial: int,
    Button: int,
    Counter: int,
    MSB: int,
    LSB: int,
    Hold: bool,
    send_count: int,
    rep_delay: float,
) -> None:
    """Send packets with automatic counter management.

    Args:
        hass: Home Assistant instance
        remote_entity_id: Remote entity to use for transmission
        counter_file: Base path for counter files
        Grouping: Device group
        Serial: Device serial
        Button: Button code to send
        Counter: Counter value (0 for auto-increment)
        MSB: Manufacturer key MSB
        LSB: Manufacturer key LSB
        Hold: Whether to hold the button
        send_count: Number of times to send the packet
        rep_delay: Delay between repeated sends
    """
    if Counter == 0:
        # Use and increment the stored counter
        base_counter = ReadCounter(counter_file, Serial)
        for i in range(send_count):
            packet = BuildPacket(
                Grouping, Serial, Button, base_counter + i, MSB, LSB, Hold
            )
            _LOGGER.debug(
                f"Sending: {Button} group: 0x{Grouping:04X} Serial: 0x{Serial:08X} counter: {base_counter + i} repeat: {i}"
            )
            send_remote_command(hass, remote_entity_id, packet)
            if i < send_count - 1:
                sleep(rep_delay)
        WriteCounter(counter_file, Serial, base_counter + send_count)
    else:
        # User provided explicit counter, send same packet multiple times
        for i in range(send_count):
            packet = BuildPacket(Grouping, Serial, Button, Counter, MSB, LSB, Hold)
            _LOGGER.debug(
                f"Sending: {Button} group: 0x{Grouping:04X} Serial: 0x{Serial:08X} counter: {Counter} repeat: {i}"
            )
            send_remote_command(hass, remote_entity_id, packet)
            if i < send_count - 1:
                sleep(rep_delay)


def _parse_hex_config_value(value: str) -> int:
    """Parse a hex configuration value to integer."""
    return int(value, 16)


def _has_config_entry(hass) -> bool:
    """Check if integration is already configured via config entry (UI)."""
    return bool(hass.config_entries.async_entries(DOMAIN))


def setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Jarolift integration from YAML (backward compatibility)."""
    if DOMAIN not in config:
        return True

    # Check if already configured via config entry (migration already done)
    if _has_config_entry(hass):
        _LOGGER.info(
            "Jarolift is already configured via UI. YAML configuration is ignored. "
            "Please remove jarolift from configuration.yaml."
        )
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

    hass.async_create_task(
        _register_services(hass, remote_entity_id, MSB, LSB, DELAY, counter_file)
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Jarolift from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Convert hex strings to integers
    msb_value = _parse_hex_config_value(entry.data[CONF_MSB])
    lsb_value = _parse_hex_config_value(entry.data[CONF_LSB])

    # Register the hub device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name=DEVICE_NAME,
        manufacturer=DEVICE_MANUFACTURER,
        model=DEVICE_MODEL,
        sw_version=DEVICE_SW_VERSION,
    )

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
    await _register_services(
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


async def _register_services(
    hass: HomeAssistant,
    remote_entity_id: str,
    MSB: int,
    LSB: int,
    DELAY: int,
    counter_file: str,
) -> bool:
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
            # We want to send at least once, so rep_count 0 means send once
            send_count = rep_count + 1
            _send_packets_with_counter(
                hass,
                remote_entity_id,
                counter_file,
                Grouping,
                Serial,
                Button,
                Counter,
                MSB,
                LSB,
                Hold,
                send_count,
                rep_delay,
            )
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

    hass.services.async_register(DOMAIN, "send_raw", handle_send_raw)
    hass.services.async_register(DOMAIN, "send_command", handle_send_command)
    hass.services.async_register(DOMAIN, "learn", handle_learn)
    hass.services.async_register(DOMAIN, "clear", handle_clear)

    return True
