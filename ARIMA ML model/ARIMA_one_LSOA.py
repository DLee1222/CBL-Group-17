import numpy as np
import pandas as pd
from pmdarima import auto_arima
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt

# Load the dataset
lsoa = pd.read_csv('//data/dataset_ML (1).csv')

# Clean column names (strip spaces just in case)
lsoa.columns = lsoa.columns.str.strip()

# Pick one actual LSOA code from your dataset
print(lsoa['LSOA code'].unique()[:5])  # See first 5 available codes

# Filter data for one LSOA
single_lsoa = lsoa[lsoa['LSOA code'] == 'E01000001']  # Replace with a code from your print

# Construct datetime index from year + Month_Num
single_lsoa['Date'] = pd.to_datetime({
    'year': single_lsoa['year'],
    'month': single_lsoa['Month_Num'],
    'day': 1
})
single_lsoa.set_index('Date', inplace=True)
single_lsoa.sort_index(inplace=True)

# Optional: visualize or decompose
result = seasonal_decompose(single_lsoa['Burglary_Count'], model='multiplicative', period=12)
result.plot()
plt.show()

# Run ARIMA
stepwise_fit = auto_arima(
    single_lsoa['Burglary_Count'],
    start_p=1, start_q=1,
    max_p=3, max_q=3,
    m=12, start_P=0,
    seasonal=True,
    d=None, D=1,
    trace=True,
    error_action='ignore',
    suppress_warnings=True,
    stepwise=True
)

print(stepwise_fit.summary())