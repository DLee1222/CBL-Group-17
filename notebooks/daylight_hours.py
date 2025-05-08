import pandas as pd

# Load the latest version of your dataset
df = pd.read_csv("C:/Users/20231229/PycharmProjects/shareddb_cbl/data_processed/burglary_with_schools.csv")

# Define more accurate daylight hours for London (mid-month average)
daylight_precise = pd.DataFrame({
    "Month_Num": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "Precise_Daylight_Hours": [
        8.07, 9.93, 11.93, 13.93, 15.87, 16.37,
        15.80, 14.40, 12.43, 10.50, 8.40, 7.93
    ]
})

# Merge with main dataset
df = df.merge(daylight_precise, on="Month_Num", how="left")

# Save the new version
output_path = "C:/Users/20231229/PycharmProjects/shareddb_cbl/data_processed/burglary_with_schools_and_daylight.csv"
df.to_csv(output_path, index=False)

print("Updated dataset with precise daylight hours saved.")
print(df[["Year", "Month_Num", "Daylight_Hours"]].drop_duplicates().sort_values(["Year", "Month_Num"]).head())
