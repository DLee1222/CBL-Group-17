import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

# STEP 1: Load your modeling dataset (with the Target column)
df = pd.read_csv("/datasets/Feature_Enhanced_Modeling_Dataset.csv")

# STEP 2: Prepare input features and target
X = df.drop(columns=["LSOA code", "Target"])
y = df["Target"]

# STEP 3: Stratified train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, test_size=0.2, random_state=42
)

# STEP 4: Handle class imbalance
scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]

# STEP 5: Initialize and train XGBoost model
model = xgb.XGBClassifier(
    objective="binary:logistic",
    eval_metric="logloss",
    use_label_encoder=False,
    scale_pos_weight=scale_pos_weight,
    random_state=42
)
model.fit(X_train, y_train)

# STEP 6: Evaluate performance
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("ROC AUC Score:", roc_auc_score(y_test, y_prob))


# TESTING THE MODEL:
# STEP 1: Load the full prediction-ready dataset (no 'Target' column)
full_df = pd.read_csv("/datasets/Full_Prediction_Ready_Dataset.csv")

# STEP 2: Extract features
X_full = full_df.drop(columns=["LSOA code"])

# STEP 3: Predict probabilities using your trained model
probs = model.predict_proba(X_full)[:, 1]  # Class 1 = hotspot

# STEP 4: Combine with LSOA codes and save
predictions = pd.DataFrame({
    "LSOA code": full_df["LSOA code"],
    "Predicted_Hotspot_Probability": probs
})

# Optional: sort by highest risk
predictions = predictions.sort_values(by="Predicted_Hotspot_Probability", ascending=False)

# STEP 5: Save to CSV
predictions.to_csv("Predicted_LSOA_Hotspot_Probabilities.csv", index=False)
print("Saved predictions to Predicted_LSOA_Hotspot_Probabilities.csv")
