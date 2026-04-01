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
    frame["month"] = pd.Categorical(frame["date"].dt.strftime("%b"), categories=MONTH_ORDER, ordered=True)
    return frame


DATA = await load_data()
metric = pn.widgets.Select(name="Metric", options=list(METRICS), value="Rainfall (mm)", width=240)


def chart(metric_label):
    column = METRICS[metric_label]
    monthly = (
        DATA.groupby("month", observed=False)[column]
        .mean()
        .reset_index()
    )
    fig = px.bar(
        monthly,
        x="month",
        y=column,
        category_orders={"month": MONTH_ORDER},
        title=f"Average monthly {metric_label.lower()}",
        labels={"month": "Month", column: metric_label},
    )
    fig.update_traces(marker_color="#1f77b4")
    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20),
        height=420,
    )
    return pn.pane.Plotly(fig, config={"displayModeBar": False, "responsive": True})


app = pn.Column(
    "# PyScript Weather Demo",
    "A minimal browser-only Panel app running on PyScript and Pyodide. It fetches a public CSV with Python, aggregates it with pandas, and renders a Plotly bar chart.",
    metric,
    pn.bind(chart, metric),
    max_width=900,
)

app.servable(target="app")
