import json
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, ctx
import dash_leaflet as dl
from dash.dependencies import Input, Output
import plotly.graph_objects as go


app = Dash(__name__)


with open('london_lsoa21.geojson') as f:
    lsoa21_geojson = json.load(f)

with open('london_lsoa11.geojson') as f:
    lsoa11_geojson = json.load(f)


monthly_df = pd.read_csv('final_dataset.csv')


burglary_df = (
    monthly_df.groupby(['LSOA code', 'Borough', 'WD24NM'])
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
def generate_heatmap( df, geojson, zoom, feature_key, center = {"lat": 51.5074, "lon": -0.1278} ):
    return px.choropleth_map(
        df,
        geojson=geojson,
        locations='LSOA code',
        featureidkey= feature_key,
        color='Burglary_Count',
        color_continuous_scale="viridis",
        range_color=(df['Burglary_Count'].quantile(0.05), df['Burglary_Count'].quantile(0.95)),
        map_style="open-street-map",
        zoom=zoom,
        opacity=0.7,
        center= center,
        labels={'Burglary_Count': 'Burglary Count'},
    )

heatmap = generate_heatmap(burglary_df, lsoa11_geojson, zoom=8.85, feature_key="properties.LSOA11CD" )

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
                            id ="map-title",
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
                        html.Div(
                            style={
                                "backgroundColor": "white",
                                "height": "55vh",
                                "marginTop": "10px",
                                "boxShadow": "0 0 10px rgba(0,0,0,0.1)",
                                "borderRadius": "8px",
                                "overflow": "hidden",
                                "flexDirection": "column",
                                "padding": "10px"
                            },
                            children=[
                                html.Div(
                                    style={"display": "flex", "flexDirection": "column"},
                                    children=[
                                        html.H2(id='trend-title', style={
                                            "textAlign": "center",
                                            "margin": "10px 0",
                                            "padding": "5px",
                                            "fontSize": "1.4rem",
                                            "fontWeight": "600",
                                            "color": "#2c3e50",
                                            "borderBottom": "1px solid #ddd"
                                        }),
                                        dcc.RadioItems(
                                            id='trend-toggle',
                                            options=[
                                                {'label': 'Yearly', 'value': 'year'},
                                                {'label': 'Monthly', 'value': 'month'}
                                            ],
                                            value='year',
                                            labelStyle={'display': 'inline-block', 'marginRight': '10px'},
                                            style={'margin': '0 auto', 'textAlign': 'center'}
                                        ),
                                        html.Div(
                                            id='trend-slider-container',
                                            style={"display": "none", "padding": "10px"},
                                            children=[
                                                dcc.RangeSlider(
                                                    id='trend-year-slider',
                                                    min=2011,
                                                    max=2025,
                                                    value=[2011, 2025],
                                                    marks={str(y): str(y) for y in range(2011, 2026)},
                                                    step=1,
                                                    tooltip={'always_visible': False, 'placement': 'bottom'}
                                                )
                                            ],
                                        ),
                                    ]
                                ),
                                dcc.Graph(
                                    id='burglary-trend',
                                    style={
                                        "flex": "1",
                                        "padding": "0px",
                                        "margin": "0px",
                                        "height": "80%",
                                        "width": "100%"
                                    },
                                    config={'displayModeBar': False}
                                )
                            ]
                        ),
                    ],

                ),

            ],
       )

    ]

)

@app.callback(
    Output("map-title", "children"),
    Input("year-slider", "value"),
)
def update_map_title(year_range):
    start_year, end_year = year_range
    if start_year == end_year:
        return f"LSOA Burglary Heatmap {start_year}"
    else:
        return f"LSOA Burglary Heatmap {start_year} - {end_year}"

#Callback to update the ward dropdown options based on the borough filter.
@app.callback(
    Output('ward-dropdown', 'options'),
    Input('borough-dropdown', 'value')
)
def update_ward_options(selected_borough):
    wards =burglary_df.copy()
    if not selected_borough:
        wards = burglary_df['WD24NM'].dropna().unique()

    if selected_borough:
        filtered_df = burglary_df[burglary_df['Borough'] == selected_borough]
        wards = filtered_df['WD24NM'].dropna().unique()

    return [{"label": ward, "value": ward} for ward in sorted(wards)]


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
        filtered_df = filtered_df[filtered_df['WD24NM'] == selected_ward]

    options = [
        {"label": f"{row['Borough']} - {row['LSOA code']}", "value": row["LSOA code"]}
        for _, row in filtered_df.drop_duplicates(subset=["LSOA code"]).iterrows()
    ]
    return options

