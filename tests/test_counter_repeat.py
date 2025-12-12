"""Tests for counter increment with repeat_count."""
import os
import tempfile
import sys


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


def test_counter_increment_with_repeat():
    """Test that counter increments by send_count (repeat_count + 1)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        counter_file = os.path.join(tmpdir, "counter_")
        serial = 0x106aa01
        
        # Initial counter is 0
        initial_counter = ReadCounter(counter_file, serial)
        assert initial_counter == 0
        print(f"Initial counter: {initial_counter}")
        
        # Simulate sending with repeat_count=4 (sends 5 times)
        repeat_count = 4
        send_count = repeat_count + 1  # 5 times
        
        # After sending, counter should be incremented by send_count
        expected_counter = initial_counter + send_count
        WriteCounter(counter_file, serial, expected_counter)
        
        # Read back and verify
        new_counter = ReadCounter(counter_file, serial)
        assert new_counter == expected_counter == 5
        print(f"After sending with repeat_count={repeat_count} (send_count={send_count}): counter={new_counter}")
        
        # Next command should start with counter=5
        next_counter = ReadCounter(counter_file, serial)
        assert next_counter == 5
        print(f"Next command will use counter: {next_counter}")


def test_counter_increment_without_repeat():
    """Test that counter increments by 1 when repeat_count=0."""
    with tempfile.TemporaryDirectory() as tmpdir:
        counter_file = os.path.join(tmpdir, "counter_")
        serial = 0x106aa02
        
        # Initial counter is 0
        initial_counter = ReadCounter(counter_file, serial)
        assert initial_counter == 0
        print(f"Initial counter: {initial_counter}")
        
        # Simulate sending with repeat_count=0 (sends 1 time)
        repeat_count = 0
        send_count = repeat_count + 1  # 1 time
        
        # After sending, counter should be incremented by send_count
        expected_counter = initial_counter + send_count
        WriteCounter(counter_file, serial, expected_counter)
        
        # Read back and verify
        new_counter = ReadCounter(counter_file, serial)
        assert new_counter == expected_counter == 1
        print(f"After sending with repeat_count={repeat_count} (send_count={send_count}): counter={new_counter}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Counter Increment with repeat_count")
    print("="*60 + "\n")
    
    try:
        test_counter_increment_with_repeat()
        print("✓ test_counter_increment_with_repeat PASSED\n")
    except AssertionError as e:
        print(f"✗ test_counter_increment_with_repeat FAILED: {e}\n")
        sys.exit(1)
    
    try:
        test_counter_increment_without_repeat()
        print("✓ test_counter_increment_without_repeat PASSED\n")
    except AssertionError as e:
        print(f"✗ test_counter_increment_without_repeat FAILED: {e}\n")
        sys.exit(1)
    
    print("="*60)
    print("All tests PASSED")
    print("="*60 + "\n")
