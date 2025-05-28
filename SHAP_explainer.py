import pandas as pd
import shap
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Load your saved modeling dataset
df = pd.read_csv("/datasets/Modeling_Dataset.csv")

# Prepare features and target
X = df.drop(columns=["LSOA code", "Target"])
y = df["Target"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

# Train Random Forest
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)


# Use shap.Explainer for better compatibility
explainer = shap.Explainer(model, X_train)

# Get SHAP values (3D: samples x features x classes)
shap_values = explainer(X_train)

# Extract SHAP values for class 1 (burglary hotspot)
shap_values_class1 = shap_values.values[:, :, 1]  # Shape: (n_samples, n_features)

# Convert to DataFrame
shap_df = pd.DataFrame(shap_values_class1, columns=X_train.columns)

mean_shap = shap_df.abs().mean().sort_values(ascending=False)
# Convert to DataFrame and print with percentages
shap_percent = (mean_shap / mean_shap.sum()) * 100
shap_table = pd.DataFrame({
    "Feature": shap_percent.index,
    "Contribution (%)": shap_percent.values.round(2)
})

print(shap_table)


# Pick the LSOA to explain (e.g., first one from test set)
sample_idx = 1  # change this to inspect different rows
sample = X_test.iloc[[sample_idx]]  # keep it as DataFrame

# Explain this row
explainer = shap.Explainer(model, X_train)
shap_values = explainer(sample)

# Get SHAP values for class 1
shap_vals_class1 = shap_values.values[:, :, 1].flatten()

# Combine with feature names
single_explanation = pd.DataFrame({
    "Feature": sample.columns,
    "SHAP Value (class 1)": shap_vals_class1,
    "Feature Value": sample.iloc[0].values
}).sort_values(by="SHAP Value (class 1)", key=abs, ascending=False)

print(single_explanation)
