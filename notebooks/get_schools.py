import osmnx as ox
import geopandas as gpd
import pandas as pd

# Define London bounding box by place name
london_polygon = ox.geocoder.geocode_to_gdf("London, UK")

# Get all schools from OSM
schools = ox.features_from_polygon(london_polygon.geometry[0], tags={"amenity": "school"})

# Keep only geometry and name
schools = schools[["geometry", "name"]]
schools = schools.to_crs("EPSG:27700")  # Match UK coordinate system if needed

print(f"✅ Fetched {len(schools)} schools from OpenStreetMap")


# Load LSOA shapefile
lsoa_path = "C:/Users/20231229/PycharmProjects/shareddb_cbl/data_raw/ESRI/LSOA_2011_London_gen_MHW.shp"
lsoas = gpd.read_file(lsoa_path)

# Keep only London LSOAs
lsoas = lsoas[lsoas["LSOA11CD"].str.startswith("E01")]  # E01 = England 2011 LSOAs
lsoas = lsoas.to_crs("EPSG:27700")  # Project to British National Grid

# Spatial join: which LSOA each school falls into
schools_with_lsoa = gpd.sjoin(schools, lsoas, how="inner", predicate="within")

# Count schools per LSOA
school_counts = schools_with_lsoa.groupby("LSOA11CD").size().reset_index(name="School_Count")
school_counts = school_counts.rename(columns={"LSOA11CD": "LSOA code"})

# Preview
print(school_counts.head())


# Load your burglary + census enriched data
df = pd.read_csv("C:/Users/20231229/PycharmProjects/shareddb_cbl/data_processed/burglary_lsoa_with_social.csv")

# Merge school counts
df = df.merge(school_counts, on="LSOA code", how="left")

# Fill missing (i.e., LSOAs with 0 schools)
df["School_Count"] = df["School_Count"].fillna(0)

# Save
df.to_csv("C:/Users/20231229/PycharmProjects/shareddb_cbl/data_processed/burglary_with_schools.csv", index=False)
print("💾 School count merged successfully.")
