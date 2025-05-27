import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, precision_score
from sklearn.model_selection import train_test_split



print("Working directory:", os.getcwd())
print("Files here:", os.listdir("."))

dataset = pd.read_csv("dataset_ML.csv")
print("Dataset shape:", dataset.shape)

hotspots = pd.read_csv("hotspot_ML.csv")
print("Hotspot sample shape:", hotspots.shape)


hotspots = hotspots.assign(hotspot=1)[[
    "LSOA code","year","Month_Num","hotspot"
]]



df = (
    dataset
    .merge(hotspots, on=["LSOA code","year","Month_Num"], how="left")
    .assign(hotspot=lambda d: d["hotspot"].fillna(0).astype(int))
)
print("After merge:", df.shape, "| 1’s in hotspot:", df["hotspot"].sum())




df = df.sort_values(["LSOA code","year","Month_Num"])


df["lag1"] = df.groupby("LSOA code")["Burglary_Count"].shift(1).fillna(0)
df["lag2"] = df.groupby("LSOA code")["Burglary_Count"].shift(2).fillna(0)


df["month_sin"] = np.sin(2*np.pi*df["Month_Num"]/12)
df["month_cos"] = np.cos(2*np.pi*df["Month_Num"]/12)



features = [
    "lag1","lag2",
    "Burglary_Count",
    "IMD SCORE",
    "INCOME SCORE",
    "EMPLOYMENT SCORE",
    "EDUCATION SKILLS AND TRAINING SCORE",
    "BARRIERS TO HOUSING AND SERVICES SCORE",
    "LIVING ENVIRONMENT SCORE",
    "longitude","latitude",
    "month_sin","month_cos"
]
X = df[features]
y = df["hotspot"]




X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

print(f"Train rows: {len(X_train)}, Test rows: {len(X_test)}")

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)



y_proba = model.predict_proba(X_test)[:,1]
y_pred  = (y_proba >= 0.5).astype(int)

auc   = roc_auc_score(y_test, y_proba)
prec  = precision_score(y_test, y_pred)

print(f"AUC-ROC:   {auc:.3f}")
print(f"Precision: {prec:.3f}")



df["risk_score"] = model.predict_proba(X)[:,1]
df["risk_rank"]  = df["risk_score"].rank(
    method="first", ascending=False
).astype(int)



output = df[[
    "LSOA code",
    "year","Month_Num",
    "risk_score","risk_rank"
]].sort_values("risk_rank")

out_path = "robbery_risk_by_lsoa.csv"
output.to_csv(out_path, index=False)
print(f"Saved summary to {out_path}")