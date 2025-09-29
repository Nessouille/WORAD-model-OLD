import serial
import pandas as pd
import time

# Adjust the port and baud rate according to your Arduino settings
SERIAL_PORT = "COM3"  
BAUD_RATE = 115200  

# Open serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Storage for data
data_list = []

try:
    print("Reading data from Arduino...\n")
    
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        
        if line.startswith("Data;"):
            # Remove "Data;" prefix and split by ";"
            data_parts = line.replace("Data;", "").split(";")
            data_dict = {}

            for part in data_parts:
                key_value = part.split(":")
                if len(key_value) == 2:
                    key, value = key_value
                    try:
                        data_dict[key.strip()] = float(value.strip())
                    except ValueError:
                        data_dict[key.strip()] = value.strip()  # Keep non-numeric values (e.g., labels)

            # Print data in a formatted way
            print(f"{time.strftime('%H:%M:%S')} → {data_dict}")

            # Store data
            data_list.append(data_dict)

            # Save to CSV every 10 entries
            csv_name = "latest_acetone.csv"

            if len(data_list) % 10 == 0:
                df = pd.DataFrame(data_list)
                df.to_csv(csv_name, index=False)
                print(f"Saved {len(data_list)} entries to {csv_name}")

except KeyboardInterrupt:
    print("\nData collection stopped by user.")
    ser.close()
