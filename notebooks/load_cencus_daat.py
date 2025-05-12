import pandas as pd

# Load ethnicity data
eth_path = "C:/Users/20231229/PycharmProjects/shareddb_cbl/data_raw/ethnic_london_lsoa_data.csv"
df_eth = pd.read_csv(eth_path)

# Pivot to get one row per LSOA, one column per ethnic group
df_eth_wide = df_eth.pivot_table(
    index="Lower layer Super Output Areas Code",
    columns="Ethnic group (20 categories)",
    values="Observation",
    aggfunc="sum",
    fill_value=0
).reset_index()

# Rename index column
df_eth_wide = df_eth_wide.rename(columns={"Lower layer Super Output Areas Code": "LSOA code"})


# Load NS-SeC occupation data
nsec_path = "C:/Users/20231229/PycharmProjects/shareddb_cbl/data_raw/social_factors_london_data.csv"
df_nsec = pd.read_csv(nsec_path)

# Pivot to wide format
df_nsec_wide = df_nsec.pivot_table(
    index="Lower layer Super Output Areas Code",
    columns="National Statistics Socio-economic Classification (NS-SeC) (10 categories)",
    values="Observation",
    aggfunc="sum",
    fill_value=0
).reset_index()

df_nsec_wide = df_nsec_wide.rename(columns={"Lower layer Super Output Areas Code": "LSOA code"})


# Merge ethnicity + NS-SeC
df_census = df_eth_wide.merge(df_nsec_wide, on="LSOA code", how="outer")

# Check result
print(f"✅ Census enrichment table has {df_census.shape[0]} rows and {df_census.shape[1]} columns")
print(df_census.head())

# Load your existing enriched burglary-month dataset
df_burg = pd.read_csv("C:/Users/20231229/PycharmProjects/shareddb_cbl/data_processed/burglary_lsoa_month_2016_2025.csv")

# Merge census features into every LSOA record
df_final = df_burg.merge(df_census, on="LSOA code", how="left")

# Optional: fill missing census data (e.g., with 0 or 'Unknown')
df_final.fillna(0, inplace=True)

# Save result
df_final.to_csv("C:/Users/20231229/PycharmProjects/shareddb_cbl/data_processed/burglary_lsoa_with_social.csv", index=False)
print("💾 Final dataset with full census features saved.")
