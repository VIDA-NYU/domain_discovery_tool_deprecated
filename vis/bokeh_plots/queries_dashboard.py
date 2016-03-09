import networkx as nx
import pandas as pd

from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import Panel, Tabs, Button, DataTable, DateFormatter, TableColumn
from bokeh.models.widgets.layouts import HBox, VBox
from bokeh.charts import Bar
from bokeh.io import vform, vplot


def queries_table(response):
    source = ColumnDataSource(data=dict(x=response.keys(), y=response.values()))
    columns = [
            TableColumn(field="x", title="Query"),
            TableColumn(field="y", title="Pages"),
        ]
    table = DataTable(source=source, columns=columns, width=400,
            height=280)
    return table


def queries_plot(response):
    graph = nx.Graph()
    graph.add_nodes_from(response.keys())
    graph_data = nx.circular_layout(graph)

    response_df = pd.DataFrame(response, index=["count"])
    graph_df = pd.DataFrame(graph_data, index=["x", "y"])
    df = pd.concat([graph_df, response_df])

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
        ),
    )

    plot = figure(plot_height=584, tools=[hover])
    plot.axis.visible = None
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    plot.circle("x", "y", size=40, color="navy", alpha=0.5, source=source,
            name="nodes")

    return plot


def queries_dashboard(response):
    table = VBox(children=[queries_table(response)])
    plot = VBox(children=[queries_plot(response)])
    return components(vplot(HBox(children=[table, plot])))
