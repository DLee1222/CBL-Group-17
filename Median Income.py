import pandas as pd
import os

# 1) Download the 2022 ASHE “Earnings by Place of Residence, Borough” CSV from ONS :contentReference[oaicite:0]{index=0}
ashe_url = (
    "https://download.ons.gov.uk/downloads/datasets/"
    "ashe-tables-7-and-8/editions/2022/versions/2.csv"
)
print("Loading ASHE borough earnings…")
# We only need these columns (inspect columns once if necessary)
usecols = [
    "Geography code",                        # borough code
    "Geography name",                        # borough name
    "All employees: Gross weekly earnings"   # median gross weekly pay
]
ashe = pd.read_csv(ashe_url, usecols=usecols)

# 2) Rename for clarity
ashe.rename(columns={
    "Geography name": "Local Authority District name",
    "All employees: Gross weekly earnings": "median_weekly_pay_2022"
}, inplace=True)

# 3) List of London boroughs (including City of London)
london_boroughs = [
    "City of London", "Barking and Dagenham", "Barnet", "Bexley",
    "Brent", "Bromley", "Camden", "Croydon", "Ealing", "Enfield",
    "Greenwich", "Hackney", "Hammersmith and Fulham", "Haringey",
    "Harrow", "Havering", "Hillingdon", "Hounslow", "Islington",
    "Kensington and Chelsea", "Kingston upon Thames", "Lambeth",
    "Lewisham", "Merton", "Newham", "Redbridge", "Richmond upon Thames",
    "Southwark", "Sutton", "Tower Hamlets", "Waltham Forest", "Wandsworth",
    "Westminster"
]

# 4) Filter to London boroughs
ashe_london = ashe[ashe["Local Authority District name"].isin(london_boroughs)].copy()
print("→ London boroughs retained:", len(ashe_london))

# 5) Save for merging
out_path = os.path.join("data", "borough_median_weekly_pay_2022.csv")
ashe_london.to_csv(out_path, index=False)
print(f"Saved London borough pay to {out_path}")