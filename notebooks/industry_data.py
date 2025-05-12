import pandas as pd

# Load industry dataset
industry_path = "C:/Users/20231229/PycharmProjects/shareddb_cbl/data_raw/industry_data.csv"  # Adjust if needed
df_ind = pd.read_csv(industry_path)

# Optional: preview column names
print(df_ind.columns)


# Pivot: one row per LSOA, one column per industry
df_ind_wide = df_ind.pivot_table(
    index="Lower layer Super Output Areas Code",
    columns="Industry (current) (9 categories)",
    values="Observation",
    aggfunc="sum",
    fill_value=0
).reset_index()

# Clean up column names
df_ind_wide.columns.name = None
df_ind_wide = df_ind_wide.rename(columns={"Lower layer Super Output Areas Code": "LSOA code"})

# Optional: rename columns to shorter labels
df_ind_wide = df_ind_wide.rename(columns={
    "A, B, D, E Agriculture, energy and water": "Ind_Agriculture",
    "C Manufacturing": "Ind_Manufacturing",
    "F Construction": "Ind_Construction",
    "G, I Distribution, hotels and restaurants": "Ind_Distribution",
    "H, J Transport and communication": "Ind_Transport",
    "K, L, M, N Financial, real estate, professional and admin": "Ind_Finance",
    "O, P, Q Public admin, education and health": "Ind_PublicServices",
    "R, S, T, U Other services": "Ind_OtherServices"
})


# Load your current dataset (with schools + daylight)
df = pd.read_csv("C:/Users/20231229/PycharmProjects/shareddb_cbl/data_processed/burglary_with_schools_and_daylight.csv")

# Merge industry info
df = df.merge(df_ind_wide, on="LSOA code", how="left")

# Optional: fill missing values with 0 (in case a small number of LSOAs are missing)
df.fillna(0, inplace=True)

# Save the final enriched dataset
df.to_csv("C:/Users/20231229/PycharmProjects/shareddb_cbl/data_processed/burglary_with_industry_almost_full.csv", index=False)
print("💾 Industry data merged into final dataset.")

