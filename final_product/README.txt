README – Burglary Prediction Web App

Overview
--------
The final product is a Dash-based web application for visualizing historical burglary data across London’s Lower Layer Super Output Areas (LSOAs) and displaying predicted burglary counts for March 2025. The app combines interactive maps, time-series charts, and model-driven forecasts to help stakeholders explore trends and anticipate hotspots.

Required Python Libraries
-------------------------
The following libraries must be installed before running the application:

json
pandas
plotly
dash
dash_leaflet

You can install them all at once via:

pip install pandas plotly dash dash-leaflet

Data Files
----------
- final_dataset.csv  
  Contains monthly burglary counts for each LSOA from January 2011 to 2025.

- march_prediction.csv  
  Model outputs: predicted burglary count per LSOA for March 2025.

- London_lsoa11.geojson & London_lsoa21.geojson  
  GeoJSON files defining LSOA boundaries for map layers (2011 and 2021 geometries).

- assets/styles.css  
  Minor CSS tweaks to control layout.

Running the Application
-----------------------

1. Launch the webapp by running:

   webapp.py

2. Open your web browser and go to http://127.0.0.1:8050/ to interact with the dashboard.

Features
--------
- Interactive Map:  
  Visualize burglary rates per LSOA.

- Time-Series Charts:  
  View historical yearly and monthly burglary counts for selected LSOAs.

- Forecast Map:  
  Display model predictions for March 2025.

- Dynamic Controls:  
  Select date ranges, borough and ward filtering and map hover for detailed statistics.
