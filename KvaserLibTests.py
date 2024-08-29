# Import functions from KvaserLib
from KvaserLib import (
    open_channel,
    enable_drive,
    disable_drive,
    set_cia402_mode_of_operation,
    move_motor_in_profile_velocity,
    sdo_write_access,
    sdo_read_access
)
import time

# Configuration settings
NODE_ID = 127  # Example node ID for testing
TIMEOUT_MS = 1000  # Timeout in milliseconds

def test_velocity_profile(channel):
    """
    Test moving the motor in profile velocity mode.
    """
    print("\nTesting Profile Velocity Mode...")

    # Set the drive to Profile Velocity Mode (3)
    set_cia402_mode_of_operation(channel, NODE_ID, 3, TIMEOUT_MS)

    # Enable the drive
    enable_drive(channel, NODE_ID, TIMEOUT_MS)

    # Move motor in profile velocity with test parameters
    move_motor_in_profile_velocity(
        channel=channel,
        node_id=NODE_ID,
        speed=1000,  # Set desired speed in CAN units
        accel=2000,  # Acceleration in CAN units
        decel=2000,  # Deceleration in CAN units
        disable_after_motion=True,
        movement_duration=5,  # Movement duration in seconds
        timeout_ms=TIMEOUT_MS
    )

def test_position_profile(channel):
    """
    Test moving the motor in profile position mode.
    """
    print("\nTesting Profile Position Mode...")

    # Set the drive to Profile Position Mode (1)
    set_cia402_mode_of_operation(channel, NODE_ID, 1, TIMEOUT_MS)

    # Enable the drive
    enable_drive(channel, NODE_ID, TIMEOUT_MS)

    # Set target position (index 0x607A)
    target_position = 50000  # Example target position
    sdo_write_access(channel, NODE_ID, 0x607A, 0x00, target_position, TIMEOUT_MS)
    print(f"Setting target position to {target_position}")

    # Set controlword to execute motion (index 0x6040, subindex 0x00)
    sdo_write_access(channel, NODE_ID, 0x6040, 0x00, 0x003F, TIMEOUT_MS)
    print("Executing motion command...")

    # Wait for the motion to complete
    time.sleep(5)

    # Disable the drive after test
    disable_drive(channel, NODE_ID, TIMEOUT_MS)

def test_current_profile(channel):
    """
    Test controlling the motor in profile current mode.
    """
    print("\nTesting Profile Current Mode...")

    # Set the drive to Profile Current Mode (6)
    set_cia402_mode_of_operation(channel, NODE_ID, 6, TIMEOUT_MS)

    # Enable the drive
    enable_drive(channel, NODE_ID, TIMEOUT_MS)

    # Set target current (index 0x2030, subindex 0x00) - Example
    target_current = 200  # Example current value in CAN units
    sdo_write_access(channel, NODE_ID, 0x2030, 0x00, target_current, TIMEOUT_MS)
    print(f"Setting target current to {target_current}")

    # Wait to observe the current effect
    time.sleep(5)

    # Disable the drive after test
    disable_drive(channel, NODE_ID, TIMEOUT_MS)

def test_torque_profile(channel):
    """
    Test controlling the motor in profile torque mode.
    """
    print("\nTesting Profile Torque Mode...")

    # Set the drive to Profile Torque Mode (4)
    set_cia402_mode_of_operation(channel, NODE_ID, 4, TIMEOUT_MS)

    # Enable the drive
    enable_drive(channel, NODE_ID, TIMEOUT_MS)

    # Set target torque (index 0x6071, subindex 0x00) - Example
    target_torque = 300  # Example torque value in CAN units
    sdo_write_access(channel, NODE_ID, 0x6071, 0x00, target_torque, TIMEOUT_MS)
    print(f"Setting target torque to {target_torque}")

    # Wait to observe the torque effect
    time.sleep(5)

    # Disable the drive after test
    disable_drive(channel, NODE_ID, TIMEOUT_MS)

def main():
    # Open the CAN channel
    channel = open_channel(0)  # Adjust the channel index if necessary
    if channel is None:
        print("Failed to open the channel. Exiting.")
        return

    try:
        # Run tests
        test_velocity_profile(channel)
        test_position_profile(channel)
        test_current_profile(channel)
        test_torque_profile(channel)

    finally:
        # Close the channel properly
        channel.busOff()
        channel.close()
        print("Channel closed successfully.")

if __name__ == "__main__":
    main()
