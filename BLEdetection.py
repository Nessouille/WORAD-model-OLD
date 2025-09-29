import asyncio
from bleak import BleakScanner, BleakClient

async def scan_devices():
    """ Scans for nearby BLE devices and prints their addresses and names. """
    print("[Scanning for devices...]")
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Found device: {device.name} - {device.address}")
    return devices

async def get_services(device_address):
    """ Fetches and prints the services and characteristics of the connected BLE device. """
    async with BleakClient(device_address) as client:
        services = await client.get_services()
        print(f"\nConnected to {device_address}")
        for service in services:
            print(f"Service: {service.uuid}")
            for char in service.characteristics:
                print(f"  ├── Characteristic: {char.uuid} (Properties: {char.properties})")

async def main():
    # Step 1: Scan for devices and get their addresses
    devices = await scan_devices()
    
    if not devices:
        print("[Error] No devices found.")
        return

    # Step 2: Choose the device address (you can modify this to pick a specific device or use its name)
    # For now, let's pick the first available device from the scan
    device_address = "C9:6D:69:38:E7:03"
    print(f"Connecting to {device_address}...\n")

    # Step 3: Fetch services and characteristics of the chosen device
    await get_services(device_address)

# Run the main function
asyncio.run(main())
