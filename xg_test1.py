import pandas as pd
import numpy as np
from datetime import timedelta
from geopy.distance import geodesic

# Load your data
crime_df = pd.read_csv("london_burglary.csv", parse_dates=['date'])
events_df = pd.read_csv("predicthq_events.csv", parse_dates=['start', 'end'])

# Assume each row in crime_df is one burglary event
# Get unique LSOAs and date range
lsoas = crime_df['lsoa'].unique()
dates = pd.date_range(start=crime_df['date'].min(), end=crime_df['date'].max(), freq='D')

# Create cartesian product of LSOA × Date
grid = pd.MultiIndex.from_product([lsoas, dates], names=['lsoa', 'date']).to_frame(index=False)
# Count burglaries per LSOA-date
burglary_counts = crime_df.groupby(['lsoa', 'date']).size().reset_index(name='burglary_count')

# Merge into grid
df = grid.merge(burglary_counts, on=['lsoa', 'date'], how='left')
df['burglary_count'] = df['burglary_count'].fillna(0)
df['burglary_occurred'] = (df['burglary_count'] > 0).astype(int)


def count_events_nearby(lsoa_row, events_df, lsoa_coords, radius_km=1.5):
    events_on_day = events_df[(events_df['start'].dt.date <= lsoa_row['date'].date()) &
                              (events_df['end'].dt.date >= lsoa_row['date'].date())]

    lsoa_coord = lsoa_coords[lsoa_row['lsoa']]
    count = 0
    attendance_sum = 0

    for _, event in events_on_day.iterrows():
        event_coord = (event['latitude'], event['longitude'])
        if geodesic(lsoa_coord, event_coord).km <= radius_km:
            count += 1
            attendance_sum += event.get('phq_attendance', 0)
    return pd.Series({'event_count': count, 'total_attendance': attendance_sum})


# Dictionary: LSOA → (lat, lon)
lsoa_coords = crime_df.groupby('lsoa')[['latitude', 'longitude']].mean().to_dict('index')

# Apply row-wise (slow, can be optimized with spatial index if needed)
event_features = df.apply(lambda row: count_events_nearby(row, events_df, lsoa_coords), axis=1)
df = pd.concat([df, event_features], axis=1)


df['day_of_week'] = df['date'].dt.dayofweek  # 0 = Monday
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
df['month'] = df['date'].dt.month


df = df.sort_values(['lsoa', 'date'])

# Grouped rolling sum over past 3 days
df['burglary_last_3days'] = (
    df.groupby('lsoa')['burglary_count']
      .rolling(window=3, min_periods=1)
      .sum().shift(1)
      .reset_index(level=0, drop=True)
)

df['burglary_last_7days'] = (
    df.groupby('lsoa')['burglary_count']
      .rolling(window=7, min_periods=1)
      .sum().shift(1)
      .reset_index(level=0, drop=True)
)


# Example weather data by date
weather_df = pd.read_csv("weather_london.csv", parse_dates=['date'])
df = df.merge(weather_df, on='date', how='left')

# Example census data per LSOA
census_df = pd.read_csv("lsoa_census.csv")
df = df.merge(census_df, on='lsoa', how='left')


# Drop rows with missing essential features if needed
df = df.dropna()

# Final features
feature_cols = ['day_of_week', 'is_weekend', 'month',
                'event_count', 'total_attendance',
                'burglary_last_3days', 'burglary_last_7days'] + \
               list(weather_df.columns.difference(['date'])) + \
               list(census_df.columns.difference(['lsoa']))

X = df[feature_cols]
y = df['burglary_occurred']
