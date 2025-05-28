import pandas as pd
import shap
import xgboost as xgb

# Load your modeling dataset
df = pd.read_csv("C:/Users/20231229/PycharmProjects/simpleML/datasets/Feature_Enhanced_Modeling_Dataset.csv")

# Prepare features and labels
X = df.drop(columns=["LSOA code", "Target"])
y = df["Target"]

# Train XGBoost model
model = xgb.XGBClassifier(
    objective="binary:logistic",
    eval_metric="logloss",
    use_label_encoder=False,
    scale_pos_weight=y.value_counts()[0] / y.value_counts()[1],
    random_state=42
)
model.fit(X, y)

# SHAP explainer and values
explainer = shap.Explainer(model, X)
shap_values = explainer(X)

# Compute mean absolute SHAP values
shap_df = pd.DataFrame(shap_values.values, columns=X.columns)
mean_shap = shap_df.abs().mean().sort_values(ascending=False).reset_index()
mean_shap.columns = ["Feature", "Mean_Absolute_SHAP"]

# Save to CSV
mean_shap.to_csv("SHAP_Feature_Importance.csv", index=False)
print("Saved SHAP feature importance to SHAP_Feature_Importance.csv")
