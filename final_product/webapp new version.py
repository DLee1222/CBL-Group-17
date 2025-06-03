import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, ctx
from dash.dependencies import Input, Output

# --- Load Data ---
app = Dash(__name__)
with open('london_lsoa.geojson') as f:
    lsoa_geojson = json.load(f)

monthly_df = pd.read_csv('final_dataset.csv')
lookup_df = pd.read_csv(LSOA_(2021)_to_Electoral_Ward_(2024)_to_LAD_(2024)_Best_Fit_Lookup_in_EW (2).csv)

# Lookup mapping
simplified_lookup = lookup_df[["LSOA21CD", "WD24CD", "WD24NM"]].dropna()
lsoa_to_ward = simplified_lookup.set_index("LSOA21CD")[["WD24CD", "WD24NM"]].to_dict(orient="index")
ward_to_lsoas = simplified_lookup.groupby("WD24CD")["LSOA21CD"].apply(list).to_dict()

burglary_df = monthly_df.groupby(['LSOA code', 'Borough'])['Burglary_Count'].sum().reset_index()
burglary_df['Ward Code'] = burglary_df['LSOA code'].map(lambda x: lsoa_to_ward.get(x, {}).get('WD24CD'))  # Add ward code
ward_totals = burglary_df.groupby('Ward Code')['Burglary_Count'].sum().to_dict()  # Precompute total burglaries per ward

data_lookup = burglary_df.set_index('LSOA code').to_dict(orient='index')
yearly_burglary = monthly_df.groupby(['LSOA code', 'Year'])['Burglary_Count'].sum().reset_index()

sorted_df = burglary_df.sort_values(by=["Borough", "LSOA code"])
dropdown_options = [
    {"label": f"{row['Borough']} - {row['LSOA code']}", "value": row["LSOA code"]}
    for _, row in sorted_df.iterrows()
]

def generate_heatmap(df, geojson, zoom, center={"lat": 51.5074, "lon": -0.1278}):
    return px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations='LSOA code',
        featureidkey='properties.LSOA11CD',
        color='Burglary_Count',
        color_continuous_scale="viridis",
        range_color=(df['Burglary_Count'].quantile(0.05), df['Burglary_Count'].quantile(0.95)),
        mapbox_style="open-street-map",
        zoom=zoom,
        center=center,
        opacity=0.7,
        labels={'Burglary_Count': 'Burglary Count'},
    )

heatmap = generate_heatmap(burglary_df, lsoa_geojson, zoom=8.85)

app.layout = html.Div(
    style={"display": "flex", "padding": "20px", "fontFamily": "'Segoe UI', sans-serif"},
    children=[
        dcc.Store(id="map-toggle", data={"show_alt": False}),  # Store for map toggle state
        html.Div(
            style={'display': 'flex', 'flexDirection': 'row', 'gap': '10px'},
            children=[
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "position": "relative",
                           "width": "60vw", "height": "105vh", "backgroundColor": "white",
                           "boxShadow": "0 0 10px rgba(0,0,0,0.1)", "borderRadius": "8px",
                           "overflow": "hidden"},
                    children=[
                        dcc.Graph(id="map", figure=heatmap, style={"width": "100%", "height": "100%"},
                                  config={"displayModeBar": True, "scrollZoom": True}),

                        html.H1("LSOA Burglary Heatmap 2011-2025", style={"position": "absolute",
                                                                         "top": "7.5px", "left": "50%",
                                                                         "transform": "translateX(-50%)",
                                                                         "margin": 0, "pointerEvents": "none",
                                                                         "color": "rgba(0,0,0,0.8)",
                                                                         "fontSize": "1.50rem"}),
                        dcc.RangeSlider(id='year-slider', min=2011, max=2025, step=1, value=[2011, 2025],
                                        marks={year: str(year) for year in range(2011, 2026)},
                                        tooltip={"placement": "bottom", "always_visible": True},
                                        allowCross=False, updatemode='mouseup'),
                        html.Button(
                            "Show burglary prediction Map",
                            id=" burglary prediction button",
                            n_clicks=0,
                            style={"padding": "10px", "margin": "10px auto", "width": "90%",
                                   "backgroundColor": "#0275d8", "color": "white",
                                   "border": "none", "borderRadius": "5px", "cursor": "pointer"},
                        ),
                    ],
                ),
                html.Div(
                    style={"backgroundColor": "#f5f5f5", "flexDirection": "column"},
                    children=[
                        html.Div(
                            style={"display": "flex", "flexDirection": "column", "gap": "10px",
                                   "width": "35.5vw", "height": "40vh", "boxShadow": "0 0 10px rgba(0,0,0,0.1)",
                                   "borderRadius": "8px", 'backgroundColor': "white", "padding": "10px"},
                            children=[
                                html.Label("Filter by Borough"),
                                dcc.Dropdown(id='borough-dropdown',
                                             options=[{"label": b, "value": b} for b in sorted(burglary_df['Borough'].unique())],
                                             placeholder='Select a Borough', style={"width": "100%"}),
                                html.Label("Search LSOA"),
                                dcc.Dropdown(id='lsoa-dropdown', options=dropdown_options,
                                             placeholder='Select an LSOA code', style={"width": "100%"}),
                                html.Button("Reset Map", id="reset-button", n_clicks=0,
                                            style={"padding": "10px", "marginTop": "10px",
                                                   "backgroundColor": "#d9534f", "color": "white",
                                                   "border": "none", "borderRadius": "5px",
                                                   "cursor": "pointer"}),
                                html.Div(id='search-feedback', style={"color": "black", "marginTop": "5px", "fontWeight": "500"}),
                            ],
                        ),
                        html.Div(
                            style={"backgroundColor": "white", "height": "65vh", 'marginTop': '10px',
                                   "boxShadow": "0 0 10px rgba(0,0,0,0.1)", "borderRadius": "8px", "overflow": "hidden",
                                   "display": "flex", "flexDirection": "column"},
                            children=[
                                html.H2(id='trend-title', style={"textAlign": "center", "margin": "10px 0 0 0",
                                                                 "padding": "5px 10px", "fontSize": "1.4rem",
                                                                 "fontWeight": "600", "color": "#2c3e50",
                                                                 "borderBottom": "1px solid #ddd"}),
                                dcc.Graph(id='burglary-trend', style={"flex": "1", "padding": "0", "margin": "0"},
                                          config={'displayModeBar': False}),
                            ],
                        ),
                    ],
                ),
            ],
        )
    ]
)


