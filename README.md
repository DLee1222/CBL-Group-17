# Shared Dataset for Police Demand Forecasting – Residential Burglary in London

This repository contains the code and datasets generation pipeline for a data-driven project focused on forecasting residential burglary in London. The dataset integrates spatial, temporal, socioeconomic, and environmental information to support automated police demand forecasting.

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

The IMD scores dataset includes different IMD scores such as IMD overall, employment, barriers to housing, education, skills, and living environment scores. The dataset contains data for all London LSOA regions from 2010 to 2025, and uses copying forward and backward during the 4-year interval periods. First the data from 2010 IMD is used to fill in the years from 2010-2014, second the IMD 2015 data is used for 2015-2018, and lastly, the 2019 IMD data is used for 2019-2025. It uses data from:
| [IMD 2019](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019) | Index of Multiple Deprivation (IMD) scores and subdomains |
| [IMD 2015](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2015) | Index of Multiple Deprivation (IMD) scores and subdomains |
| [IMD 2010](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2010) | Index of Multiple Deprivation (IMD) scores and subdomains |
## Code & Tools

The dataset was created using the following tools and libraries:
- Python: `pandas`, `geopandas`, `osmnx`, `shapely`
- Data wrangling, merging, and aggregation scripts
- GitHub for version control
- PyCharm for local development

## Final Datasets Description

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


**IMD dataset column descriptions:**

** IMD Score (Overall Index)**
The IMD Score is a composite measure of relative deprivation for small areas in England, known as Lower-layer Super Output Areas (LSOAs). It combines information from seven distinct domains of deprivation, each weighted to reflect its relative importance. The overall score ranks areas from the most to the least deprived, facilitating comparisons across regions. 

** Employment Score**
This domain measures the proportion of the working-age population in an area involuntarily excluded from the labour market due to unemployment, sickness, or disability. It includes individuals who are unemployed or unable to work due to health conditions or disabilities. Indicators encompass claimants of benefits such as Jobseeker’s Allowance, Employment and Support Allowance, and Universal Credit under specific conditions. 

** Education, Skills, and Training Score**
This domain evaluates educational deprivation by examining both:
Children and Young People Sub-domain: Focuses on metrics like school attainment levels and absenteeism rates.
Adult Skills Sub-domain: Assesses the proportion of adults lacking qualifications or possessing low literacy and numeracy skills.
Together, these sub-domains reflect the flow and stock of educational disadvantage within an area. 

** Income Score**
This domain measures the proportion of the population experiencing deprivation relating to low income. The definition of low income includes both those people who are out-of-work and those who are in work but have low earnings (and who satisfy the respective means tests). The indicators which comprise this domain are: Income Support claimants, income-based Jobseeker’s Allowance claimants, income-based Employment and Support Allowance claimants, Pension Credit claimants, Working Tax Credit and Child Tax Credit recipients below a certain income threshold, and Universal Credit claimants with no income from employment. GOV.UK
 Barriers to Housing and Services Score
This domain captures challenges related to housing and access to essential services, divided into two sub-domains:
Wider Barriers: Includes issues like housing affordability, overcrowding, and homelessness.
Geographical Barriers: Assesses the physical distance to key services such as general practitioners, supermarkets, and schools. 

** Living Environment**
This domain evaluates the quality of the local environment through two sub-domains:
Indoors Living Environment: Assesses housing quality, including factors like the presence of central heating and compliance with the Decent Homes Standard.
Outdoors Living Environment: Measures external environmental factors such as air quality and road traffic accidents. 

These descriptions are based on the official definitions provided in the English Indices of Deprivation 2019 Technical Report. 

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



