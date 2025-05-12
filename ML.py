import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, precision_score
from sklearn.model_selection import train_test_split


imd_url = (
    "https://assets.publishing.service.gov.uk/media/"
    "5dc407b440f0b6379a7acc8d/"
    "File_7_-_All_IoD2019_Scores__Ranks__Deciles_and_Population_Denominators_3.csv"
)
print("Loading IMD data from GOV.UK…")
imd = pd.read_csv(imd_url)
imd.rename(columns={"LSOA code (2011)": "LSOA code"}, inplace=True)


imd_feats = imd[[
    "LSOA code",
    "Index of Multiple Deprivation (IMD) Score",
    "Index of Multiple Deprivation (IMD) Decile (where 1 is most deprived 10% of LSOAs)",
    "Income Score (rate)",
    "Employment Score (rate)",
    "Living Environment Score"
]]
print(f"→ IMD features: {imd_feats.shape[1]} columns")


crimes_dir = os.path.join(os.getcwd(), "data", "2022-03")
print("Loading crime CSVs from:", crimes_dir)
csv_files = [
    os.path.join(crimes_dir, f)
    for f in os.listdir(crimes_dir)
    if f.lower().endswith(".csv")
]
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {crimes_dir}")
print(f"Found {len(csv_files)} files. Concatenating…")
crimes = pd.concat((pd.read_csv(p) for p in csv_files), ignore_index=True)
print("→ Combined crimes:", crimes.shape)


rob = crimes[crimes["Crime type"] == "Robbery"].copy()
rob["Month"] = pd.to_datetime(rob["Month"], format="%Y-%m")
rob.dropna(subset=["Longitude", "Latitude", "LSOA code"], inplace=True)
print("→ Robberies subset:", rob.shape)


df = rob.merge(imd_feats, on="LSOA code", how="left")
print("→ After IMD merge:", df.shape)
# SANITY‐CHECK
print(df.loc[:, [
    "LSOA code",
    "Month",
    "Index of Multiple Deprivation (IMD) Score",
    "Income Score (rate)",
    "Employment Score (rate)",
    "Living Environment Score"
]].head(5))


counts = (
    df
    .groupby([df["LSOA code"], df["Month"].dt.to_period("M")])
    .size()
    .reset_index(name="rob_count")
)
counts["Month"] = counts["Month"].dt.to_timestamp()
df_count = counts.merge(imd_feats, on="LSOA code", how="left")
print("→ Aggregated LSOA-Month rows:", df_count.shape[0])


df_count.sort_values(["LSOA code", "Month"], inplace=True)
df_count["lag1"] = df_count.groupby("LSOA code")["rob_count"].shift(1).fillna(0)
df_count["lag2"] = df_count.groupby("LSOA code")["rob_count"].shift(2).fillna(0)
df_count["mo"]    = df_count["Month"].dt.month
df_count["mo_sin"] = np.sin(2 * np.pi * df_count["mo"] / 12)
df_count["mo_cos"] = np.cos(2 * np.pi * df_count["mo"] / 12)


threshold = df_count["rob_count"].quantile(0.90)
df_count["hot"] = (df_count["rob_count"] >= threshold).astype(int)
print(f"Hotspot threshold (90th pct): {threshold}")


features = [
    "lag1", "lag2", "mo_sin", "mo_cos",
    "Index of Multiple Deprivation (IMD) Score",
    "Income Score (rate)",
    "Employment Score (rate)"
]
X = df_count[features]
y = df_count["hot"]


n_months = df_count["Month"].nunique()
if n_months > 1:
    split_date = df_count["Month"].max() - pd.DateOffset(months=3)
    mask_train = df_count["Month"] <= split_date
    X_train, y_train = X[mask_train], y[mask_train]
    X_test,  y_test  = X[~mask_train], df_count.loc[~mask_train, "hot"]
    print(f"Using time split: Train months ≤ {split_date.date()}")
else:
    print(f"Only {n_months} month(s) present—using random 70/30 split")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

print(f"Train rows: {len(X_train)}, Test rows: {len(X_test)}")


print("Training RandomForestClassifier…")
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

y_proba = model.predict_proba(X_test)[:, 1]
auc      = roc_auc_score(y_test, y_proba)
y_pred   = (y_proba >= 0.5).astype(int)
prec     = precision_score(y_test, y_pred)

print(f"AUC-ROC : {auc:.3f}")
print(f"Precision: {prec:.3f}")




risk_proba = model.predict_proba(X)[:, 1]
df_count["risk_score"] = risk_proba


df_count["risk_rank"] = (
    df_count["risk_score"]
    .rank(method="first", ascending=False)
    .astype(int)
)



output = df_count[[
    "LSOA code",
    "Month",
    "risk_score",
    "risk_rank"
]].sort_values("risk_rank")

print("\nTop 10 high-risk LSOAs:")
print(output.head(10).to_string(index=False))

out_path = os.path.join(os.getcwd(), "robbery_risk_by_lsoa.csv")
output.to_csv(out_path, index=False)
print(f"\nSaved risk summary to: {out_path}")