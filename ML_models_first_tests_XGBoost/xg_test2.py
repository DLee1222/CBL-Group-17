import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt

# Load your CSV file
df = pd.read_csv("/data_train/dataset_ML.csv")

# Clean column names
df.columns = ['lsoa', 'year', 'month', 'burglary_count', 'imd_score', 'employment',
              'education', 'income', 'barriers', 'living_env', 'longitude', 'latitude']

# Add cyclical features
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

# Train/test split
train_df = df[df['year'] < 2016]
test_df = df[df['year'] >= 2016]

features = ['year', 'month_sin', 'month_cos', 'imd_score', 'employment', 'education',
            'income', 'barriers', 'living_env', 'longitude', 'latitude']

X_train = train_df[features]
y_train = train_df['burglary_count']

X_test = test_df[features]
y_test = test_df['burglary_count']

# XGBoost Regressor
model = xgb.XGBRegressor(
    objective='reg:squarederror',
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1
)

model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))
print("MAE:", mean_absolute_error(y_test, y_pred))

# Feature importance

fig, ax = plt.subplots()
xgb.plot_importance(model, ax=ax)
plt.title("Feature Importance")
plt.tight_layout()
plt.savefig("feature_importance.png")