@app.callback(
    Output('trend-slider-container', 'style'),
    Input('trend-toggle', 'value')
)
def toggle_trend_slider(trend_type):
    if trend_type == 'month':
        return {"display": "block", "padding": "10px"}
    return {"display": "none"}


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
    Input('year-slider', 'value'),
    Input('trend-toggle', 'value'),  
    Input('trend-year-slider', 'value')
)
def zoom_to_lsoa(code, n_clicks, year_range, trend_view, trend_year_slider):
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

    geojson = lsoa21_geojson if start_year >= 2021 else lsoa11_geojson
    lsoa_code_key = 'properties.LSOA21CD' if start_year >= 2021 else 'properties.LSOA11CD'

    range_map = generate_heatmap(df_map, geojson, zoom=8.85, feature_key=lsoa_code_key)

    if not code:
        return range_map, "", go.Figure(), year_range, None, 'Select an LSOA to see burglary trends'

    triggered_id = ctx.triggered_id
    if triggered_id == 'reset-button':
        return range_map, "", go.Figure(), year_range, None, 'Select an LSOA to see burglary trends'

    code = code.strip().upper()
    if code not in data_lookup:
        return range_map, "LSOA code not found.", go.Figure(), year_range, code, 'Select an LSOA to see burglary trends'

    polygon = next((f for f in geojson['features'] if f['properties'].get(lsoa_code_key.split(".")[-1]) == code), None)
    if not polygon:
        return range_map, f"No geometry polygon for LSOA code {code}.", go.Figure(), year_range, code, 'Select an LSOA to see burglary trends'

    coordinates = []
    def gather_coordinates(coord_list):
        for c in coord_list:
            if isinstance(c[0], list):
                gather_coordinates(c)
            else:
                coordinates.append(c)
    gather_coordinates(polygon['geometry']['coordinates'])

    lons, lats = zip(*coordinates)
    center = {"lon": sum(lons)/len(lons), "lat": sum(lats)/len(lats)}

    updated_map = generate_heatmap(df_map, geojson, zoom=12, feature_key=lsoa_code_key, center=center)
    updated_map.add_trace(go.Scattermap(
        lon=lons + (lons[0],),
        lat=lats + (lats[0],),
        mode='lines',
        line=dict(width=3, color='red'),
        fill=None,
        hoverinfo='skip',
        showlegend=False
    ))

    series = df_map.loc[df_map['LSOA code'] == code, 'Burglary_Count']
    count = int(series.iloc[0]) if not series.empty else 0
    feedback = f"LSOA {code} recorded {count} burglaries from {start_year} to {end_year}."

    if trend_view == 'month':
        trend_start, trend_end = trend_year_slider
        trend_df = monthly_df[
            (monthly_df['LSOA code'] == code) &
            (monthly_df['Year'] >= trend_start) &
            (monthly_df['Year'] <= trend_end)
        ]
        trend_df = trend_df.groupby('Month_Num')['Burglary_Count'].sum().reindex(range(1, 13), fill_value=0).reset_index()
        fig = px.bar(trend_df, x='Month_Num', y='Burglary_Count', labels={'Burglary_Count': 'Burglaries'}, text='Burglary_Count', color_discrete_sequence=['#4A90E2'])
        fig.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
        trend_title = f"Monthly burglary trend for LSOA {code} ({trend_start}–{trend_end})"
    else:
        trend_df = monthly_df[
            (monthly_df['LSOA code'] == code) &
            (monthly_df['Year'] >= 2011) &
            (monthly_df['Year'] <= 2025)
        ]
        trend_df = trend_df.groupby('Year')['Burglary_Count'].sum().reset_index()
        fig = px.bar(trend_df, x='Year', y='Burglary_Count', labels={'Burglary_Count': 'Burglaries'}, text='Burglary_Count', color_discrete_sequence=['#4A90E2'])
        trend_title = f"Yearly burglary trend for LSOA {code} 2011-2025"

    fig.update_traces(textposition='outside', marker_line_width=0, opacity=0.85)

    return updated_map, feedback, fig, year_range, code, trend_title

if __name__ == '__main__':
    app.run(debug=False)
