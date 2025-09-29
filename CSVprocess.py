import os
import csv

# Folder containing the files
folder_path = r"C:\Users\User\Documents\RobotRead\JashData1103\Isoprop15"

# Required sensor names
required_sensors = ["BME688", "SGPVRaw", "SGPNRaw", "SGPVin", "SGPNin", "STCCO2", "ENSVoc",
                    "MiCO", "MiNO2", "MiNH3", "GMVOC", "GNH2S", "GMSMO", "GMETH", "GMWIN"]

# Process all .txt files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith(".txt"):
        txt_file_path = os.path.join(folder_path, file_name)
        csv_file_path = os.path.splitext(txt_file_path)[0] + ".csv"  # Change extension to .csv

        # Check if CSV already exists
        if os.path.exists(csv_file_path):
            print(f"Skipping {file_name}, CSV already exists.")
            continue

        cleaned_data = []

        # Read and process the text file
        with open(txt_file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                data_dict = {sensor: "" for sensor in required_sensors}  # Initialize empty values
                key_value_pairs = line.split(";")

                for pair in key_value_pairs:
                    if ":" in pair:
                        key, value = pair.split(":")
                        if key in data_dict:  # Only store known sensors
                            data_dict[key] = value.strip()

                cleaned_data.append(data_dict)

        # If no valid data, skip file
        if not cleaned_data:
            print(f"Skipping {file_name}, no valid data found.")
            continue

        # Write to CSV
        with open(csv_file_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=required_sensors)
            writer.writeheader()
            writer.writerows(cleaned_data)

        print(f"Processed {file_name} -> {csv_file_path}")
