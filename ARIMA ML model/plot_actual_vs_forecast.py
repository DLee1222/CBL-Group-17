import matplotlib.pyplot as plt

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
