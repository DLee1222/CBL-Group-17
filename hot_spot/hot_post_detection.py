import pandas as pd
import os


data = "../data_processed/burglary_lsoa_month_2010_2025.csv"
df = pd.read_csv(data)

df_burglary_aggregated = df.groupby("LSOA code", as_index = False)['Burglary_Count'].sum()
output_path = "hot-spot"
df_burglary_aggregated.to_csv(output_path, index=False)
print(f"Saved full burglary dataset to {output_path}")