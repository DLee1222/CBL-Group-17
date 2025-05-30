import json
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, ctx
import dash_leaflet as dl
from dash.dependencies import Input, Output
import plotly.graph_objects as go

app = Dash(__name__)

# Load the GeoJSON map
with open('london_lsoa.geojson') as f:
    lsoa_geojson = json.load(f)

# Load the burglary data
monthly_df = pd.read_csv('final_dataset.csv')
burglary_df = (
    monthly_df.groupby(['LSOA code', 'Borough'])
    ['Burglary_Count'].sum()
    .reset_index()
)
data_lookup = burglary_df.set_index('LSOA code').to_dict(orient='index')

yearly_burglary = (
    monthly_df.groupby(['LSOA code', 'Year'])['Burglary_Count']
    .sum()
    .reset_index()
)
sorted_df = burglary_df.sort_values(by=["Borough", "LSOA code"])

# Dropdown options
dropdown_options = [
    {
        "label": f"{row['Borough']} - {row['LSOA code']}",
        "value": row["LSOA code"]
    }
    for _, row in sorted_df.iterrows()
]

# Create initial heatmap
heatmap = px.choropleth_map(
    burglary_df,
    geojson=lsoa_geojson,
    locations='LSOA code',
    featureidkey='properties.LSOA21CD',
    color='Burglary_Count',
    color_continuous_scale="viridis",
    range_color=(burglary_df['Burglary_Count'].quantile(0.05), burglary_df['Burglary_Count'].quantile(0.95)),
    map_style="open-street-map",
    zoom=8.85,
    opacity=0.7,
    center={"lat": 51.5074, "lon": -0.1278},
    labels={'Burglary_Count': 'Burglary Count'},
)

# App Layout
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
                        "display": "flex",
                        "flexDirection": "column",
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
                            "LSOA Burglary Heatmap 2011-2025",
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
                        dcc.RangeSlider(
                            id='year-slider',
                            min=2011,
                            max=2025,
                            step=1,
                            value=[2011, 2025],
                            marks={year: str(year) for year in range(2011, 2025)},
                            tooltip={"placement": "bottom", "always_visible": True},
                            allowCross=False,
                            updatemode='mouseup',
                        ),
                    ],
                ),
                html.Div(
                    style = {"backgroundColor": "#f5f5f5", "flexDirection": "column",},
                    children = [
                        html.Div(
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "gap": "10px",
                                "width": "35.5vw",
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
                        html.Div (
                            style = {
                                "backgroundColor":"white",
                                "height": "70vh",
                                'marginTop': '10px',
                                "boxShadow": "0 0 10px rgba(0,0,0,0.1)",
                                "borderRadius": "8px",
                                "overflow": "hidden",
                            },
                            children=[
                                dcc.Graph(id='burglary-trend', style={}, config={'displayModeBar': False}),
                            ],
                        ),
                    ],

                ),

            ],
       )

    ]

)





# Callback
@app.callback(
    Output('map', 'figure'),
    Output('search-feedback', 'children'),
    Output('burglary-trend', 'figure'),
    Output('year-slider', 'value'),
    Output('lsoa-dropdown', 'value'),
    Input('lsoa-dropdown', 'value'),
    Input('reset-button', 'n_clicks'),
    Input('year-slider', 'value')
)
def zoom_to_lsoa(code, n_clicks, year_range):
    DEFAULT_RANGE = [2011, 2025]
    start_year, end_year = year_range

    filtered = monthly_df[
        (monthly_df['Year'] >= start_year) &
        (monthly_df['Year'] <= end_year)
        ]

    df_map = (
        filtered
        .groupby(['LSOA code', 'Borough'])['Burglary_Count']
        .sum()
        .reset_index()
    )
    range_map = px.choropleth_map(
        df_map,
        geojson=lsoa_geojson,
        locations='LSOA code',
        featureidkey='properties.LSOA21CD',
        color='Burglary_Count',
        color_continuous_scale="viridis",
        range_color=(df_map['Burglary_Count'].quantile(0.05),
                     df_map['Burglary_Count'].quantile(0.95)),
        map_style="open-street-map",
        zoom=8.85,
        opacity=0.7,
        center={"lat": 51.5074, "lon": -0.1278},
        labels={'Burglary_Count': 'Burglary Count'},
    )

    if not code:
        empty_trend = go.Figure().update_layout(title="Select an LSOA to see yearly burglary trends")
        return range_map, "", empty_trend, year_range, None

    triggered_id = ctx.triggered_id
    if triggered_id == 'reset-button' or not code:
        empty_fig = go.Figure().update_layout(title="Select an LSOA to see yearly burglary trends")
        return heatmap, "", empty_fig, year_range, None

    code = code.strip().upper()

    if code not in data_lookup:
        empty_fig = go.Figure().update_layout(title="No data available")
        return range_map, "LSOA code not found.", empty_fig, year_range, code

    polygon = None
    for f in lsoa_geojson['features']:
        if f['properties']['LSOA21CD'] == code:
            polygon = f
            break
    if polygon is None:
        empty_fig = go.Figure().update_layout(title="No polygon found")
        return heatmap, f"No geometry polygon for LSOA code {code}.", empty_fig, year_range

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
    center = {"lon": sum(longitude) / len(longitude), "lat": sum(latitude) / len(latitude)}

    updated_heatmap = px.choropleth_map(
        df_map,
        geojson=lsoa_geojson,
        locations='LSOA code',
        featureidkey='properties.LSOA21CD',
        color='Burglary_Count',
        color_continuous_scale="viridis",
        range_color=(df_map['Burglary_Count'].quantile(0.05),df_map['Burglary_Count'].quantile(0.95)),
        map_style="open-street-map",
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
    series = df_map.loc[df_map['LSOA code'] == code, 'Burglary_Count']
    count = int(series.iloc[0])
    feedback = f"LSOA {code} recorded {count} burglaries from {start_year} to {end_year}."

    trend_df = (
        filtered[filtered['LSOA code'] == code]
        .groupby('Year')['Burglary_Count']
        .sum()
        .reset_index()
    )
    trend = px.bar(
        trend_df,
        x='Year', y='Burglary_Count',
        title=f"Yearly Burglary Trends for {code}",
        labels={'Burglary_Count': 'Burglaries'},
        text='Burglary_Count'
    )
    trend.update_traces(textposition='outside')
    trend.update_layout(uniformtext_minsize=5, uniformtext_mode='hide')


    return updated_heatmap, feedback, trend, year_range, code

if __name__ == '__main__':
    app.run(debug=False)
