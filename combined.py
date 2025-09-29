import pandas as pd

# Load clean air data and assign label 0
df_clean = pd.read_csv("latest_clean.csv")
df_clean["Label"] = 0  # 0 represents Clean Air

# Load ethanol data and assign label 1
df_ethanol = pd.read_csv("latest_ethanol.csv")
df_ethanol["Label"] = 1  # 1 represents ethanol

# Load isopropanol data and assign label 2
df_iso = pd.read_csv("latest_isopropanol.csv")
df_iso["Label"] = 2  # 1 represents isopropanol

# Load acetone data and assign label 3
df_acetone = pd.read_csv("latest_acetone.csv")
df_acetone["Label"] = 3  # 1 represents isopropanol

# Combine all datasets
df = pd.concat([df_clean, df_ethanol, df_iso, df_acetone], ignore_index=True)

# Save combined dataset
output_filename = "latest.csv"

# Save combined dataset for reference
df.to_csv(output_filename, index=False)

print(f"Datasets merged and saved as {output_filename}")
