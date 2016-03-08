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
        ("desc", "@desc")
    ]
)

x = list(df.iloc[[0]].values[0])
y = list(df.iloc[[1]].values[0])
source = ColumnDataSource(
    data=dict(
        x=x,
        y=y,
        desc=list(df.keys())
    )
)

p = figure(plot_width=400, plot_height=400, tools=[hover])

# p.circle(x, y, size=40, color="navy", alpha=0.5)
p.circle("x", "y", size=40, color="navy", alpha=0.5, source=source)


output_file("image.html", title="image.py example")
show(p)
