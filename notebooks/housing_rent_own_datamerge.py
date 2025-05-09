import pandas as pd

# Load the housing dataset
housing_path = "C:/Users/20231229/PycharmProjects/shareddb_cbl/data_raw/houseing_type_rent_own.csv"  # Adjust if needed
df = pd.read_csv(housing_path)

# Common column
lsoa_col = "Lower layer Super Output Areas Code"

df_accom = df[df["Accommodation type (5 categories)"].notna()]
df_accom_wide = df_accom.pivot_table(
    index=lsoa_col,
    columns="Accommodation type (5 categories)",
    values="Observation",
    aggfunc="sum",
    fill_value=0
).reset_index()

df_accom_wide.columns.name = None
df_accom_wide = df_accom_wide.rename(columns={lsoa_col: "LSOA code"})


df_tenure = df[df["Tenure of household (5 categories)"].notna()]
df_tenure_wide = df_tenure.pivot_table(
    index=lsoa_col,
    columns="Tenure of household (5 categories)",
    values="Observation",
    aggfunc="sum",
    fill_value=0
).reset_index()

df_tenure_wide.columns.name = None
df_tenure_wide = df_tenure_wide.rename(columns={lsoa_col: "LSOA code"})


df_rooms = df[df["Number of people per room in household (5 categories)"].notna()]
df_rooms_wide = df_rooms.pivot_table(
    index=lsoa_col,
    columns="Number of people per room in household (5 categories)",
    values="Observation",
    aggfunc="sum",
    fill_value=0
).reset_index()

df_rooms_wide.columns.name = None
df_rooms_wide = df_rooms_wide.rename(columns={lsoa_col: "LSOA code"})


# Merge wide tables on LSOA code
df_housing = df_accom_wide.merge(df_tenure_wide, on="LSOA code", how="outer")
df_housing = df_housing.merge(df_rooms_wide, on="LSOA code", how="outer")

# Load your full enriched burglary dataset
df_main = pd.read_csv("C:/Users/20231229/PycharmProjects/shareddb_cbl/data_processed/burglary_with_industry_almost_full.csv")

# Merge housing data
df_main = df_main.merge(df_housing, on="LSOA code", how="left")
df_main.fillna(0, inplace=True)

# Save the final version
df_main.to_csv("C:/Users/20231229/PycharmProjects/shareddb_cbl/data_processed/all_features_data.csv", index=False)
print("Housing data successfully merged.")

