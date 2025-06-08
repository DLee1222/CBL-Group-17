import pandas as pd
from pmdarima import auto_arima
from tqdm import tqdm

# Load the dataset
df = pd.read_csv('//data/dataset_ML (1).csv')
df.columns = df.columns.str.strip()

# Convert year + month to datetime
df['Date'] = pd.to_datetime({'year': df['year'], 'month': df['Month_Num'], 'day': 1})

# Store results
results = []

# Group by LSOA
for lsoa_code, group in tqdm(df.groupby('LSOA code'), desc="Running ARIMA for each LSOA"):

    group = group.sort_values('Date').set_index('Date')
    y = group['Burglary_Count']

    try:
        model = auto_arima(y,
                           start_p=1, start_q=1,
                           max_p=3, max_q=3,
                           m=12, seasonal=True,
                           d=None, D=1,
                           error_action='ignore',
                           suppress_warnings=True,
                           stepwise=True,
                           maxiter=20)
        results.append({
            'LSOA code': lsoa_code,
            'AIC': model.aic(),
            'Order': model.order,
            'Seasonal Order': model.seasonal_order
        })

    except Exception as e:
        results.append({
            'LSOA code': lsoa_code,
            'AIC': None,
            'Order': None,
            'Seasonal Order': None,
            'Error': str(e)
        })

# Convert results to DataFrame
results_df = pd.DataFrame(results)
results_df.to_csv('arima_summary_per_lsoa.csv', index=False)
print("✅ ARIMA results saved to arima_summary_per_lsoa.csv")