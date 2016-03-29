from urlparse import urlparse
import itertools

import networkx as nx
import pandas as pd

from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import Panel, Tabs, Button, DataTable, DateFormatter, TableColumn
from bokeh.models.widgets.layouts import HBox, VBox
from bokeh.charts import Bar
from bokeh.io import vform, vplot


def parse_queries(queries):
    # Take the values from the queries dictionary and convert them to sets.
    for query in queries.keys():
        queries[query] = {urlparse(url).hostname for url in queries[query]}

    # Get combinations of keys in pairs of two.
    key_combos = (keys for keys in itertools.combinations(queries.keys(), r=2))

    # Create a dictionary with a key_combo as key and the result of the set
    # operation as a value.
    keys_sets = {key: tuple(queries[key[0]] & queries[key[1]]) for key in key_combos}
    return keys_sets


def queries_table(response):
    source = ColumnDataSource(data=dict(x=response.keys(), y=response.values()))
    columns = [
            TableColumn(field="x", title="Query"),
            TableColumn(field="y", title="Pages"),
        ]
    table = DataTable(source=source, columns=columns, width=400,
            height=280)
    return table


def queries_plot(response, queries_pages):
    graph = nx.Graph()
    graph.add_nodes_from(response.keys())
    graph_data = nx.circular_layout(graph)

    response_df = pd.DataFrame(response, index=["count"])
    graph_df = pd.DataFrame(graph_data, index=["x", "y"])
    df = pd.concat([graph_df, response_df])

    queries_line_data = parse_queries(queries_pages)

    hover = HoverTool(
        tooltips=[
            ("query", "@query"),
            ("count", "@count"),
        ],
        names=["nodes"],
    )

    xvalues = df.loc["x"]
    yvalues = df.loc["y"]
    source = ColumnDataSource(
        data=dict(
            x=xvalues,
            y=yvalues,
            query=df.keys(),
            count=df.loc["count"],
            sizes=df.loc["count"] / 2,
        ),
    )

    plot = figure(plot_height=584, tools=[hover, "wheel_zoom"])
    plot.axis.visible = None
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None

    # Create connection lines.
    for key in queries_line_data.keys():
        if queries_line_data[key]:
            line_width = abs(len(queries_line_data[key]) / float(len(queries_line_data.keys()))) * 2
            plot.line([df[key[0]]["x"], df[key[1]]["x"]], [df[key[0]]["y"],
                    df[key[1]]["y"]], line_width=line_width)

    plot.circle("x", "y", size="sizes", color="green", alpha=1, source=source,
            name="nodes")

    return plot


def queries_dashboard(response, queries_data):
    table = VBox(children=[queries_table(response)])
    plot = VBox(children=[queries_plot(response, queries_data)])
    return components(vplot(HBox(children=[table, plot])))
