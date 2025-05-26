import json
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, ctx
import dash_leaflet as dl
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from soupsieve.util import lower

app = Dash(__name__)

#open the geojson file to load the map
with open('london_lsoa.geojson') as f:
    lsoa_geojson = json.load(f)
# Load the burglary data
burglary_df = pd.read_csv('burglary.csv')

#Create a dictionary such that the key is the lsoa_code and the value is a dictionary of the information of that LSOA.
data_lookup = burglary_df.set_index('LSOA code').to_dict(orient='index')

sorted_df = burglary_df.sort_values(by="Borough")

dropdown_options = [
    {
        "label": f"{row['Borough']} - {row['LSOA code']}",
        "value": row["LSOA code"]
    }
    for _, row in sorted_df.iterrows()
]

heatmap = px.choropleth_map(
    burglary_df,
    geojson=lsoa_geojson,
    locations='LSOA code',
    featureidkey='properties.LSOA21CD',
    color='Burglary_Count',
    color_continuous_scale="viridis",
    range_color = (burglary_df['Burglary_Count'].quantile(0.05), burglary_df['Burglary_Count'].quantile(0.95)),
    map_style="white-bg",
    zoom=8.85,
    opacity=0.7,
    center={"lat": 51.5074, "lon": -0.1278},
    labels={'Burglary_Count': 'Burglary Count'},
)

app.layout = html.Div(
    style={
        "display": "flex",
        "padding": "20px",
    },
    children=[
        html.Div(
            style={'display': 'flex', 'flexDirection': 'row', 'gap': '10px'},
            children=[

                html.Div(
                    style={
                        "position": "relative",
                        "width": "60vw",
                        "height": "94vh",
                        "backgroundColor": "white",
                        "boxShadow": "0 0 10px rgba(0,0,0,0.1)",
                        "borderRadius": "8px",
                        "overflow": "hidden",
                    },
                    children=[
                        dcc.Graph(
                            id="map",
                            figure=heatmap,
                            style={"width": "100%", "height": "100%"},
                            config={"displayModeBar": False},
                        ),
                        html.H1(
                            "LSOA Burglary Heatmap",
                            style={
                                "position": "absolute",
                                "top": "10px",
                                "left": "50%",
                                "transform": "translateX(-50%)",
                                "margin": 0,
                                "pointerEvents": "none",
                                "color": "rgba(0,0,0,0,0.8)",
                                "fontSize": "1.75rem",
                            },
                        ),
                    ],
                ),

                html.Div(
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "10px",
                        "width": "35vw",
                        "height": "20vh",
                        "boxShadow": "0 0 10px rgba(0,0,0,0.1)",
                        "borderRadius": "8px",
                        'backgroundColor': "white",
                        "justifyContent": "flex-start",
                        "padding": "10px",
                    },
                    children=[
                        html.Label("Search LSOA"),
                        dcc.Dropdown(
                            id='lsoa-dropdown',
                            options=dropdown_options,
                            placeholder='Select an LSOA code',
                            style={"width": "100%"}
                        ),
                        html.Button(
                            "Reset Map",
                            id="reset-button",
                            n_clicks=0,
                            style={
                                "padding": "10px",
                                "backgroundColor": "#d9534f",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "5px",
                                "cursor": "pointer"
                            }
                        ),

                        html.Div(id='search-feedback', style={"color": "black"}),
                    ],
                ),
            ],
        )
    ]
)

@app.callback(
    Output('map', 'figure'),
    Output('search-feedback', 'children'),
    Input('lsoa-dropdown', 'value'),
    Input('reset-button', 'n_clicks'),
)
def zoom_to_lsoa(code, n_clicks):
    triggered_id = ctx.triggered_id
    if triggered_id == 'reset-button' or not code:
        return heatmap, ""

    if not code:
        return heatmap, ""

    code = code.strip().upper()

    if code not in data_lookup:
        return heatmap, "LSOA code not found."

    polygon = None
    for f in lsoa_geojson['features']:
        if f['properties']['LSOA21CD'] == code:
            polygon = f
            break
    if polygon is None:
        return heatmap, f"No geometry polygon for" f"LSOA code {code}."

    coordinates = []

    def gather_coordinates(coordinate_list):
        for coordinate in coordinate_list:
            if isinstance(coordinate[0], list):
                gather_coordinates(coordinate)
            else:
                coordinates.append(coordinate)

    gather_coordinates(polygon['geometry']['coordinates'])

    longitude = [pt[0] for pt in coordinates]
    latitude = [pt[1] for pt in coordinates]
    center = {"lon": sum(longitude) / len(longitude), "lat": sum(latitude) / len(latitude)} #computing the average to get the center

    updated_heatmap = px.choropleth_map(
        burglary_df,
        geojson=lsoa_geojson,
        locations='LSOA code',
        featureidkey='properties.LSOA21CD',
        color='Burglary_Count',
        color_continuous_scale="viridis",
        range_color = (burglary_df['Burglary_Count'].quantile(0.05), burglary_df['Burglary_Count'].quantile(0.95)),
        map_style="white-bg",
        zoom=12,
        center=center,
        opacity=0.7,
        labels={'Burglary_Count': 'Burglary Count'},
    )

    lons, lats = zip(*coordinates)
    updated_heatmap.add_trace(go.Scattermap(
        lon=lons + (lons[0],),
        lat=lats + (lats[0],),
        mode='lines',
        line=dict(width=3, color='red'),
        fill=None,
        hoverinfo='skip',
        showlegend=False
    ))

    count = data_lookup[code]['Burglary_Count']
    feedback = f"LSOA {code} recorded {count} burglaries."

    return updated_heatmap, feedback


if __name__ == '__main__':
    app.run(debug=False)