@app.callback(
    Output('lsoa-dropdown', 'options'),
    Input('borough-dropdown', 'value')
)
def update_lsoa_options(selected_borough):
    if not selected_borough:
        return dropdown_options
    return [{"label": f"{row['Borough']} - {row['LSOA code']}", "value": row["LSOA code"]}
            for _, row in sorted_df.iterrows() if row["Borough"] == selected_borough]

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
    start_year, end_year = year_range
    filtered = monthly_df[(monthly_df['Year'] >= start_year) & (monthly_df['Year'] <= end_year)]
    df_map = filtered.groupby(['LSOA code', 'Borough'])['Burglary_Count'].sum().reset_index()
    range_map = generate_heatmap(df_map, lsoa_geojson, zoom=8.85)

    if not code or ctx.triggered_id == 'reset-button':
        return heatmap, "", go.Figure(), year_range, None, "Yearly Burglary Trends"

    code = code.strip().upper()
    if code not in data_lookup:
        return range_map, "LSOA code not found.", go.Figure(), year_range, code, "Yearly Burglary Trends"

    polygon = next((f for f in lsoa_geojson['features'] if f['properties']['LSOA11CD'] == code), None)
    if not polygon:
        return heatmap, f"No geometry polygon for LSOA code {code}.", go.Figure(), year_range, code, "Yearly Burglary Trends"

    coordinates = []

    def gather_coords(coord_list):
        for coord in coord_list:
            if isinstance(coord[0], list):
                gather_coords(coord)
            else:
                coordinates.append(coord)

    gather_coords(polygon['geometry']['coordinates'])

    center = {"lon": sum(pt[0] for pt in coordinates) / len(coordinates),
              "lat": sum(pt[1] for pt in coordinates) / len(coordinates)}

    updated_heatmap = generate_heatmap(df_map, lsoa_geojson, 12, center)

    lons, lats = zip(*coordinates)
    updated_heatmap.add_trace(go.Scattermapbox(
        lon=lons + (lons[0],),
        lat=lats + (lats[0],),
        mode='lines',
        line=dict(width=5, color='red'),
        hoverinfo='skip',
        showlegend=False
    ))

    ward_info = lsoa_to_ward.get(code)
    if ward_info:
        ward_lsoas = ward_to_lsoas.get(ward_info['WD24CD'], [])
        for lsoa in ward_lsoas:
            poly = next((f for f in lsoa_geojson['features'] if f['properties']['LSOA11CD'] == lsoa), None)
            if poly:
                def extract_coords_nested(coords):
                    loops = []
                    def recurse(c):
                        if isinstance(c[0][0], (float, int)):
                            loops.append(c)
                        else:
                            for sub in c:
                                recurse(sub)
                    recurse(coords)
                    return loops

                polygons = extract_coords_nested(poly['geometry']['coordinates'])

                for coords in polygons:
                    lons, lats = zip(*coords)
                    updated_heatmap.add_trace(go.Scattermapbox(
                        lon=lons + (lons[0],),
                        lat=lats + (lats[0],),
                        mode='lines',
                        line=dict(width=3, color='blue'),
                        hoverinfo='skip',
                        showlegend=False
                    ))

    count = int(df_map.loc[df_map['LSOA code'] == code, 'Burglary_Count'].iloc[0])
    ward_code = lsoa_to_ward.get(code, {}).get('WD24CD')
    ward_total = ward_totals.get(ward_code, None)
    if ward_total:
        percent = (count / ward_total) * 100
        feedback = (f"LSOA {code} recorded {count} burglaries from {start_year} to {end_year}. "
                    f"This is {percent:.2f}% of all burglaries in its ward.")
    else:
        feedback = f"LSOA {code} recorded {count} burglaries from {start_year} to {end_year}."

    trend_df = filtered[filtered['LSOA code'] == code].groupby('Year')['Burglary_Count'].sum().reset_index()
    trend = px.bar(trend_df, x='Year', y='Burglary_Count', labels={'Burglary_Count': 'Burglaries'},
                   text='Burglary_Count', color_discrete_sequence=['#4A90E2'])
    trend.update_traces(textposition='outside', marker_line_width=0, opacity=0.85)
    trend.update_layout(margin=dict(l=20, r=20, t=30, b=20), plot_bgcolor='white', paper_bgcolor='white',
                        font=dict(size=12), xaxis=dict(showgrid=False, tickmode='linear'),
                        yaxis=dict(title='Burglaries', showgrid=True, gridcolor='#eee'),
                        uniformtext_minsize=8, uniformtext_mode='hide')

    return updated_heatmap, feedback, trend, year_range, code, f"Yearly Burglary Trends for {code}"

if __name__ == '__main__':
    app.run(debug=False)
