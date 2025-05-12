# Shared Dataset for Police Demand Forecasting – Residential Burglary in London

This repository contains the code and dataset generation pipeline for a data-driven project focused on forecasting residential burglary in London. The dataset integrates spatial, temporal, socioeconomic, and environmental information to support automated police demand forecasting.

## Project Aim

The aim of this dataset is to support:
- Forecasting the risk and volume of residential burglaries
- Strategic police resource allocation by location and time
- Analysis of factors contributing to burglary patterns across London

## Data Sources Used

The final dataset combines the following official and publicly available sources:

| Source | Description |
|--------|-------------|
| [data.police.uk](https://data.police.uk/) | Monthly police-recorded crime data for London (2016–present) |
| [ONS Census 2021](https://www.ons.gov.uk/census) | Demographics, housing, occupation, and industry per LSOA |
| [IMD 2019](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019) | Index of Multiple Deprivation (IMD) scores and subdomains |
| [OpenStreetMap](https://www.openstreetmap.org/) | Geographic location of schools |
| UK Solar Data | Monthly daylight hour estimates for London, derived from solar calculations |

## Code & Tools

The dataset was created using the following tools and libraries:
- Python: `pandas`, `geopandas`, `osmnx`, `shapely`
- Data wrangling, merging, and aggregation scripts
- GitHub for version control
- PyCharm for local development

## Final Dataset Description

Each row in the final dataset represents one month for one LSOA (Lower Layer Super Output Area) in London. The columns include:

### Temporal and Spatial Identifiers
| Column | Description |
|--------|-------------|
| `LSOA code` | Unique 2011 LSOA identifier (e.g. E01000001) |
| `Year` | Calendar year of observation (e.g. 2018) |
| `Month_Num` | Numeric month (1 = January, ..., 12 = December) |

### Crime Data
| Column | Description |
|--------|-------------|
| `Burglary_Count` | Number of recorded residential burglaries in that LSOA and month |

### Deprivation and Socioeconomic Indicators
| Column | Description |
|--------|-------------|
| `IMD_Score` | Index of Multiple Deprivation score (higher = more deprived) |
| `Income_Score` | Income deprivation score |
| `Employment_Score` | Employment deprivation score |
| `Crime_Score` | Crime deprivation score (subdomain of IMD) |

### Census 2021: Ethnic Group Counts
| Column | Description |
|--------|-------------|
| `Eth_Bangladeshi`, `Eth_Chinese`, `Eth_Indian`, etc. | Count of people in each ethnic group in the LSOA (Census 2021) |

### Census 2021: Occupation (NS-SeC Categories)
| Column | Description |
|--------|-------------|
| `NSSEC_HigherManagerial` | Higher managerial, administrative, and professional occupations |
| `NSSEC_LowerManagerial` | Lower managerial and professional occupations |
| Other categories may be added if needed |

### Census 2021: Industry
| Column | Description |
|--------|-------------|
| `Ind_Manufacturing`, `Ind_Construction`, `Ind_Distribution`, etc. | Number of people working in each industry group (Census 2021 categories) |

### Environment and Accessibility
| Column | Description |
|--------|-------------|
| `School_Count` | Number of schools located within the LSOA (based on OpenStreetMap) |
| `Precise_Daylight_Hours` | Average number of daylight hours in the month (based on solar data for London) |

### Census 2021: Housing and Accommodation
| Column | Description |
|--------|-------------|
| `House_Detached`, `House_SemiDetached`, `Flat_Apartment` | Number of homes of each housing type |
| `Tenure_OwnedOutright`, `Tenure_SocialRented`, `Tenure_PrivateRented`, etc. | Count of households by tenure type |
| `RoomDensity_Low` | Households with up to 1 person per room (not overcrowded) |
| `RoomDensity_Medium` | Households with 1 to 1.5 people per room |
| `RoomDensity_High` | Households with more than 1.5 people per room (overcrowded) |

> Note: Most census features are static (from 2021), repeated for each monthly row.

## Intended Uses

This dataset is designed to support:
- Predictive modeling (machine learning forecasting of burglary risk)
- Statistical exploration and risk factor analysis
- Visual mapping of spatial trends
- Ethical evaluation of data-driven policing

## Ethical Considerations

This dataset:
- Aggregates data to a non-personal, neighborhood level (LSOA)
- Includes social context to avoid reinforcing biased policing
- Promotes fairness, transparency, and ethical forecasting

## Repository Structure

| Folder | Description |
|--------|-------------|
| `data_raw/` | Original downloaded data sources |
| `data_processed/` | Final and intermediate datasets, including the enriched panel data |
| `README.md` | This documentation |
| Scripts (optional) | Python files used to generate and merge the datasets |



