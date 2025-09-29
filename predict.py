import serial
import joblib
import pandas as pd

# Load trained pipeline model
model = joblib.load("best_worad_rf.pkl")  # Load the latest trained model

# Load feature names from training data
df_train = pd.read_csv("latest.csv")
feature_columns = df_train.drop(columns=["Label"]).columns

# Serial settings
SERIAL_PORT = "COM7"
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

print("Listening for data...")

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("Data;"):
            # Parse serial data
            data_parts = line.replace("Data;", "").split(";")
            data_dict = {key_value.split(":")[0]: float(key_value.split(":")[1]) for key_value in data_parts if ":" in key_value}

            # Convert to DataFrame
            df_input = pd.DataFrame([data_dict])

            # Ensure feature order matches training data
            df_input = df_input.reindex(columns=feature_columns, fill_value=0)

            print("Raw Sensor Data:", df_input)

            # Predict (scaling is handled inside the model pipeline)
            prediction = model.predict(df_input)[0]

            # Assign labels
            label_dict = {
                1: "Ethanol",
                2: "Isopropanol",
                3: "Acetone"
            }
            label = label_dict.get(prediction, "Clean Air")

            print(f"Detected: {label}")

except KeyboardInterrupt:
    print("Stopping detection.")
    ser.close()
