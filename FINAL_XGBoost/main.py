import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

# === Load your processed dataset ===
df = pd.read_csv("/FINAL_XGBoost/Interpolated_Burglary_Data_With_Lags.csv")

# === Build date column ===
df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

# === Exclude COVID-affected period ===
covid_start = pd.to_datetime("2020-03-01")
covid_end = pd.to_datetime("2021-06-30")
df = df[~df['date'].between(covid_start, covid_end)]

# === Define features and target ===
features = [
    'burglary_lag_1', 'burglary_lag_2', 'burglary_lag_3', 'burglary_rolling_3',
    'IMD SCORE', 'EMPLOYMENT SCORE', 'EDUCATION SKILLS AND TRAINING SCORE',
    'INCOME SCORE', 'BARRIERS TO HOUSING AND SERVICES SCORE',
    'LIVING ENVIRONMENT SCORE', 'longitude', 'latitude', 'daylight_hours'
]
target = 'Burglary_Count'

# === Drop missing rows ===
df = df.dropna(subset=features + [target])

# === Train/test split ===
train_df = df[df['date'] < '2021-11-01']
test_df = df[df['date'] >= '2021-11-01']
X_train = train_df[features]
y_train = train_df[target]
X_test = test_df[features]
y_test = test_df[target]

# === Define model and parameter grid ===
xgb = XGBRegressor(objective='reg:squarederror', n_jobs=-1, random_state=42)

param_grid = {
    'n_estimators': [50, 100, 150],
    'max_depth': [3, 5, 7, 9],
    'learning_rate': [0.01, 0.05, 0.1, 0.2],
    'subsample': [0.6, 0.8, 1.0],
    'colsample_bytree': [0.6, 0.8, 1.0],
    'min_child_weight': [1, 3, 5]
}

# === Hyperparameter tuning ===
search = RandomizedSearchCV(
    estimator=xgb,
    param_distributions=param_grid,
    n_iter=50,
    scoring='neg_root_mean_squared_error',
    cv=3,
    verbose=2,
    random_state=42
)

print("🔍 Starting hyperparameter tuning...")
search.fit(X_train, y_train)

# === Final model ===
best_model = search.best_estimator_
print("✅ Best Parameters:", search.best_params_)

# === Predict and evaluate ===
preds = best_model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, preds))
print(f"\n📉 Final RMSE on test data: {rmse:.3f}")

# === Save predictions ===
test_df = test_df.copy()
test_df['Predicted_Burglary_Count'] = preds
test_df.to_csv("test_predictions_without_covid_optimized.csv", index=False)
print("✅ Optimized predictions saved to 'test_predictions_without_covid_optimized.csv'")
