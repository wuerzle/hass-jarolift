# Fix for Counter Increment Issue with repeat_count

## Problem Description

When using the `repeat_count` parameter (e.g., `repeat_count: 4`), users experienced a desynchronization issue where after operating one cover, they needed to press the button multiple times on other covers before they would respond.

### Root Cause

The issue was in the `handle_send_command` function in `__init__.py`. The code was:

1. Reading the current counter value (e.g., 0)
2. Building a **single packet** with that counter value
3. Incrementing the counter by **1** in the file (counter = 1)
4. Sending the **same packet** multiple times (repeat_count + 1 times)

For example, with `repeat_count=4`:
- Counter file: 0
- Packet built with counter=0
- Counter file updated to: 1
- Same packet (counter=0) sent **5 times**

### Why This Caused the Issue

Jarolift covers use KeeLoq encryption, which requires each transmission to have a **unique, incrementing counter** for security (to prevent replay attacks). When the cover received:

- 5 packets with counter=0, it accepted each one but expected counters 0, 1, 2, 3, 4
- The counter file only showed counter=1 (incremented by 1, not 5)
- Next command tried to use counter=1, but the cover expected counter=5
- Difference: 4 presses needed to catch up

This matches the user's report: "when pressing wohnzimmer1 opening the shutter i have to press 4 times for the next functional operation on all other shutters."

## Solution

The fix ensures that **each repeated transmission uses a unique, incrementing counter**:

1. Read the current counter value (e.g., 0)
2. For each transmission (repeat_count + 1):
   - Build a packet with counter = base_counter + i (0, 1, 2, 3, 4)
   - Send that unique packet
3. Increment the counter file by the total number of packets sent (send_count = 5)

### Code Changes

**Before:**
```python
RCounter = ReadCounter(counter_file, Serial)
Counter = parse_hex_param(call.data, "counter", "0x0000")
if Counter == 0:
    packet = BuildPacket(Grouping, Serial, Button, RCounter, MSB, LSB, Hold)
    WriteCounter(counter_file, Serial, RCounter + 1)
else:
    packet = BuildPacket(Grouping, Serial, Button, Counter, MSB, LSB, Hold)

with mutex:
    send_count = rep_count + 1
    for i in range(send_count):
        send_remote_command(hass, remote_entity_id, packet)
        if i < send_count - 1:
            sleep(rep_delay)
    sleep(DELAY)
```

**After:**
```python
with mutex:
    send_count = rep_count + 1
    
    if Counter == 0:
        RCounter = ReadCounter(counter_file, Serial)
        for i in range(send_count):
            # Build packet with incrementing counter for each transmission
            packet = BuildPacket(Grouping, Serial, Button, RCounter + i, MSB, LSB, Hold)
            send_remote_command(hass, remote_entity_id, packet)
            if i < send_count - 1:
                sleep(rep_delay)
        # Increment counter by the number of packets sent
        WriteCounter(counter_file, Serial, RCounter + send_count)
    else:
        # User provided explicit counter, send same packet multiple times
        for i in range(send_count):
            packet = BuildPacket(Grouping, Serial, Button, Counter, MSB, LSB, Hold)
            send_remote_command(hass, remote_entity_id, packet)
            if i < send_count - 1:
                sleep(rep_delay)
    
    sleep(DELAY)
```

## Validation

This fix aligns with the existing behavior in other functions:

1. **`handle_learn`** sends 2 commands with counters `UsedCounter` and `UsedCounter + 1`, then increments by 2
2. **`handle_clear`** sends 8 commands with incrementing counters `UsedCounter + 0` through `UsedCounter + 7`, then increments by 8

### Testing

New test added in `tests/test_counter_repeat.py` to verify:
- With `repeat_count=4` (5 transmissions), counter increments by 5
- With `repeat_count=0` (1 transmission), counter increments by 1

## User Impact

After this fix:
- Users with `repeat_count > 0` will no longer experience desynchronization
- Covers will respond immediately to commands without needing multiple button presses
- Counter files will correctly reflect the number of packets actually sent
- Each transmission uses a unique counter, maintaining KeeLoq security

## Example Scenario

**User Configuration:**
```yaml
cover:
  - platform: jarolift
    covers:
      - name: 'Wohnzimmer1'
        serial: '0x106aa01'
        repeat_count: 4
```

**Before Fix:**
1. Press Wohnzimmer1 → Counter: 0→1, Sent: 5 packets (counter=0)
2. Press Wohnzimmer1 → Counter: 1→2, Sent: 5 packets (counter=1)
3. Cover expects counter=10, file shows counter=2
4. Need 8 more presses to sync

**After Fix:**
1. Press Wohnzimmer1 → Counter: 0→5, Sent: 5 packets (counter=0,1,2,3,4)
2. Press Wohnzimmer1 → Counter: 5→10, Sent: 5 packets (counter=5,6,7,8,9)
3. Cover and file stay in sync ✓
4. No extra presses needed ✓
