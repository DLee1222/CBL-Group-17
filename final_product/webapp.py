import json
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
import dash_leaflet as dl
from dash.dependencies import Input, Output
from mercantile import feature

app = Dash(__name__)

#open the geojson file to load the map
with open('london_lsoa.geojson') as f:
    lsoa_geojson = json.load(f)
# Load the burglary data
burglary_df = pd.read_csv('burglary.csv')

#Create a dictionary such that the key is the lsoa_code and the value is a dictionary of the information of that LSOA.
data_lookup = burglary_df.set_index('LSOA code').to_dict(orient='index')



heatmap = px.choropleth_map(
    burglary_df,
    geojson=lsoa_geojson,
    locations='LSOA code',
    featureidkey='properties.LSOA21CD',
    color='Burglary_Count',
    color_continuous_scale="viridis",
    range_color = (10, 350),
    map_style="white-bg",
    zoom=8.85,
    opacity=0.7,
    center={"lat": 51.5074, "lon": -0.1278},
    labels={'Burglary_Count': 'Burglary Count'},
)

#whenever dash want to render the webapp layout you can find its definition in the function serve_layout
app.layout = app.layout = html.Div(
    # outer container: fill full width + center its child
    style={
        "display": "flex",
        "justifyContent": "flex-start",
        "padding": "20px",
        "backgroundColor": "#f5f5f5",
    },
    children=[
        # the “blue box” container
        html.Div(
            style= {'display': 'flex', 'flexDirection': 'column', 'gap': '10px', 'alignItems': 'center'},
            children =[
                html.H1("LSOA Burglary Heatmap", style={"margin": "0"}),

                html.Div(
                    style={
                        "display": "flex",
                        "flexDirection": "row",
                        "width": "800px",       # ← your desired box width
                        "height": "600px",      # ← your desired box height
                        "backgroundColor": "white",
                        "boxShadow": "0 0 10px rgba(0,0,0,0.1)",
                        "borderRadius": "8px",
                        "overflow": "hidden",
                    },
                    children=[
                        # map takes up most of the box
                        html.Div(
                            style={"flex": "1 1 auto"},
                            children=[
                                dcc.Graph(
                                    id="map",
                                    figure=heatmap,
                                    style={"height": "100%", "width": "100%"},
                                    config={"displayModeBar": False,},
                                    )
                                ],
                            ),
                        ],
                    )
                ],
            )
        ],
    )






if __name__ == '__main__':
    app.run(debug=False)