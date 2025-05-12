
import pandas as pd

# === LOAD 2010 DATA ===
imd_2010 = pd.read_csv("IMD 2010.csv")
employment_2010 = pd.read_csv("employment_2010.csv")
education_2010 = pd.read_csv("education and skills 2010.csv")
income_2010 = pd.read_csv("income 2010.csv")
barriers_2010 = pd.read_csv("Barries to Housing and services 2010.csv")
living_2010 = pd.read_csv("Living environment 2010.csv")

# Merge 2010 datasets
merged_2010 = imd_2010[["LSOA CODE", "IMD SCORE"]] \
    .merge(employment_2010[["LSOA CODE", "EMPLOYMENT SCORE"]], on="LSOA CODE") \
    .merge(education_2010[["LSOA CODE", "EDUCATION SKILLS AND TRAINING SCORE"]], on="LSOA CODE") \
    .merge(income_2010[["LSOA CODE", "INCOME SCORE"]], on="LSOA CODE") \
    .merge(barriers_2010[["LSOA CODE", "BARRIERS TO HOUSING AND SERVICES SCORE"]], on="LSOA CODE") \
    .merge(living_2010[["LSOA CODE", "LIVING ENVIRONMENT SCORE"]], on="LSOA CODE")

merged_2010["YEAR"] = 2010

# === LOAD 2015 DATA ===
scores_2015 = pd.read_excel("File_5_ID_2015_Scores_for_the_Indices_of_Deprivation.xlsx", sheet_name="ID2015 Scores")

scores_2015 = scores_2015[[
    "LSOA code (2011)",
    "Index of Multiple Deprivation (IMD) Score",
    "Employment Score (rate)",
    "Education, Skills and Training Score",
    "Income Score (rate)",
    "Barriers to Housing and Services Score",
    "Living Environment Score"
]].copy()

scores_2015.columns = [
    "LSOA CODE", "IMD SCORE", "EMPLOYMENT SCORE", "EDUCATION SKILLS AND TRAINING SCORE",
    "INCOME SCORE", "BARRIERS TO HOUSING AND SERVICES SCORE", "LIVING ENVIRONMENT SCORE"
]
scores_2015["YEAR"] = 2015

# === LOAD 2019 DATA ===
scores_2019 = pd.read_excel("File_5_-_IoD2019_Scores.xlsx", sheet_name="IoD2019 Scores")

scores_2019 = scores_2019[[
    "LSOA code (2011)",
    "Index of Multiple Deprivation (IMD) Score",
    "Employment Score (rate)",
    "Education, Skills and Training Score",
    "Income Score (rate)",
    "Barriers to Housing and Services Score",
    "Living Environment Score"
]].copy()

scores_2019.columns = [
    "LSOA CODE", "IMD SCORE", "EMPLOYMENT SCORE", "EDUCATION SKILLS AND TRAINING SCORE",
    "INCOME SCORE", "BARRIERS TO HOUSING AND SERVICES SCORE", "LIVING ENVIRONMENT SCORE"
]
scores_2019["YEAR"] = 2019

# === COMBINE ALL YEARS ===
combined = pd.concat([merged_2010, scores_2015, scores_2019], ignore_index=True)
combined.set_index(["LSOA CODE", "YEAR"], inplace=True)
combined.sort_index(inplace=True)

# === COPY FORWARD/BACKWARD TO FILL 2010–2025 ===
years = list(range(2010, 2026))
lsoas = combined.index.get_level_values(0).unique()

# Full LSOA × YEAR index
full_index = pd.MultiIndex.from_product([lsoas, years], names=["LSOA CODE", "YEAR"])
copy_filled_df = pd.DataFrame(index=full_index)

# Join known data and copy-fill missing years
copy_filled_df = copy_filled_df.join(combined)
copy_filled_df = copy_filled_df.groupby(level=0).apply(lambda group: group.ffill().bfill())
copy_filled_df.index = copy_filled_df.index.droplevel(0)

# === EXPORT FINAL CSV ===
final_df = copy_filled_df.reset_index()
final_df.to_csv("London_LSOA_Scores_CopyFilled_2010_2025.csv", index=False)
