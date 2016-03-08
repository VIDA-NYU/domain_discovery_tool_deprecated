import networkx as nx

import pandas as pd

from bokeh.plotting import show, output_file, figure
from bokeh.models import ColumnDataSource, HoverTool


data = {u'ak47': 95, u'glock': 92, u'm16': 90, u'rpg': 91, u'ar15': 92, u'pkm': 92}

graph = nx.Graph()
graph.add_nodes_from(data.keys())
graph_data = nx.circular_layout(graph)

df = pd.DataFrame(graph_data)

hover = HoverTool(
    tooltips=[
        ("query", "@query")
    ]
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

p = figure(plot_width=600, plot_height=600, tools=[hover])

p.circle("x", "y", size=40, color="navy", alpha=0.5, source=source)

def add_line(df, x, y, p):
    p.line([df[x][0], df[y][0]], [df[x][1], df[y][1]])

add_line(df, "pkm", "m16", p)
add_line(df, "ak47", "glock", p)
add_line(df, "m16", "glock", p)


output_file("image.html", title="image.py example")
show(p)
