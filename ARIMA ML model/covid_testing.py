import pandas as pd
from pmdarima import auto_arima

# === Load data ===
file_path = '//data/dataset_ML (1).csv'  # Replace with your file path
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime({'year': df['year'], 'month': df['Month_Num'], 'day': 1})

# === Find LSOAs with both pre-COVID and COVID data ===
pre_years = list(range(2010, 2020))
covid_years = [2020, 2021, 2022]

lsoas_pre = set(df[df['year'].isin(pre_years)]['LSOA code'].unique())
lsoas_covid = set(df[df['year'].isin(covid_years)]['LSOA code'].unique())
lsoas_with_both = list(lsoas_pre & lsoas_covid)[:19]

# === Compare ARIMA fits ===
results = []

for code in lsoas_with_both:
    data = df[df['LSOA code'] == code].sort_values('Date')
    full_series = data.set_index('Date')['Burglary_Count']
    pre_series = data[data['year'] <= 2019].set_index('Date')['Burglary_Count']

    try:
        model_full = auto_arima(full_series, seasonal=True, m=12, suppress_warnings=True, error_action='ignore')
        aic_full = model_full.aic()
    except:
        aic_full = None

    try:
        model_pre = auto_arima(pre_series, seasonal=True, m=12, suppress_warnings=True, error_action='ignore')
        aic_pre = model_pre.aic()
    except:
        aic_pre = None

    results.append({
        'LSOA code': code,
        'AIC (Full Data)': aic_full,
        'AIC (Pre-COVID Only)': aic_pre,
        'Δ AIC (Pre - Full)': round(aic_pre - aic_full, 2) if aic_full and aic_pre else None
    })

# === Save results ===
results_df = pd.DataFrame(results)
results_df.to_csv('arima_comparison_results.csv', index=False)
print("✅ Comparison complete. Results saved to 'arima_comparison_results.csv'")
