import os
import pandas as pd

data = "../data_raw/police_data"
#List that holds the dataframes corresponding to each csv.
df_old_list = []

#iterate through each csv, convert it to a dataframe and append it to the list.
for filename in  os.listdir(data):
    if filename.endswith(".csv") or filename.endswith(".CSV"):
        file_path = os.path.join(data, filename)
        folder_month = filename[:7]  # e.g., "2016-05"
        try:
            df = pd.read_csv(file_path)
            df["Folder_Month"] = folder_month
            df_old_list.append(df)
            print(f"Loaded : {filename}")
        except Exception as e:
            print(f"Error loading {filename}: {e}")
#connect all the dataframes in the list into one dataframe.
df_all = pd.concat(df_old_list, ignore_index=True)

# Create the dataframe burglary which contains only the rows with the crime type "Burglary"
df_burglary = df_all[df_all["Crime type"] == "Burglary"].copy()
df_burglary["Month"] = pd.to_datetime(df_burglary["Folder_Month"], format="%Y-%m")
df_burglary["Year"] = df_burglary["Month"].dt.year
df_burglary["Month_Num"] = df_burglary["Month"].dt.month

#Group by LSOA + Year + Month
df_counts = (
    df_burglary.groupby(["LSOA code", "Year", "Month_Num"])
    .size()
    .reset_index(name="Burglary_Count")
)
# Save final result
output_path = "../data_processed/burglary_lsoa_month_2010_2025.csv"
df_counts.to_csv(output_path, index=False)
print(f"Saved full burglary dataset to {output_path}")



 #2. LOAD NEW FILES
 #new_path = "/data_raw/data2"
 #df_new_list = []
#
# for folder_name in os.listdir(new_path):
#     folder_path = os.path.join(new_path, folder_name)
#     if os.path.isdir(folder_path):
#         for filename in os.listdir(folder_path):
#             if filename.endswith(".csv") or filename.endswith(".CSV"):
#                 file_path = os.path.join(folder_path, filename)
#                 try:
#                     df = pd.read_csv(file_path)
#                     df["Folder_Month"] = folder_name
#                     df_new_list.append(df)
#                     print(f"Loaded (new): {filename}")
#                 except Exception as e:
#                     print(f"Error loading {filename}: {e}")
#
# df_new_all = pd.concat(df_new_list, ignore_index=True)


#  3. COMBINE ALL DATA
# df_all = pd.concat([df_old_all, df_new_all], ignore_index=True)
# print(f"\nTotal combined rows: {len(df_all)}")
#
#
# # 4. PROCESS FOR BURGLARY AGGREGATION
# df_burglary = df_all[df_all["Crime type"] == "Burglary"].copy()
# df_burglary["Month"] = pd.to_datetime(df_burglary["Folder_Month"], format="%Y-%m")
# df_burglary["Year"] = df_burglary["Month"].dt.year
# df_burglary["Month_Num"] = df_burglary["Month"].dt.month
#
# # Group by LSOA + Year + Month
# df_counts = (
#     df_burglary.groupby(["LSOA code", "Year", "Month_Num"])
#     .size()
#     .reset_index(name="Burglary_Count")
# )
#
# # Save final result
# output_path = "/data_processed/burglary_lsoa_month_2016_2025.csv"
# df_counts.to_csv(output_path, index=False)
# print(f"Saved full burglary dataset to {output_path}")



