from bokeh.layouts import column
from bokeh.models import Select, ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.server.server import Server
import pandas as pd

from .data import Data, Cache
from .constants import ROOT


def load() -> pd.DataFrame:
    cache = Cache(f"{ROOT}/.cache")
    data = Data(f"{ROOT}/.in/data.csv", cache=cache)
    df = data.load()
    df["month"] = pd.to_datetime(df["month"])

    return df


def make_dashboard(doc) -> None:
    df = load()

    # Get unique zipcodes for dropdown
    zipcodes = sorted(df["zip"].unique().astype(str))

    # Calculate overall average for all zipcodes by month
    all_data = df.groupby("month")["avg_response_time_hours"].mean().reset_index()
    all_data.columns = ["month", "avg_response_time_hours"]

    # Initial zipcode selections
    initial_zip1 = zipcodes[0] if len(zipcodes) > 0 else "00000"
    initial_zip2 = zipcodes[1] if len(zipcodes) > 1 else zipcodes[0]

    # Filter data for initial zipcodes
    zip1_data = df[df["zip"] == initial_zip1].copy()
    zip2_data = df[df["zip"] == initial_zip2].copy()

    # Create ColumnDataSources
    source_all = ColumnDataSource(
        data=dict(
            month=all_data["month"],
            avg_response_time_hours=all_data["avg_response_time_hours"],
        )
    )

    source_zip1 = ColumnDataSource(
        data=dict(
            month=zip1_data["month"],
            avg_response_time_hours=zip1_data["avg_response_time_hours"],
        )
    )

    source_zip2 = ColumnDataSource(
        data=dict(
            month=zip2_data["month"],
            avg_response_time_hours=zip2_data["avg_response_time_hours"],
        )
    )

    # Create figure
    p = figure(
        title="Monthly Average Incident Response Time (2020)",
        x_axis_label="Month",
        y_axis_label="Average Response Time (hours)",
        x_axis_type="datetime",
        width=800,
        height=400,
    )

    # Add lines
    line_all = p.line(
        "month",
        "avg_response_time_hours",
        source=source_all,
        legend_label="All Zipcodes",
        line_width=2,
        color="blue",
    )
    line_zip1 = p.line(
        "month",
        "avg_response_time_hours",
        source=source_zip1,
        legend_label=f"Zipcode {initial_zip1}",
        line_width=2,
        color="red",
    )
    line_zip2 = p.line(
        "month",
        "avg_response_time_hours",
        source=source_zip2,
        legend_label=f"Zipcode {initial_zip2}",
        line_width=2,
        color="green",
    )

    # Configure legend
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    # Create dropdowns
    select_zip1 = Select(title="Zipcode 1:", value=initial_zip1, options=zipcodes)
    select_zip2 = Select(title="Zipcode 2:", value=initial_zip2, options=zipcodes)

    # Update function
    def update():
        # Get selected zipcodes
        zip1 = select_zip1.value
        zip2 = select_zip2.value

        # Filter data for selected zipcodes
        zip1_data = df[df["zip"] == zip1].copy()
        zip2_data = df[df["zip"] == zip2].copy()

        # Update data sources
        source_zip1.data = dict(
            month=zip1_data["month"],
            avg_response_time_hours=zip1_data["avg_response_time_hours"],
        )

        source_zip2.data = dict(
            month=zip2_data["month"],
            avg_response_time_hours=zip2_data["avg_response_time_hours"],
        )

        p.legend.items[1].label = {"value": f"Zipcode {zip1}"}
        p.legend.items[2].label = {"value": f"Zipcode {zip2}"}

    # Attach callbacks
    select_zip1.on_change("value", lambda attr, old, new: update())
    select_zip2.on_change("value", lambda attr, old, new: update())

    # Create layout
    layout = column(select_zip1, select_zip2, p)

    # Add to document
    doc.add_root(layout)
    doc.title = "311 Response Time Dashboard"


def main() -> None:
    print("Starting Bokeh server...")
    server = Server({"/": make_dashboard}, port=5006)
    server.start()
    print("Dashboard available at: http://localhost:5006/")
    print("Server started. Press Ctrl+C to stop.")
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
