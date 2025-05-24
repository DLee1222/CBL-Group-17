import pandas as pd

hotspots = pd.read_csv("hot-spot.csv")
burglary = pd.read_csv("burglary_lsoa_month_2010_2025.csv")

filtered_burglary = burglary[burglary['LSOA code'].isin(hotspots['LSOA code'])]

burglary_sum = filtered_burglary.groupby('LSOA code')['Burglary_Count'].sum().reset_index()

hotspot_info = pd.merge(
    burglary_sum,
    hotspots[['LSOA code', 'Borough', 'longitude', 'latitude']],
    on='LSOA code',
    how='left'
)

hotspot_info.to_csv("hot-spot-new.csv", index=False)
