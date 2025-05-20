import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import shap
import matplotlib.pyplot as plt

df = pd.read_csv("")

# split features and target
X = df.drop(columns=["is_hotspot"])
y = df["is_hotspot"]

# scale features (good for SMOTE)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# SMOTE to handle class imbalance
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_scaled, y)

X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.2, stratify=y_resampled, random_state=42
)
model = lgb.LGBMClassifier(
    boosting_type="gbdt",
    objective="binary",
    is_unbalance=True,
    n_estimators=300,
    learning_rate=0.05,
    max_depth=7,
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_probs = model.predict_proba(X_test)[:, 1]

print("Classification Report:")
print(classification_report(y_test, y_pred))

print("ROC AUC:", roc_auc_score(y_test, y_probs))
print("PR AUC (Average Precision):", average_precision_score(y_test, y_probs))

# feature importance
lgb.plot_importance(model, max_num_features=15, importance_type="gain")
plt.title("Top 15 Feature Importances")
plt.tight_layout()
plt.show()

# create SHAP explainer
explainer = shap.Explainer(model, X_train)
shap_values = explainer(X_test)

# summary plot
shap.summary_plot(shap_values, X_test, feature_names=X.columns)