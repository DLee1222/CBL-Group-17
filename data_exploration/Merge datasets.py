import pandas as pd

file1_path = "C:/Users/KIM JINOK/PycharmProjects/CBL-Group-17/data_processed/burglary_lsoa_month_2010_2025.csv"
file2_path = "C:/Users/KIM JINOK/PycharmProjects/CBL-Group-17/data_processed/London_LSOA_Scores_CopyFilled_2010_2025.csv"

burglary_df = pd.read_csv(file1_path)
scores_df = pd.read_csv(file2_path)

burglary_df.rename(columns={"LSOA code": "lsoa_code", "Year": "year"}, inplace=True)
scores_df.rename(columns={"LSOA CODE": "lsoa_code", "YEAR": "year"}, inplace=True)

merged_df = pd.merge(burglary_df, scores_df, on=["lsoa_code", "year"], how="left")

merged_df.head()

output_path = "C:/Users/KIM JINOK/PycharmProjects/CBL-Group-17/data_exploration/merged_burglary_scores_2010_2025.csv"
merged_df.to_csv(output_path, index=False)

output_path