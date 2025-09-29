import asyncio
from bleak import BleakClient

# BLE Device Address
DEVICE_ADDRESS = "C9:6D:69:38:E7:03"

# UUIDs for Read (Notify) and Write characteristics
WRITE_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
READ_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

# Buffer to store fragmented BLE packets
received_data = []

# Callback to handle incoming notifications
def notification_handler(sender, data):
    """Handles BLE notifications and reconstructs split messages."""
    global received_data
    text = data.decode("utf-8")  # Convert bytes to string
    received_data.append(text)  # Store fragment

    # Check for end of message (assuming a newline '\n' or semicolon as an end marker)
    if "\n" in text or text.endswith(";GMWIN:"):
        full_message = "".join(received_data)  # Merge all fragments
        print(f"\n[BLE Full Message] {full_message}\n> ")
        received_data.clear()  # Reset buffer for next message

async def receive_notifications(client):
    """ Continuously listens for notifications. """
    await client.start_notify(READ_CHAR_UUID, notification_handler)
    print(f"Listening for incoming data from {READ_CHAR_UUID}...\n")
    try:
        while True:
            await asyncio.sleep(1)  # Keeps the loop alive
    except asyncio.CancelledError:
        pass

async def send_commands(client):
    """ Allows user to send messages while notifications are running. """
    while True:
        user_input = await asyncio.to_thread(input, "> Type message (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
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
