import os
import pandas as pd

# === 1. Load all monthly police CSVs ===
folder_path = "C:/Users/20231229/PycharmProjects/shareddb_cbl/data_raw/police_data"  # Your folder with monthly CSVs
df_list = []

for file in os.listdir(folder_path):
    if file.endswith(".csv"):
        path = os.path.join(folder_path, file)
        try:
            df = pd.read_csv(path)
            df["Month_Str"] = file[:7]  # for example 2011-03
            df_list.append(df)
        except Exception as e:
            print(f"Could not read {file}: {e}")

df_all = pd.concat(df_list, ignore_index=True)

# === 2. Filter only burglary crimes ===
df_burglary = df_all[df_all["Crime type"].str.lower() == "burglary"].copy()

# === 3. Extract Year, Month ===
df_burglary["Year"] = df_burglary["Month_Str"].str[:4].astype(int)
df_burglary["Month_Num"] = df_burglary["Month_Str"].str[-2:].astype(int)

# Use LSOA code
if "LSOA code" in df_burglary.columns:
    group_col = "LSOA code"
elif "LSOA name" in df_burglary.columns:
    group_col = "LSOA name"
else:
    raise ValueError("No usable LSOA column found.")

df_grouped = df_burglary.groupby([group_col, "Year", "Month_Num"]).size().reset_index(name="Burglary_Count")
df_grouped = df_grouped.rename(columns={group_col: "LSOA code"})

# === 4. Add precise daylight hours per month ===
daylight_hours = pd.DataFrame({
    "Month_Num": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "Precise_Daylight_Hours": [8.07, 9.93, 11.93, 13.93, 15.87, 16.37,
                               15.80, 14.40, 12.43, 10.50, 8.40, 7.93]
})

df_grouped = df_grouped.merge(daylight_hours, on="Month_Num", how="left")

# === 5. Load LSOA-level static features ===
df_lsoa = pd.read_csv("C:/Users/20231229/PycharmProjects/shareddb_cbl/data_processed/LSOA_features.csv")

# === 6. Merge time series with LSOA features ===
df_final = df_grouped.merge(df_lsoa, on="LSOA code", how="left")
df_final.fillna(0, inplace=True)

# === 7. Save the final dataset ===
output_path = "C:/Users/20231229/PycharmProjects/shareddb_cbl/data_processed/burglary_lsoa_month_enriched.csv"
os.makedirs("data_processed", exist_ok=True)
df_final.to_csv(output_path, index=False)

print(f"Final dataset with daylight hours saved to: {output_path}")
