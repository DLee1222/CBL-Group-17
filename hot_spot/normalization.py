import pandas as pd
from scipy.stats import norm
df = pd.read_csv("hot-spot.csv")
# we calculate the z-score for the Burglary_Count column
df["z_score"] = (df["Burglary_Count"]- df["Burglary_Count"].mean()) / df["Burglary_Count"].std()
# calculate what is the z-score belonging to the top 10% of the distribution
z90 = norm.ppf(0.90) # finds the z-score where 90% of the distribution lies below that value.
#put the rows with true in the hotspots dataframe.
hotspots = df[df["z_score"] > z90]
hotspots.to_csv("hot_spots_top10%.csv", index=False)