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
    graph_data = nx.spring_layout(graph)

    df = pd.DataFrame(graph_data)

    hover = HoverTool(
        tooltips=[
            ("query", " @query")
        ],
        names=["nodes"],
    )

    xvalues = list(df.iloc[[0]].values[0])
    yvalues = list(df.iloc[[1]].values[0])
    source = ColumnDataSource(
        data=dict(
            x=xvalues,
            y=yvalues,
            query=list(df.keys())
        )
    )

    plot = figure(plot_width=600, plot_height=600, tools=[hover])
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
