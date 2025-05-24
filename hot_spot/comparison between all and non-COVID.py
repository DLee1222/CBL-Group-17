import pandas as pd

all_hotspot =  pd.read_csv('hot_spots_top50%.csv')
nonCOVID_hotspot = pd.read_csv('hot_spots_top50%_nonCOVID.csv')

all_lsoas = set(all_hotspot['LSOA code'].unique())
nonCOVID_lsoas = set(nonCOVID_hotspot['LSOA code'].unique())

lsoas_only_in_nonCOVID= nonCOVID_lsoas - all_lsoas

# Count how many are different
count_diff = len(lsoas_only_in_nonCOVID)

# Show result
print(f"Number of LSOA codes in 'b' but not in 'a': {count_diff}")
print("Different LSOA codes:", lsoas_only_in_nonCOVID)