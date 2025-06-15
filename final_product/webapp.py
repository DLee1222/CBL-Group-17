# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 11:48:18 2025

@author: 20234513
"""

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

prediction = pd.read_csv('Modified_March_2025_With_Boroughs.csv')
prediction['Predicted_Burglary_Count'] = prediction['Predicted_Burglary_Count'].round(2)

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


def allocate_officers(lsoa_code, prediction, total_officers=100):
    if not lsoa_code:
        return "Please select an LSOA code."
    
    ward_data = prediction[prediction['LSOA code'] == lsoa_code]
    if ward_data.empty:
        return f"LSOA code {lsoa_code} not found."
    
    ward_name = ward_data['WD24NM'].iloc[0]
    ward_df = prediction[prediction['WD24NM'] == ward_name].copy()
    
    # Calculate crime proportions
    ward_total_crime = ward_df['Predicted_Burglary_Count'].sum()
    ward_df['Officer_Share'] = ward_df['Predicted_Burglary_Count'] / ward_total_crime * total_officers
    ward_df['Base_Allocation'] = ward_df['Officer_Share'].apply(int)
    ward_df['Decimals'] = ward_df['Officer_Share'] - ward_df['Base_Allocation']
    
    # Ensure a minimum of 2 officers for each LSOA
    ward_df['Base_Allocation'] = ward_df['Base_Allocation'].apply(lambda x: max(x, 2))
    total_allocated = ward_df['Base_Allocation'].sum()
    remaining_officers = total_officers - total_allocated
    
    # Distribute remaining officers
    if remaining_officers > 0:
        ward_df = ward_df.sort_values(by='Decimals', ascending=False).copy()
        for i in range(remaining_officers):
            ward_df.iloc[i, ward_df.columns.get_loc('Base_Allocation')] += 1
    
    ward_df['Final_Allocation'] = ward_df['Base_Allocation']
    return ward_df[['LSOA code', 'Final_Allocation']].set_index('LSOA code').to_dict()['Final_Allocation']


# Compute allocations across all wards
all_allocations = {}

for ward in prediction['WD24NM'].dropna().unique():
    ward_df = prediction[prediction['WD24NM'] == ward]
    if not ward_df.empty:
        example_lsoa = ward_df['LSOA code'].iloc[0]
        ward_allocations = allocate_officers(example_lsoa, prediction)
        all_allocations.update(ward_allocations)

prediction['Allocated_Officers'] = prediction['LSOA code'].map(all_allocations)



prediction_map_df = prediction.rename(columns={"Predicted_Burglary_Count": "Burglary_Count"})
def generate_heatmap(df, geojson, zoom, feature_key, center={"lat": 51.5074, "lon": -0.1278},
                     color_col="Burglary_Count"):
    return px.choropleth_map(
        df,
        geojson=geojson,
        locations='LSOA code',
        featureidkey=feature_key,
        color=color_col,
        color_continuous_scale="viridis",
        range_color=(df[color_col].quantile(0.05), df[color_col].quantile(0.95)),
        map_style="open-street-map",
        zoom=zoom,
        opacity=0.7,
        center=center,
        labels={color_col: 'Burglary Count'},
    )

heatmap = generate_heatmap(burglary_df, lsoa11_geojson, zoom=8.85, feature_key="properties.LSOA11CD")


prediction_map = generate_heatmap(
    prediction_map_df,
    lsoa21_geojson,
    zoom=8.85,
    feature_key="properties.LSOA21CD"
)
# Update hover text to include officer allocation
hover_texts = prediction_map_df.apply(
    lambda row: f"LSOA: {row['LSOA code']}<br>"
                f"Burglary Count: {row['Burglary_Count']}<br>"
                f"Allocated Officers: {row['Allocated_Officers']}",
    axis=1
)

# Inject the custom hover text
prediction_map.data[0].hovertemplate = "%{customdata}"
prediction_map.data[0].customdata = hover_texts.values[:, None]


# Layout for the prediction page
prediction_layout = html.Div([
    html.Div(
        style={'display': 'flex', 'flexDirection': 'row', 'gap': '10px', 'padding': '20px'},
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
                        id='prediction-map',
                        figure=prediction_map,
                        style={"width": "100%", "height": "100%"},
                        config={"displayModeBar": False},
                    ),

                    html.H1("Burglary Prediction Map For March 2025",
                            id="prediction-map-title",
                            style={
                                "position": "absolute",
                                "top": "10px",
                                "left": "40%",
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
                style={"display': 'flex', 'backgroundColor": "f5f5f5", "flexDirection": "column", 'height': '94vh',
                       'width': '36.5vw'},
                children=[
                    html.Div(
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "10px",
                            "height": "37vh",
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
                                children=[
                                    html.Div(
                                        children=[
                                            html.Label("Filter by Borough"),
                                            dcc.Dropdown(id='prediction-borough-dropdown',
                                                         options=[{"label": b, "value": b} for b in
                                                                  sorted(prediction_map_df['Borough'].unique())],
                                                         placeholder='Select a Borough',
                                                         style={"width": "100%"}),
                                        ], style={"width": "50%"}
                                    ),
                                    html.Div(
                                        children=[
                                            html.Label("Filter by Ward"),
                                            dcc.Dropdown(id='prediction-ward-dropdown',
                                                         options=[],
                                                         placeholder='Select a Ward',
                                                         style={"width": "100%"})
                                        ], style={"width": "50%"}
                                    )
                                ],
                            ),
                            html.Label("Search LSOA"),
                            dcc.Dropdown(
                                id='prediction-lsoa-dropdown',
                                options=dropdown_options,
                                placeholder='Select an LSOA code',
                                style={"width": "100%"}
                            ),
                            html.Button(
                                "Reset Map",
                                id="prediction-reset-button",
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
                                "Back to Main Page",
                                id="back-button",
                                n_clicks=1,
                                style={
                                    "padding": "10px",
                                    "backgroundColor": "#0275d8",
                                    "color": "white",
                                    "border": "none",
                                    "borderRadius": "5px",
                                    "cursor": "pointer"
                                },
                            ),
                            html.Div(id='prediction-search-feedback', style={"color": "black"}),
                            html.Div(id='officer-allocation-output', style={"padding": "10px", "color": "black"}),

                        ],
                            
                    ),
                ],
            ),
        ]
    )
])

# Main layout
main_layout = html.Div(
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
                        "height": "95.5vh",
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
                            id="map-title",
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
                    style={"display': 'flex', 'backgroundColor": "f5f5f5", "flexDirection": "column", 'height': '94vh',
                           'width': '36.5vw'},
                    children=[
                        html.Div(
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "gap": "10px",
                                "height": "34vh",
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
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Label("Filter by Borough"),
                                                dcc.Dropdown(id='borough-dropdown',
                                                             options=[{"label": b, "value": b} for b in
                                                                      sorted(burglary_df['Borough'].unique())],
                                                             placeholder='Select a Borough',
                                                             style={"width": "100%"}),
                                            ], style={"width": "50%"}
                                        ),
                                        html.Div(
                                            children=[
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
                                    "Show burglary prediction-Map",
                                    id='burglary-prediction-button',
                                    n_clicks=1,
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
                                            "fontSize": "1rem",
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
                                        "height": "85%",
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

# Prepare prediction map figure (rename column to match heatmap function)
# layout of the main webapp
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='main-layout-container', children=main_layout),
    html.Div(id='prediction-layout-container', children=prediction_layout, style={"display": "none"})
])


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


# Callback to update the ward dropdown options based on the borough filter.
@app.callback(
    Output('ward-dropdown', 'options'),
    Input('borough-dropdown', 'value')
)
def update_ward_options(selected_borough):
    wards = burglary_df.copy()
    if not selected_borough:
        wards = burglary_df['WD24NM'].dropna().unique()

    if selected_borough:
        filtered_df = burglary_df[burglary_df['Borough'] == selected_borough]
        wards = filtered_df['WD24NM'].dropna().unique()

    return [{"label": ward, "value": ward} for ward in sorted(wards)]


# callback to update the LSOA dropdown options based on the ward and borough filter.
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


# Call back for the heatmap, search feedback, LSOA plot and its header
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
    center = {"lon": sum(lons) / len(lons), "lat": sum(lats) / len(lats)}

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
        trend_df = trend_df.groupby('Month_Num')['Burglary_Count'].sum().reindex(range(1, 13),
                                                                                 fill_value=0).reset_index()
        fig = px.bar(trend_df, x='Month_Num', y='Burglary_Count', labels={'Burglary_Count': 'Burglaries'},
                     text='Burglary_Count', color_discrete_sequence=['#4A90E2'])
        fig.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
        trend_title = f"Monthly burglary trend for LSOA {code} ({trend_start}–{trend_end})"
    else:
        trend_df = monthly_df[
            (monthly_df['LSOA code'] == code) &
            (monthly_df['Year'] >= 2011) &
            (monthly_df['Year'] <= 2025)
            ]
        trend_df = trend_df.groupby('Year')['Burglary_Count'].sum().reset_index()
        fig = px.bar(trend_df, x='Year', y='Burglary_Count', labels={'Burglary_Count': 'Burglaries'},
                     text='Burglary_Count', color_discrete_sequence=['#4A90E2'])
        trend_title = f"Yearly burglary trend for LSOA {code} 2011-2025"

    fig.update_traces(textposition='outside', marker_line_width=0, opacity=0.85)

    return updated_map, feedback, fig, year_range, code, trend_title


# Switch between pages
@app.callback(
    Output('main-layout-container', 'style'),
    Output('prediction-layout-container', 'style'),
    Input('url', 'pathname')
)
def toggle_visibility(pathname):
    if pathname == "/prediction":
        return {"display": "none"}, {"display": "block"}
    return {"display": "block"}, {"display": "none"}


# Navigate via buttons
@app.callback(
    Output('url', 'pathname'),
    Input('burglary-prediction-button', 'n_clicks'),
    Input('back-button', 'n_clicks'),
    prevent_initial_call=True
)
def navigate(pred_clicks, back_clicks):
    triggered = ctx.triggered_id
    if triggered == 'burglary-prediction-button':
        return '/prediction'
    elif triggered == 'back-button':
        return '/'


#######
######
#######
#####
########
### Callbacks for predictive page!
@app.callback(
    Output('prediction-ward-dropdown', 'options'),
    Input('prediction-borough-dropdown', 'value')
)
def update_prediction_ward_options(borough):
    if not borough:
        return []
    wards = prediction_map_df[prediction_map_df['Borough'] == borough]['WD24NM'].dropna().unique()
    return [{"label": w, "value": w} for w in sorted(wards)]


@app.callback(
    Output('prediction-lsoa-dropdown', 'options'),
    Input('prediction-borough-dropdown', 'value'),
    Input('prediction-ward-dropdown', 'value')
)
def update_prediction_lsoa_options(borough, ward):
    df = prediction_map_df.copy()
    if borough:
        df = df[df['Borough'] == borough]
    if ward:
        df = df[df['WD24NM'] == ward]

    return [{"label": f"{row['Borough']} - {row['LSOA code']}", "value": row["LSOA code"]}
            for _, row in df.iterrows()]


@app.callback(
    Output('prediction-map', 'figure'),
    Output('prediction-borough-dropdown', 'value'),
    Output('prediction-ward-dropdown', 'value'),
    Output('prediction-lsoa-dropdown', 'value'),
    Output('prediction-search-feedback', 'children'),
    Output('officer-allocation-output', 'children'),
    Input('prediction-lsoa-dropdown', 'value'),
    Input('prediction-reset-button', 'n_clicks'),
)
def update_prediction_view(code, n_clicks):
    triggered_id = ctx.triggered_id

    # Create the default map
    default_map = generate_heatmap(
        prediction_map_df,
        lsoa21_geojson,
        zoom=8.85,
        feature_key="properties.LSOA21CD"
    )
    default_map.data[0].hovertemplate = "%{customdata}"
    default_map.data[0].customdata = prediction_map_df.apply(
        lambda row: f"LSOA: {row['LSOA code']}<br>"
                    f"Burglary Count: {row['Burglary_Count']}<br>"
                    f"Allocated Officers: {row['Allocated_Officers']}",
        axis=1
    ).values[:, None]

    if triggered_id == 'prediction-reset-button' or not code:
        return (
            default_map,
            None,
            None,
            None,
            "",
            "Please select an LSOA code to see officer allocation."
        )

    polygon = next((f for f in lsoa21_geojson['features'] if f['properties']['LSOA21CD'] == code), None)
    if not polygon:
        return default_map, None, None, None, f"Geometry not found for LSOA {code}.", ""

    coordinates = []

    def gather_coords(coord_list):
        for c in coord_list:
            if isinstance(c[0], list):
                gather_coords(c)
            else:
                coordinates.append(c)

    gather_coords(polygon['geometry']['coordinates'])
    if not coordinates:
        return default_map, None, None, None, f"No coordinates for LSOA {code}.", ""

    lons, lats = zip(*coordinates)
    center = {"lon": sum(lons) / len(lons), "lat": sum(lats) / len(lats)}

    prediction_map = generate_heatmap(
        prediction_map_df,
        lsoa21_geojson,
        zoom=12,
        feature_key="properties.LSOA21CD",
        center=center
    )
    prediction_map.data[0].hovertemplate = "%{customdata}"
    prediction_map.data[0].customdata = prediction_map_df.apply(
        lambda row: f"LSOA: {row['LSOA code']}<br>"
                    f"Burglary Count: {row['Burglary_Count']}<br>"
                    f"Allocated Officers: {row['Allocated_Officers']}",
        axis=1
    ).values[:, None]

    prediction_map.add_trace(go.Scattermap(
        lon=lons + (lons[0],),
        lat=lats + (lats[0],),
        mode='lines',
        line=dict(width=3, color='red'),
        fill=None,
        hoverinfo='skip',
        showlegend=False
    ))

    df = prediction.copy()
    row = df[df['LSOA code'] == code]
    if row.empty:
        return prediction_map, None, None, code, f"No data found for LSOA {code}.", ""

    pred_value = row['Predicted_Burglary_Count'].iloc[0]
    feedback = f"Predicted number of burglaries next month in LSOA {code}: {round(pred_value, 1)}"

    allocation = allocate_officers(code, prediction)
    ward_name = row['WD24NM'].iloc[0]
    ward_df = prediction[prediction['WD24NM'] == ward_name]
    ward_total = ward_df['Predicted_Burglary_Count'].sum()

    table_rows = [
        html.Tr([
            html.Th("LSOA Code"),
            html.Th("Burglary Count"),
            html.Th("Percentage of Ward Total"),
            html.Th("Allocated Officers")
        ])
    ]

    for lsoa, officers in allocation.items():
        lsoa_data = prediction[prediction['LSOA code'] == lsoa]
        count = lsoa_data['Predicted_Burglary_Count'].iloc[0]
        percent = (count / ward_total) * 100
        row_style = {
            "backgroundColor": "#d9f2d9",
            "fontWeight": "bold"
        } if lsoa == code else {}

        table_rows.append(
            html.Tr([
                html.Td(lsoa),
                html.Td(count),
                html.Td(f"{percent:.2f}%"),
                html.Td(max(officers, 2))
            ], style=row_style)
        )

    table_rows.append(
        html.Tr([
            html.Td("Total", style={"fontWeight": "bold"}),
            html.Td(ward_total, style={"fontWeight": "bold"}),
            html.Td("100.00%", style={"fontWeight": "bold"}),
            html.Td(sum(max(o, 2) for o in allocation.values()), style={"fontWeight": "bold"})
        ])
    )

    allocation_output = html.Div([
        html.H4(f"Officer Allocation for Ward: {ward_name}", style={"marginTop": "10px"}),
        html.Table(table_rows, style={
            "width": "100%",
            "border": "1px solid black",
            "borderCollapse": "collapse",
            "textAlign": "left",
            "marginTop": "10px"
        })
    ])

    return prediction_map, None, None, code, feedback, allocation_output


if __name__ == '__main__':
    app.run(debug=False)
