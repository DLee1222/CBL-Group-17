import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# Load predictions
df = pd.read_csv("/test_predictions_without_covid_optimized.csv")
df['date'] = pd.to_datetime(df['date'])

# Get top 25 LSOAs by burglary count
top_lsoas = df.groupby("LSOA code")["Burglary_Count"].sum().nlargest(25).index
df = df[df["LSOA code"].isin(top_lsoas)]

# Create Plotly figure
fig = go.Figure()

# Create a trace pair (actual & predicted) for each LSOA, but make them invisible at first
buttons = []
for i, lsoa in enumerate(top_lsoas):
    lsoa_df = df[df["LSOA code"] == lsoa]

    # Actual
    fig.add_trace(go.Scatter(
        x=lsoa_df["date"],
        y=lsoa_df["Burglary_Count"],
        mode="lines",
        name=f"{lsoa} Actual",
        visible=(i == 0),
        line=dict(color="blue")
    ))

    # Predicted
    fig.add_trace(go.Scatter(
        x=lsoa_df["date"],
        y=lsoa_df["Predicted_Burglary_Count"],
        mode="lines",
        name=f"{lsoa} Predicted",
        visible=(i == 0),
        line=dict(color="red", dash="dash")
    ))

    # Button: toggle visibility for this LSOA only
    visibility = [False] * len(top_lsoas) * 2
    visibility[i * 2] = True      # actual
    visibility[i * 2 + 1] = True  # predicted

    buttons.append(dict(
        label=lsoa,
        method="update",
        args=[{"visible": visibility},
              {"title": f"Burglary Trends for {lsoa}"}]
    ))

# Update layout with dropdown menu
fig.update_layout(
    updatemenus=[dict(
        active=0,
        buttons=buttons,
        direction="down",
        showactive=True,
        x=1.05,
        y=1,
    )],
    title=f"Burglary Trends for {top_lsoas[0]}",
    xaxis_title="Date",
    yaxis_title="Burglary Count",
    legend_title="Type",
    height=600,
    width=950,
    template="plotly_white"
)

fig.show()