# Import necessary modules
from canlib import canlib, Frame
import time

def sdo_read_access(channel, node_id, index, subindex, timeout_ms):
    """
    Sends an SDO read request and waits for the response.
    
    :param channel: The CAN channel object.
    :param node_id: The node ID of the target device.
    :param index: The index of the object to read.
    :param subindex: The subindex of the object to read.
    :param timeout_ms: Timeout in milliseconds.
    :return: Data read from the device.
    """
    cob_id = 0x600 + node_id
    sdo_command = 0x40  # Read command
    sdo_data = [sdo_command, index & 0xFF, (index >> 8) & 0xFF, subindex, 0, 0, 0, 0]

    # Create and send the read request
    frame = Frame(id_=cob_id, data=sdo_data, flags=canlib.canMSG_STD)
    try:
        channel.write(frame)
        print(f"Sent SDO Read Access: Index {hex(index)}, Subindex {hex(subindex)}")

        # Wait for the response
        end_time = time.time() + (timeout_ms / 1000)
        while time.time() < end_time:
            try:
                response = channel.read(timeout=1000)
                if response.id == (cob_id - 0x80):  # Check for matching response ID
                    data = int.from_bytes(response.data[4:], byteorder='little')
                    print(f"Received Data: {data}")
                    return data
            except canlib.CanNoMsg:
                continue
            except canlib.CanlibException as e:
                print(f"Error reading SDO response: {e}")
                break
    except canlib.CanlibException as e:
        print(f"Failed to send SDO read: {e}")

    print("Timeout waiting for SDO response.")
    return None

def sdo_write_access(channel, node_id, index, subindex, data, timeout_ms):
    """
    Sends an SDO write request to the specified node.
    
    :param channel: The CAN channel object.
    :param node_id: The node ID of the target device.
    :param index: The index of the object to write to.
    :param subindex: The subindex of the object to write to.
    :param data: The data to write.
    :param timeout_ms: Timeout in milliseconds.
    """
    cob_id = 0x600 + node_id  # COB-ID for SDO request
    sdo_command = 0x2B  # Write 2 bytes (0x2B for 2 bytes, 0x23 for 4 bytes, adjust if needed)
    sdo_data = [sdo_command, index & 0xFF, (index >> 8) & 0xFF, subindex, data & 0xFF, (data >> 8) & 0xFF, 0, 0]

    # Create and send the CAN frame
    frame = Frame(id_=cob_id, data=sdo_data, flags=canlib.canMSG_STD)
    try:
        channel.write(frame)
        print(f"Sent SDO Write Access: Index {hex(index)}, Subindex {hex(subindex)}, Data {data}")
    except canlib.CanlibException as e:
        print(f"Failed to send SDO write: {e}")

def enable_drive(channel, node_id, timeout_ms):
    """
    Enables the drive by sending the required commands.
    
    :param channel: The CAN channel object.
    :param node_id: The node ID of the drive.
    :param timeout_ms: Timeout for communication in milliseconds.
    """
    sleep_time_after_transmission = 1  # 1 second
    
    # Check for errors and try to clear the fault
    read_data = sdo_read_access(channel, node_id, 0x6041, 0x00, timeout_ms)
    if read_data is not None:
        # Check if status word reports a fault
        if (read_data & 0x0000004F) == 0x0000000F:
            print("Enable not possible since Drive in fault reaction active state!")
        elif (read_data & 0x0000004F) == 0x00000008:
            # Issue fault reset command, transition T15
            print("Issuing fault reset command...")
            sdo_write_access(channel, node_id, 0x6040, 0x00, 0x80, timeout_ms)
            time.sleep(sleep_time_after_transmission)
            read_data = sdo_read_access(channel, node_id, 0x6041, 0x00, timeout_ms)
            if (read_data & 0x0000004F) != 0x00000040:
                print("A pending fault could not be cleared!")

    # Continue with enabling sequence
    commands = [
        (0x00, "disable voltage command"),
        (0x06, "shutdown command"),
        (0x07, "switch on command"),
        (0x0F, "switch on and enable command"),
    ]

    for command, description in commands:
        print(f"Issuing {description}...")
        sdo_write_access(channel, node_id, 0x6040, 0x00, command, timeout_ms)
        time.sleep(sleep_time_after_transmission)
        read_data = sdo_read_access(channel, node_id, 0x6041, 0x00, timeout_ms)

    print("Drive enabled successfully.")

def disable_drive(channel, node_id, timeout_ms):
    """
    Disables the drive by sending the required commands.
    
    :param channel: The CAN channel object.
    :param node_id: The node ID of the drive.
    :param timeout_ms: Timeout for communication in milliseconds.
    """
    sleep_time_after_transmission = 1  # 1 second

    # Check for errors and try to clear the fault
    read_data = sdo_read_access(channel, node_id, 0x6041, 0x00, timeout_ms)
    if read_data is not None:
        # Check if status word reports a fault
        if (read_data & 0x0000004F) == 0x0000000F:
            print("Disable not possible since Drive in fault reaction active state!")
        elif (read_data & 0x0000004F) == 0x00000008:
            # Issue fault reset command, transition T15
            print("Issuing fault reset command...")
            sdo_write_access(channel, node_id, 0x6040, 0x00, 0x80, timeout_ms)
            time.sleep(sleep_time_after_transmission)
            read_data = sdo_read_access(channel, node_id, 0x6041, 0x00, timeout_ms)
            if (read_data & 0x0000004F) != 0x00000040:
                print("A pending fault could not be cleared!")

    # Issue disable voltage command, Transition T9
    print("Issuing disable voltage command...")
    sdo_write_access(channel, node_id, 0x6040, 0x00, 0x00, timeout_ms)
    time.sleep(sleep_time_after_transmission)
    read_data = sdo_read_access(channel, node_id, 0x6041, 0x00, timeout_ms)
    if read_data is not None and (read_data & 0x0000004F) != 0x00000040:
        print("Wrong status word value!")

    time.sleep(sleep_time_after_transmission)
    print("Drive disabled successfully.")

