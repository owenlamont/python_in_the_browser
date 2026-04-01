from io import StringIO

import pandas as pd
import panel as pn
import plotly.express as px
from pyscript.fetch import fetch


pn.extension("plotly", sizing_mode="stretch_width")

CSV_URL = "https://raw.githubusercontent.com/vega/vega-datasets/main/data/seattle-weather.csv"
MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
METRICS = {
    "Rainfall (mm)": "precipitation",
    "Max temperature (°C)": "temp_max",
    "Wind speed": "wind",
}


async def load_data() -> pd.DataFrame:
    response = await fetch(CSV_URL)
    csv_text = await response.text()
    frame = pd.read_csv(StringIO(csv_text), parse_dates=["date"])
    frame["year"] = frame["date"].dt.year
    frame["month"] = frame["date"].dt.strftime("%b")
    return frame


DATA = await load_data()
YEAR_OPTIONS = sorted(DATA["year"].unique().tolist())
WEATHER_OPTIONS = sorted(DATA["weather"].unique().tolist())

metric = pn.widgets.Select(name="Metric", options=list(METRICS), value="Rainfall (mm)")
years = pn.widgets.CheckButtonGroup(name="Years", options=YEAR_OPTIONS, value=YEAR_OPTIONS)
weather = pn.widgets.CheckButtonGroup(name="Weather", options=WEATHER_OPTIONS, value=WEATHER_OPTIONS)


def subset(metric_label, year_values, weather_values):
    year_values = year_values or YEAR_OPTIONS
    weather_values = weather_values or WEATHER_OPTIONS
    frame = DATA.loc[DATA["year"].isin(year_values) & DATA["weather"].isin(weather_values)].copy()
    return frame, METRICS[metric_label]


def summary(metric_label, year_values, weather_values):
    frame, column = subset(metric_label, year_values, weather_values)
    stats = frame[column].agg(["mean", "min", "max"]).round(2)
    return pn.Row(
        pn.pane.Markdown(f"### Rows\n**{len(frame)}**"),
        pn.pane.Markdown(f"### Mean\n**{stats['mean']}**"),
        pn.pane.Markdown(f"### Range\n**{stats['min']} to {stats['max']}**"),
        sizing_mode="stretch_width",
    )


def chart(metric_label, year_values, weather_values):
    frame, column = subset(metric_label, year_values, weather_values)
    fig = px.bar(
        frame,
        x="month",
        y=column,
        color="weather",
        barmode="group",
        facet_row="year",
        category_orders={"month": MONTH_ORDER},
        title=f"{metric_label} by month and weather type",
        width=1100,
        height=650,
    )
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20), autosize=False)
    return pn.pane.Plotly(
        fig,
        link_figure=False,
        config={"displayModeBar": False, "responsive": False},
        width=1100,
        height=650,
        sizing_mode="fixed",
    )


def preview(metric_label, year_values, weather_values):
    frame, column = subset(metric_label, year_values, weather_values)
    preview_frame = frame.loc[:, ["year", "month", "weather", column]].copy()
    preview_frame.columns = ["year", "month", "weather", metric_label]
    return pn.pane.DataFrame(preview_frame, index=False, height=260)


app = pn.Column(
    "# PyScript Weather Explorer",
    "A browser-only Panel app running on PyScript and Pyodide. It loads a public CSV at runtime and drives a Plotly chart using Panel widgets.",
    pn.Row(
        pn.Column("## Controls", metric, years, weather, width=280),
        pn.Column(
            pn.bind(summary, metric, years, weather),
            pn.bind(chart, metric, years, weather),
            pn.bind(preview, metric, years, weather),
            sizing_mode="stretch_width",
        ),
        sizing_mode="stretch_width",
    ),
)

app.servable(target="app")
