import os
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, precision_score
from sklearn.model_selection import train_test_split


print("Working dir:", os.getcwd())
print("Files here:", os.listdir("."))

dataset = pd.read_csv("dataset_ML.csv")
hotspots = (
    pd.read_csv("hotspot_ML.csv")
      .assign(hotspot=1)[["LSOA code","year","Month_Num","hotspot"]]
)


df = (
    dataset
    .merge(hotspots, on=["LSOA code","year","Month_Num"], how="left")
    .assign(hotspot=lambda d: d["hotspot"].fillna(0).astype(int))
)
print("Merged shape:", df.shape, "| #hotspots:", df["hotspot"].sum())


df = df.sort_values(["LSOA code","year","Month_Num"])
df["lag1"] = df.groupby("LSOA code")["Burglary_Count"].shift(1).fillna(0)
df["lag2"] = df.groupby("LSOA code")["Burglary_Count"].shift(2).fillna(0)
df["month_sin"] = np.sin(2 * np.pi * df["Month_Num"] / 12)
df["month_cos"] = np.cos(2 * np.pi * df["Month_Num"] / 12)


all_features = [
    "lag1","lag2","Burglary_Count",
    "IMD SCORE","INCOME SCORE","EMPLOYMENT SCORE",
    "EDUCATION SKILLS AND TRAINING SCORE",
    "BARRIERS TO HOUSING AND SERVICES SCORE",
    "LIVING ENVIRONMENT SCORE","longitude","latitude",
    "month_sin","month_cos"
]
X_all = df[all_features]
y_all = df["hotspot"]

X_train_all, X_test_all, y_train, y_test = train_test_split(
    X_all, y_all, test_size=0.3, random_state=42, stratify=y_all
)
print(f"Train rows: {len(X_train_all)}, Test rows: {len(X_test_all)}")


initial_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
initial_model.fit(X_train_all, y_train)


y_proba_initial = initial_model.predict_proba(X_test_all)[:, 1]
y_pred_initial  = (y_proba_initial >= 0.5).astype(int)

auc_initial  = roc_auc_score(y_test, y_proba_initial)
prec_initial = precision_score(y_test, y_pred_initial)

print("Initial (all‐feature) model metrics:")
print(f"  AUC-ROC:   {auc_initial:.3f}")
print(f"  Precision: {prec_initial:.3f}")


explainer_all = shap.TreeExplainer(initial_model)
shap_vals_all  = explainer_all.shap_values(X_train_all)
shap_pos_all   = shap_vals_all[1]


plt.figure(figsize=(8, 6))
shap.summary_plot(
    shap_pos_all,
    X_train_all,
    feature_names=all_features,
    plot_type="bar",
    show=False
)
plt.tight_layout()
plt.savefig("shap_all_features_bar.png", dpi=150)
plt.close()
print("Saved SHAP bar chart on ALL features to shap_all_features_bar.png")


importance_df = pd.DataFrame({
    "feature": all_features,
    "mean_abs_shap": np.abs(shap_pos_all).mean(axis=0)
}).sort_values("mean_abs_shap", ascending=False)

importance_df.to_csv("shap_feature_importances_all.csv", index=False)
print("Saved numeric SHAP importances (all) to shap_feature_importances_all.csv")


k = 8
topk_features = importance_df["feature"].iloc[:k].tolist()
print(f"Top {k} features by SHAP importance: {topk_features}")


X_train_topk = X_train_all[topk_features]
X_test_topk  = X_test_all[topk_features]

reduced_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
reduced_model.fit(X_train_topk, y_train)

y_proba_reduced = reduced_model.predict_proba(X_test_topk)[:, 1]
y_pred_reduced  = (y_proba_reduced >= 0.5).astype(int)

auc_reduced  = roc_auc_score(y_test, y_proba_reduced)
prec_reduced = precision_score(y_test, y_pred_reduced)

print(f"Reduced‐feature (top {k}) model metrics:")
print(f"  AUC-ROC:   {auc_reduced:.3f}")
print(f"  Precision: {prec_reduced:.3f}")


explainer_topk = shap.TreeExplainer(reduced_model)
shap_vals_topk = explainer_topk.shap_values(X_test_topk)[1]


plt.figure(figsize=(8, 6))
shap.summary_plot(
    shap_vals_topk,
    X_test_topk,
    feature_names=topk_features,
    plot_type="bar",
    show=False
)
plt.tight_layout()
plt.savefig("shap_topk_bar.png", dpi=150)
plt.close()
print("Saved SHAP bar chart (top k features) to shap_topk_bar.png")


reduced_importances = pd.DataFrame({
    "feature": topk_features,
    "mean_abs_shap": np.abs(shap_vals_topk).mean(axis=0)
}).sort_values("mean_abs_shap", ascending=False)

reduced_importances.to_csv("shap_feature_importances_topk.csv", index=False)
print("Saved numeric SHAP importances (topk) to shap_feature_importances_topk.csv")


X_all_topk = X_all[topk_features]
df["risk_score"] = reduced_model.predict_proba(X_all_topk)[:, 1]
df["risk_rank"]  = df["risk_score"].rank(method="first", ascending=False).astype(int)

out = df[[
    "LSOA code","year","Month_Num","risk_score","risk_rank"
]].sort_values("risk_rank")

out.to_csv("robbery_risk_by_lsoa.csv", index=False)
print("Saved risk summary to robbery_risk_by_lsoa.csv")