def set_cia402_mode_of_operation(channel, node_id, mode, timeout_ms):
    """
    Sets the CiA402 mode of operation for the motor.
    
    :param channel: The CAN channel object.
    :param node_id: The node ID of the motor.
    :param mode: Mode value to set (e.g., 3 for Profile Velocity).
    :param timeout_ms: Timeout for communication in milliseconds.
    """
    print(f"Setting CiA402 mode of operation to {mode} (Profile Velocity)...")
    sdo_write_access(channel, node_id, 0x6060, 0x00, mode, timeout_ms)

def move_motor_in_profile_velocity(channel, node_id, speed, accel, decel, disable_after_motion, movement_duration, timeout_ms):
    """
    Moves the motor in profile velocity mode with specified speed, acceleration, and deceleration.
    
    :param channel: The CAN channel object.
    :param node_id: The node ID of the drive.
    :param speed: Speed in CAN units.
    :param accel: Acceleration in CAN units.
    :param decel: Deceleration in CAN units.
    :param disable_after_motion: Boolean to disable drive after motion.
    :param movement_duration: Duration of movement in seconds.
    :param timeout_ms: Timeout for communication in milliseconds.
    """
    # Read current acceleration and deceleration settings
    current_accel = sdo_read_access(channel, node_id, 0x6083, 0x00, timeout_ms)
    current_decel = sdo_read_access(channel, node_id, 0x6084, 0x00, timeout_ms)

    # Check if the settings need to be updated
    if current_accel != accel or current_decel != decel:
        disable_drive(channel, node_id, timeout_ms)
        sdo_write_access(channel, node_id, 0x6083, 0x00, accel, timeout_ms)  # Set acceleration
        sdo_write_access(channel, node_id, 0x6084, 0x00, decel, timeout_ms)  # Set deceleration

    # Check and set mode of operation to profile velocity
    mode_of_operation = sdo_read_access(channel, node_id, 0x6061, 0x00, timeout_ms)
    if mode_of_operation != 3:
        disable_drive(channel, node_id, timeout_ms)
        set_cia402_mode_of_operation(channel, node_id, 3, timeout_ms)  # Set mode to profile velocity
        enable_drive(channel, node_id, timeout_ms)

    # Read status word and enable drive if not already enabled
    status_word = sdo_read_access(channel, node_id, 0x6041, 0x00, timeout_ms)
    if status_word is None or (status_word & 0x0000006F) != 0x00000027:
        enable_drive(channel, node_id, timeout_ms)

    # Set velocity
    print(f"Setting speed to {speed}...")
    sdo_write_access(channel, node_id, 0x60FF, 0x00, speed, timeout_ms)  # Set velocity

    # Fetch messages during movement
    if movement_duration > 0:
        print(f"Moving for {movement_duration} seconds...")
        fetch_telegrams(channel, movement_duration)

    # Optionally disable after motion
    if disable_after_motion:
        disable_drive(channel, node_id, timeout_ms)

def fetch_telegrams(channel, duration_seconds):
    """
    Fetches CAN frames from the bus and checks for heartbeat messages.

    :param channel: The CAN channel object.
    :param duration_seconds: Duration in seconds to fetch messages.
    :return: None
    """
    end_time = time.time() + duration_seconds
    received_heartbeat_count = 0

    print(f"Fetching CAN messages for {duration_seconds} seconds...")

    while time.time() < end_time:
        try:
            # Read a frame from the CAN bus
            frame = channel.read(timeout=1000)
            # Check for heartbeat frames; adjust based on specific heartbeat structure (node ID + 0x700)
            if frame.id == 0x700 + 127:  # Check if it's a heartbeat message from node 127
                print(f"Received heartbeat from node {frame.id - 0x700}")
                received_heartbeat_count += 1

        except canlib.CanNoMsg:
            continue  # No message received within the timeout
        except canlib.CanlibException as e:
            print(f"Error fetching message: {e}")

    print(f"Total heartbeat messages received: {received_heartbeat_count}")

if __name__ == "__main__":
    # Open the channel with bitrate 1M
    channel = canlib.openChannel(0, canlib.canOPEN_ACCEPT_VIRTUAL)
    channel.setBusParams(canlib.canBITRATE_1M)
    channel.busOn()

    try:
        # Move motor with given parameters
        move_motor_in_profile_velocity(
            channel=channel,
            node_id=127,
            speed=800,  # Example speed in CAN units
            accel=1000,  # Example acceleration
            decel=1000,  # Example deceleration
            disable_after_motion=True,
            movement_duration=15,  # Move for 15 seconds
            timeout_ms=1000
        )
    finally:
        # Properly close the channel
        channel.busOff()
        channel.close()
