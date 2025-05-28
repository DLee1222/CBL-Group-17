# Re-import libraries after code execution environment reset
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

# Reload the uploaded datasets
burglary_data = pd.read_csv("/mnt/data/dataset_ML.csv")
hotspot_data = pd.read_csv("/mnt/data/hotspot_ML.csv")

# Step 1: Compute Burglary Trend
def compute_trend(df, lsoa_col="LSOA code", year_col="year", target_col="Burglary_Count"):
    trends = []
    for lsoa, group in df.groupby(lsoa_col):
        X = group[year_col].values.reshape(-1, 1)
        y = group[target_col].values
        if len(X) > 1 and len(set(y)) > 1:
            model = LinearRegression().fit(X, y)
            trend = model.coef_[0]
        else:
            trend = 0.0
        trends.append((lsoa, trend))
    return pd.DataFrame(trends, columns=[lsoa_col, "Burglary_Trend"])

trend_df = compute_trend(burglary_data)

# Step 2: Compute average burglaries in the last 3 years (2023–2025)
recent_avg = burglary_data[burglary_data["year"] >= 2023]
recent_mean = recent_avg.groupby("LSOA code")["Burglary_Count"].mean().reset_index()
recent_mean.columns = ["LSOA code", "Recent_3yr_Avg_Burglaries"]

# Step 3: Compute geographic clusters
agg_coords = burglary_data.groupby("LSOA code")[["longitude", "latitude"]].first().reset_index()
kmeans = KMeans(n_clusters=10, random_state=42)
agg_coords["GeoCluster"] = kmeans.fit_predict(agg_coords[["longitude", "latitude"]])

# Step 4: Create base modeling dataset
base = burglary_data.groupby("LSOA code").agg({
    'IMD SCORE': 'first',
    'EMPLOYMENT SCORE': 'first',
    'EDUCATION SKILLS AND TRAINING SCORE': 'first',
    'INCOME SCORE': 'first',
    'BARRIERS TO HOUSING AND SERVICES SCORE': 'first',
    'LIVING ENVIRONMENT SCORE': 'first',
    'longitude': 'first',
    'latitude': 'first'
}).reset_index()

# Step 5: Add target label
hotspot_lsoas = set(hotspot_data['LSOA code'].unique())
base["Target"] = base["LSOA code"].apply(lambda x: 1 if x in hotspot_lsoas else 0)

# Step 6: Merge engineered features into base dataset
merged_df = base.merge(trend_df, on="LSOA code", how="left")
merged_df = merged_df.merge(recent_mean, on="LSOA code", how="left")
merged_df = merged_df.merge(agg_coords[["LSOA code", "GeoCluster"]], on="LSOA code", how="left")

# Display the resulting feature-enhanced dataset
import ace_tools as tools

tools.display_dataframe_to_user(name="Feature-Enhanced Modeling Dataset", dataframe=merged_df)

merged_df.head()
