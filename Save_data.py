import asyncio
import os
from bleak import BleakClient
from datetime import datetime

# BLE Device Address
DEVICE_ADDRESS = "C9:6D:69:38:E7:03"

# UUIDs for Read (Notify) and Write characteristics
WRITE_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
READ_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

# Storage parameters
SAVE_FOLDER = r"C:\Users\User\Documents\RobotRead"
SAVE_FILENAME = "BLE_Readings.txt"
FILE_PATH = os.path.join(SAVE_FOLDER, SAVE_FILENAME)

# Data storage
received_data = []
full_messages = []
MAX_MESSAGES = 30  # Save exactly 30 messages per file
collecting_data = False  # Flag to track if we should collect messages

# Ensure folder exists
os.makedirs(SAVE_FOLDER, exist_ok=True)

def notification_handler(sender, data):
    """Handles BLE notifications and stores data only when collecting_data is True."""
    global received_data, full_messages, collecting_data

    if not collecting_data:
        return  # Ignore messages when not in collection mode

    text = data.decode("utf-8")  # Convert bytes to string
    received_data.append(text)  # Store fragment

    # Detect full message (assuming newline "\n" or known ending like ";GMWIN:")
    if "\n" in text or text.endswith(";GMWIN:"):
        full_message = "".join(received_data).strip()
        full_messages.append(full_message)
        
        # Show the current count
        print(f"\n📥 Message {len(full_messages)} received: {full_message}\n> ")

        received_data.clear()  # Reset buffer

        # If 30 messages are stored, write to file and stop collecting
        if len(full_messages) >= MAX_MESSAGES:
            save_to_file()
            full_messages.clear()  # Reset buffer after saving
            collecting_data = False  # Stop collecting until "save" is typed again

def save_to_file():
    """Saves exactly 30 readings to a file and stops data collection."""
    if len(full_messages) < MAX_MESSAGES:
        print("\n⚠️ Not enough messages collected yet (need 30).\n")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"BLE_Readings_{timestamp}.txt"
    file_path = os.path.join(SAVE_FOLDER, file_name)

    with open(file_path, "w", encoding="utf-8") as file:
        for msg in full_messages:
            file.write(msg + "\n")

    print(f"\n✅ Data saved to: {file_path}\n")

async def receive_notifications(client):
    """ Continuously listens for BLE notifications. """
    await client.start_notify(READ_CHAR_UUID, notification_handler)
    print(f"Listening for incoming data from {READ_CHAR_UUID}...\n")
    try:
        while True:
            await asyncio.sleep(1)  # Keeps loop alive
    except asyncio.CancelledError:
        pass

async def send_commands(client):
    """Allows user to send messages while notifications are running."""
    global collecting_data

    while True:
        user_input = await asyncio.to_thread(input, "> Type message (or 'exit' to quit, 'save' to start saving): ")
        
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "save":
            if not collecting_data:
                print("\n📡 Now collecting the next 30 messages...\n")
                collecting_data = True  # Start collecting data
            else:
                print("\n⚠️ Already collecting data! Waiting for 30 messages...\n")
        else:
            await client.write_gatt_char(WRITE_CHAR_UUID, user_input.encode('utf-8'), response=True)
            print(f"[BLE Sent] {user_input}")

async def ble_read_write():
    async with BleakClient(DEVICE_ADDRESS) as client:
        if client.is_connected:
            print(f"Connected to {DEVICE_ADDRESS}")

            # Run reading and writing in parallel
            receive_task = asyncio.create_task(receive_notifications(client))
            send_task = asyncio.create_task(send_commands(client))

            # Wait for the send task to finish (user exits)
            await send_task
            
            # Stop notifications before disconnecting
            await client.stop_notify(READ_CHAR_UUID)
            receive_task.cancel()  # Stop the receive loop

asyncio.run(ble_read_write())
