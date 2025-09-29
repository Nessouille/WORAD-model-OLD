import asyncio
import os
from bleak import BleakClient
from datetime import datetime

# BLE Device Address
DEVICE_ADDRESS = "C9:6D:69:38:E7:03"

# UUIDs for Read (Notify) and Write characteristics
WRITE_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
READ_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

# Folder path for saving files
FOLDER_PATH = r"C:\Users\User\Documents\RobotRead"  # Update this to your folder path

# Ensure the folder exists, create it if it doesn't
if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)

# Global variables for managing readings
readings = []
is_recording = False

async def send_ack(client):
    """Send acknowledgment to the device"""
    try:
        ack_message = b'ACK\n'
        await client.write_gatt_char(WRITE_CHAR_UUID, ack_message)
    except Exception as e:
        print(f"Failed to send ACK: {e}")

# Callback to handle incoming notifications
def notification_handler(sender, data, client):
    global readings, is_recording
    try:
        message = data.decode('utf-8').strip()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        formatted_message = f"{timestamp}: {message}"
        #print(f"\n[BLE Received] {formatted_message}", end="\n> ")
        
        if is_recording:
            readings.append(formatted_message)
            #print(f"[Recording] {formatted_message}")
            # Send acknowledgment after receiving data in recording mode
            
            asyncio.create_task(send_ack(client))  # Instead of sender.client

        
        if len(readings) >= 5:
            save_to_file()
            readings = []
            print(f"Saved 5 readings to {get_filename()}")
    except Exception as e:
        print(f"Error processing notification: {e}")

async def listen_for_notifications(client):
    """ Continuously listens for notifications from BLE device. """
    await client.start_notify(READ_CHAR_UUID, lambda s, d: notification_handler(s, d, client))

    while True:
        await asyncio.sleep(0.1)  # Keep the loop alive to process notifications

async def send_messages(client):
    """ Handles user input without blocking BLE listening. """
    global is_recording
    while True:
        user_input = await asyncio.to_thread(input, "> Type 'start' to begin recording or 'stop' to stop: ")
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "start":
            # Start recording and reset the readings list
            if not is_recording:
                is_recording = True
                readings = []  # Clear any previous data
                # Send initial START acknowledgment
                await send_ack(client)
                print("Recording started!")
        elif user_input.lower() == "stop":
            # Stop recording
            if is_recording:
                is_recording = False
                # Send final STOP acknowledgment
                await send_ack(client)
                await save_to_file()
                print("Recording stopped and saved.")
        else:
            print("Invalid command. Type 'start' to record or 'stop' to stop.")

async def save_to_file():
    try:
        filename = get_filename()
        file_path = os.path.join(FOLDER_PATH, filename)
        with open(file_path, "w") as file:
            file.write(f"Recording Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write("-" * 50 + "\n")
            for reading in readings:
                file.write(f"{reading}\n")
        print(f"Successfully saved readings to {filename}")
    except Exception as e:
        print(f"Error saving to file: {e}")

async def ble_read_write():
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Attempting to connect... (Attempt {retry_count + 1}/{max_retries})")
            async with BleakClient(DEVICE_ADDRESS, timeout=20.0) as client:
                if client.is_connected:
                    print(f"Connected to {DEVICE_ADDRESS}\n")
                    print("Connection established successfully!")
                    print("Type 'start' to begin recording or 'stop' to stop")

                    listen_task = asyncio.create_task(listen_for_notifications(client))
                    
                    try:
                        await send_messages(client)
                    except asyncio.CancelledError:
                        print("\nConnection interrupted...")
                    finally:
                        listen_task.cancel()
                        await client.stop_notify(READ_CHAR_UUID)
                    break
        except Exception as e:
            retry_count += 1
            print(f"Connection failed: {e}")
            if retry_count < max_retries:
                print(f"Retrying in 5 seconds...")
                await asyncio.sleep(5)
            else:
                print("Maximum retry attempts reached. Please check the device and try again.")
                break

def get_filename():
    """ Generates a filename with the current date and time in YYMMDD_HHMM format. """
    current_time = datetime.now()
    return f"reading_{current_time.strftime('%y%m%d_%H%M')}.txt"

asyncio.run(ble_read_write())

