import json
import pandas as pd
from dash import Dash, html, dcc
import dash_leaflet as dl
from dash.dependencies import Input, Output

app = Dash(__name__)

#open the geojson file to load the map
with open('london_lsoa.geojson') as f:
    lsoa_geojson = json.load(f)
# Load the burglary data
burglary_df = pd.read_csv('burglary.csv')

#Create a dictionary such that the key is the lsoa_code and the value is a dictionary of the information of that LSOA.
data_lookup = burglary_df.set_index('LSOA code').to_dict(orient='index')

#Create python wrapper for the GeoJSON react component
geojson_layer = dl.GeoJSON(
    data=lsoa_geojson,
    id="geojson",
    options=dict(style=dict(weight=1, color='black', fillOpacity=0.5)),
    hoverStyle={"weight": 3, "color": 'blue', "fillOpacity": 0.7},
)

def serve_layout():
    return html.Div([
        html.H1("London LSOA Burglary Map"),
        dl.Map(
            [dl.TileLayer(), geojson_layer, ],
            id="map",
            style={'width': '100%', 'height': '600px'},
            center=[51.5074, -0.1278],  # London center
            zoom=10
        ),
        html.Div(id="tooltip", style={"whiteSpace": "pre-line", "marginTop": "10px", "fontSize": "16px"}),
    ])
#whenever dash want to render the webapp layout you can find its definition in the function serve_layout
app.layout = serve_layout

def tooltip_text(feature, **kwargs):

    lsoa = feature.get('LSOA21CD')
    info = data_lookup.get(lsoa, {})
    count = info.get('Burglary_Count', 'N/A')
    print( f"LSOA: {lsoa} \n Burglary Count: {count}")
    return f"LSOA: {lsoa} \n Burglary Count: {count}"


@app.callback(
    Output("tooltip", "children"),
    Input("geojson", "clickData")
)
def update_tooltip(click_data):

    if click_data is None:
        return ""

    # click_data contains the GeoJSON feature clicked under 'feature' key
    feature = click_data.get('properties')
    print(feature)
    return tooltip_text(feature)


if __name__ == '__main__':
    app.run(debug=False)