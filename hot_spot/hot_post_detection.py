import pandas as pd


df = pd.read_csv("hot-spot.csv")
total_crime = df["Burglary_Count"].sum()

df_sorted = df.sort_values("Burglary_Count", ascending=False).reset_index(drop=True)
df_sorted["Cumulative"] = df_sorted["Burglary_Count"].cumsum()
df_sorted["Cumulative_Percent"] = df_sorted["Cumulative"] / total_crime * 100

threshold_index = df_sorted[df_sorted["Cumulative_Percent"] >= 50].index[0]
num_lsoas_50pct = threshold_index + 1

print(f"Total burglary count: {total_crime}")
print(f"Number of LSOAs accounting for 50% of total crime: {num_lsoas_50pct}")

top_lsoas = df_sorted.head(num_lsoas_50pct)
print("\nLSOAs contributing to the first 50% of crime:")
print(top_lsoas[["LSOA code", "Burglary_Count", "Cumulative_Percent"]].to_string(index=False))
