import pandas as pd
import numpy as np
from pmdarima import auto_arima
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# === Load dataset ===
df = pd.read_csv('//data/dataset_ML (1).csv')   # Replace with your actual CSV
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime({'year': df['year'], 'month': df['Month_Num'], 'day': 1})

# === Define LSOAs to forecast ===
target_lsoas = ['E01000001', 'E01000002', 'E01000005', 'E01032739', 'E01032740']

# === Forecast storage ===
all_forecasts = []

for lsoa in target_lsoas:
    data = df[(df['LSOA code'] == lsoa) & (df['year'] < 2020)].copy()
    data = data.sort_values('Date').set_index('Date')
    y = data['Burglary_Count']

    if y.count() < 24 or y.var() == 0:
        continue  # skip weak data

    try:
        # Fit ARIMA
        model = auto_arima(y, seasonal=True, m=12, suppress_warnings=True, error_action='ignore')

        # Forecast next 72 months (2020–2025)
        forecast = model.predict(n_periods=72)

        # Create future dates
        start = y.index[-1] + pd.DateOffset(months=1)
        future_dates = pd.date_range(start=start, periods=72, freq='MS')

        # Save results
        forecast_df = pd.DataFrame({
            'LSOA code': lsoa,
            'Date': future_dates,
            'Forecast': forecast
        })
        all_forecasts.append(forecast_df)

        # Plot
        plt.figure(figsize=(10, 5))
        plt.plot(y.index, y, label='Historical')
        plt.plot(future_dates, forecast, label='Forecast', linestyle='--')
        plt.title(f"Forecast (2020–2025) for LSOA: {lsoa}")
        plt.xlabel("Date")
        plt.ylabel("Burglary Count")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'forecast_{lsoa}.png')
        plt.close()

        print(f"✅ Forecast saved and plotted for {lsoa}")

    except Exception as e:
        print(f"❌ Failed for {lsoa}: {e}")

# === Save all forecasts to CSV ===
if all_forecasts:
    combined_df = pd.concat(all_forecasts)
    combined_df.to_csv('post_covid_forecasts.csv', index=False)
    print("📦 All forecasts saved to post_covid_forecasts.csv")
