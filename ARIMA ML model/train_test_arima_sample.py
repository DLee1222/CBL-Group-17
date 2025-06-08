import pandas as pd
import numpy as np
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# === LOAD DATA ===
df = pd.read_csv('//data/dataset_ML (1).csv')  # Replace with your file
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime({'year': df['year'], 'month': df['Month_Num'], 'day': 1})

# === FILTER LSOAs with ≥ 36 months and non-zero variance ===
valid_lsoas = []
for lsoa, group in df[df['year'] < 2020].groupby('LSOA code'):
    burglary_series = group.sort_values('Date')['Burglary_Count']
    if burglary_series.count() >= 36 and burglary_series.var() > 0:
        valid_lsoas.append(lsoa)

print(f"✅ {len(valid_lsoas)} LSOAs selected with ≥36 months of usable data")

# === TRAIN/TEST SPLIT AND MODEL FITTING ===
results = []

for lsoa in valid_lsoas:
    series = df[(df['LSOA code'] == lsoa) & (df['year'] < 2020)].copy()
    series = series.sort_values('Date').set_index('Date')
    y = series['Burglary_Count']

    # Check again: skip if all values are zero or short
    if y.count() < 36 or y.var() == 0:
        continue

    # 80/20 split
    split_idx = int(len(y) * 0.8)
    train, test = y.iloc[:split_idx], y.iloc[split_idx:]

    try:
        model = auto_arima(train, seasonal=True, m=12, suppress_warnings=True, error_action='ignore')
        forecast = model.predict(n_periods=len(test))

        rmse = mean_squared_error(test, forecast, squared=False)
        mae = mean_absolute_error(test, forecast)

        results.append({
            'LSOA code': lsoa,
            'Train Size': len(train),
            'Test Size': len(test),
            'RMSE': round(rmse, 2),
            'MAE': round(mae, 2),
            'Model Order': model.order,
            'Seasonal Order': model.seasonal_order
        })
    except Exception as e:
        results.append({
            'LSOA code': lsoa,
            'Train Size': len(train),
            'Test Size': len(test),
            'RMSE': None,
            'MAE': None,
            'Model Order': None,
            'Seasonal Order': None,
            'Error': str(e)
        })

# === SAVE RESULTS ===
results_df = pd.DataFrame(results)
results_df.to_csv('adaptive_arima_results.csv', index=False)
print("📦 Results saved to adaptive_arima_results.csv")


# Replace with one of your LSOAs
target_lsoa = 'E01000001'

# Extract series
series = df[(df['LSOA code'] == target_lsoa) & (df['year'] < 2020)].copy()
series = series.sort_values('Date').set_index('Date')['Burglary_Count']

# Split
split_idx = int(len(series) * 0.8)
train, test = series.iloc[:split_idx], series.iloc[split_idx:]

# Fit model
model = auto_arima(train, seasonal=True, m=12, suppress_warnings=True, error_action='ignore')
forecast = model.predict(n_periods=len(test))

# Plot
plt.figure(figsize=(10, 5))
plt.plot(train.index, train, label='Train')
plt.plot(test.index, test, label='Actual')
plt.plot(test.index, forecast, label='Forecast', linestyle='--')
plt.title(f"ARIMA Forecast vs Actual: {target_lsoa}")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
