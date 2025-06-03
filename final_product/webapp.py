import json
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, ctx
import dash_leaflet as dl
from dash.dependencies import Input, Output
import plotly.graph_objects as go

app = Dash(__name__)


with open('london_lsoa.geojson') as f:
    lsoa_geojson = json.load(f)


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

dropdown_options = [
    {
        "label": f"{row['Borough']} - {row['LSOA code']}",
        "value": row["LSOA code"]
    }
    for _, row in sorted_df.iterrows()
]
def generate_heatmap( df, geojson, zoom, center = {"lat": 51.5074, "lon": -0.1278} ):
    return px.choropleth_map(
        df,
        geojson=geojson,
        locations='LSOA code',
        featureidkey='properties.LSOA11CD',
        color='Burglary_Count',
        color_continuous_scale="viridis",
        range_color=(df['Burglary_Count'].quantile(0.05), df['Burglary_Count'].quantile(0.95)),
        map_style="open-street-map",
        zoom=zoom,
        opacity=0.7,
        center= center,
        labels={'Burglary_Count': 'Burglary Count'},
    )

heatmap = generate_heatmap(burglary_df, lsoa_geojson, zoom=8.85)

# App Layout
app.layout = html.Div(
    style={
        "display": "flex",
        "padding": "20px",
    },
    children=[
        dcc.Store(id="map-toggle", data={"show_alt": False}),
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
                    style = {"display': 'flex', 'backgroundColor": "f5f5f5", "flexDirection": "column", 'height':'94vh', 'width':'36.5vw'},
                    children = [
                        html.Div(
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "gap": "10px",
                                "height": "35vh",
                                "boxShadow": "0 0 10px rgba(0,0,0,0.1)",
                                "borderRadius": "8px",
                                'backgroundColor': "white",
                                "justifyContent": "flex-start",
                                "padding": "10px",
                            },
                            children=[
                                html.Div(
                                    style={
                                        "display": "flex",
                                        "flexDirection": "row",
                                        "gap": "10px"},
                                    children =[
                                        html.Div(
                                            children =[
                                                html.Label("Filter by Borough"),
                                                dcc.Dropdown(id='borough-dropdown',
                                                options=[{"label": b, "value": b} for b in sorted(burglary_df['Borough'].unique())],
                                                placeholder='Select a Borough',
                                                style={"width": "100%"}),
                                            ], style={"width": "50%"}
                                        ),
                                        html.Div(
                                            children =[
                                                html.Label("Filter by Ward"),
                                                dcc.Dropdown(id='ward-dropdown',
                                                options=[],
                                                placeholder='Select a Ward',
                                                style={"width": "100%"})
                                            ], style={"width": "50%"}
                                        )
                                    ],
                                ),
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
                                html.Button(
                                    "Show burglary prediction Map",
                                    id=" burglary prediction button",
                                    n_clicks=0,
                                    style={
                                        "padding": "10px",
                                        "backgroundColor": "#0275d8",
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "5px",
                                        "cursor": "pointer"
                                    },
                                ),
                                html.Div(id='search-feedback', style={"color": "black"}),
                            ],
                        ),
                        html.Div (
                            style = {
                                "backgroundColor":"white",
                                "height": "55vh",
                                'marginTop': '10px',
                                "boxShadow": "0 0 10px rgba(0,0,0,0.1)",
                                "borderRadius": "8px",
                                "overflow": "hidden",
                                "flexDirection": "column",
                            },
                            children=[
                                html.H2(
                                    id='trend-title',
                                    style={
                                        "textAlign": "center",
                                        "margin": "10px 0 0 0",
                                        "padding": "5px 10px",
                                        "fontSize": "1.4rem",
                                        "fontWeight": "600",
                                        "color": "#2c3e50",
                                        "borderBottom": "1px solid #ddd"
                                    }
                                ),
                                dcc.Graph(
                                    id='burglary-trend',
                                    style={
                                        "flex": "1",
                                        "padding": "0px",
                                        "margin": "0px",
                                        "height": "100%",
                                        "width": "100%"
                                    },
                                    config={'displayModeBar': False}
                                )
                            ],
                        ),
                    ],

                ),

            ],
       )

    ]

)
#Callback to update the ward dropdown options based on the borough filter.
@app.callback(
    Output('ward-dropdown', 'options'),
    Input('borough-dropdown', 'value')
)
def update_ward_options(selected_borough):
    if not selected_borough:
        return []

    filtered_df = burglary_df[burglary_df['Borough'] == selected_borough]
    #Once the ward column is added to the final_dataset file, this section will be enabled.
    # options =[
    #     {"label": ward, "value": ward}
    #     for ward in sorted(filtered_df['Ward'].dropna().unique())
    # ]
    #return options

#callback to update the LSOA dropdown options based on the ward and borough filter.
@app.callback(
    Output('lsoa-dropdown', 'options'),
    Input('borough-dropdown', 'value'),
    Input('ward-dropdown', 'value')
)
def update_lsoa_options(selected_borough, selected_ward):
    filtered_df = burglary_df.copy()

    if selected_borough:
        filtered_df = burglary_df[burglary_df['Borough'] == selected_borough]
    if selected_ward:
        pass
        #this will be enabled when the final_dataset file contains ward information for each LSOA.
        #filtered_df= burglary_df[burglary_df['Ward'] == selected_ward]

    options = [
        {"label": f"{row['Borough']} - {row['LSOA code']}", "value": row["LSOA code"]}
        for _, row in filtered_df.drop_duplicates(subset=["LSOA code"]).iterrows()
    ]
    return options


#Call back for the heatmap, search feedback, LSOA plot and its header
@app.callback(
    Output('map', 'figure'),
    Output('search-feedback', 'children'),
    Output('burglary-trend', 'figure'),
    Output('year-slider', 'value'),
    Output('lsoa-dropdown', 'value'),
    Output('trend-title', 'children'),
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
    range_map = generate_heatmap(df_map, lsoa_geojson, zoom=8.85)


    if not code:
        empty_trend = go.Figure()
        return range_map, "", empty_trend, year_range, None, 'Select an LSOA to see yearly burglary trends'

    triggered_id = ctx.triggered_id
    if triggered_id == 'reset-button' or not code:
        empty_fig = go.Figure()
        return heatmap, "",  empty_fig, year_range, None, 'Select an LSOA to see yearly burglary trends'

    code = code.strip().upper()

    if code not in data_lookup:
        empty_fig = go.Figure()
        return range_map, "LSOA code not found.", empty_fig, year_range, code, 'Select an LSOA to see yearly burglary trends'

    #This section finds the polygon for the selected LSOA code
    polygon = None
    for f in lsoa_geojson['features']:
        if f['properties']['LSOA11CD'] == code:
            polygon = f
            break
    if polygon is None:
        empty_fig = go.Figure()
        return heatmap, f"No geometry polygon for LSOA code {code}.", empty_fig, year_range, code, 'Select an LSOA to see yearly burglary trends'

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

    updated_heatmap = generate_heatmap(df_map, lsoa_geojson, 12, center)

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
        labels={'Burglary_Count': 'Burglaries'},
        text='Burglary_Count',
        color_discrete_sequence = ['#4A90E2']
    )
    trend.update_traces(textposition='outside', marker_line_width=0, opacity=0.85)
    return updated_heatmap, feedback, trend, year_range, code, f'yearly burglary trend for LSOA {code}'

if __name__ == '__main__':
    app.run(debug=False)
