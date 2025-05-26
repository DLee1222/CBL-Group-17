import json
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, ctx
from dash.dependencies import Input, Output

# Initialize the app
app = Dash(__name__)

# Load geojson file
with open(r"C:\Users\20234513\Downloads\london_lsoa (4).geojson") as f:
    lsoa_geojson = json.load(f)

# Load the burglary data
burglary_df = pd.read_csv(r"C:\Users\20234513\Downloads\burglary (3).csv")

# Lookup dictionary by LSOA code
data_lookup = burglary_df.set_index('LSOA code').to_dict(orient='index')

# Sort by borough for dropdown
sorted_df = burglary_df.sort_values(by="Borough")

# Dropdown options
dropdown_options = [
    {
        "label": f"{row['Borough']} - {row['LSOA code']}",
        "value": row["LSOA code"]
    }
    for _, row in sorted_df.iterrows()
]

# App layout
app.layout = html.Div(
    style={
        "display": "flex",
        "justifyContent": "space-between",
        "padding": "20px",
        "backgroundColor": "#f5f5f5",
    },
    children=[
        # LEFT: Map section
        html.Div(
            style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px', 'alignItems': 'center'},
            children=[
                html.H1("LSOA Burglary Heatmap", style={"margin": "0"}),

                html.Div(
                    style={
                        "width": "800px",
                        "height": "600px",
                        "backgroundColor": "white",
                        "boxShadow": "0 0 10px rgba(0,0,0,0.1)",
                        "borderRadius": "8px",
                        "overflow": "hidden",
                    },
                    children=[
                        dcc.Graph(
                            id="map",
                            style={"height": "100%", "width": "100%"},
                            config={"displayModeBar": False},
                        )
                    ],
                )
            ],
        ),

        # RIGHT: Dropdown and results
        html.Div(
            style={
                "width": "300px",
                "padding": "20px",
                "backgroundColor": "white",
                "boxShadow": "0 0 10px rgba(0,0,0,0.1)",
                "borderRadius": "8px",
                "display": "flex",
                "flexDirection": "column",
                "gap": "15px",
            },
            children=[
                html.H2("Search LSOA", style={"marginBottom": "10px"}),

                dcc.Dropdown(
                    id="lsoa-dropdown",
                    options=dropdown_options,
                    placeholder="Select an LSOA code...",
                    style={"width": "100%"}
                ),

                html.Button(
                    "Reset Map",
                    id="reset-button",
                    n_clicks=0,
                    style={
                        "marginTop": "10px",
                        "padding": "10px",
                        "backgroundColor": "#d9534f",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "5px",
                        "cursor": "pointer"
                    }
                ),

                html.Div(
                    id="search-result",
                    style={"marginTop": "20px", "fontSize": "16px", "color": "#333"},
                )
            ],
        )
    ]
)



@app.callback(
    Output("map", "figure"),
    Input("lsoa-dropdown", "value"),
    Input("reset-button", "n_clicks"),
)
def update_map(selected_lsoa, reset_clicks):
    triggered_id = ctx.triggered_id

    # Add hover-friendly columns
    hover_df = burglary_df.copy()
    hover_df["hover_text"] = (
        "LSOA: " + hover_df["LSOA code"] +
        "<br>Borough: " + hover_df["Borough"] +
        "<br>Burglaries: " + hover_df["Burglary_Count"].astype(str)
    )

    # Base map
    fig = px.choropleth_mapbox(
        hover_df,
        geojson=lsoa_geojson,
        locations='LSOA code',
        featureidkey='properties.LSOA21CD',
        color='Burglary_Count',
        color_continuous_scale="viridis",
        range_color=(10, 350),
        mapbox_style="carto-positron",
        opacity=0.7,
        labels={'Burglary_Count': 'Burglary Count'},
        hover_name='hover_text',
        zoom=8.85,
        center={"lat": 51.5074, "lon": -0.1278},
    )

    # If reset button was clicked, return base map
    if triggered_id == "reset-button":
        return fig

    # If LSOA selected, zoom in and highlight
    if selected_lsoa:
        selected_row = burglary_df[burglary_df["LSOA code"] == selected_lsoa]
        if not selected_row.empty:
            lat = selected_row.iloc[0]["latitude"]
            lon = selected_row.iloc[0]["longitude"]

            fig.update_layout(
                mapbox={
                    "center": {"lat": lat, "lon": lon},
                    "zoom": 10.5,
                    "style": "carto-positron",
                    #   "uirevision": 'static'
                }
            )

            # Highlight selected LSOA with red border
            highlight_trace = px.choropleth_mapbox(
                pd.DataFrame([{
                    "LSOA code": selected_lsoa,
                    "Burglary_Count": 0
                }]),
                geojson=lsoa_geojson,
                locations="LSOA code",
                featureidkey='properties.LSOA21CD'
            ).data[0]

            highlight_trace.marker.line.color = "red"
            highlight_trace.marker.line.width = 5
            highlight_trace.marker.opacity = 0  # Hide fill

            fig.add_trace(highlight_trace)

    return fig


# Callback: Update search result panel
@app.callback(
    Output("search-result", "children"),
    Input("lsoa-dropdown", "value")
)
def update_search_result(lsoa_code):
    if not lsoa_code:
        return "Select an LSOA code above."

    data = data_lookup.get(lsoa_code.upper())
    if data:
        borough = data.get("Borough", "Unknown")
        count = data.get("Burglary_Count", "N/A")
        return [
            html.P(f"LSOA Code: {lsoa_code.upper()}"),
            html.P(f"Borough: {borough}"),
            html.P(f"Burglary Count: {count}")
        ]
    else:
        return "LSOA code not found."


# Run app
if __name__ == '__main__':
    print("🌐 App running at http://127.0.0.1:8050/")
    app.run(debug=True)
