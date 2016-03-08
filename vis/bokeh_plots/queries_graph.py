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

# p = figure(plot_width=600, plot_height=600, tools=[hover])
p = figure(plot_width=600, plot_height=600)

# p.circle(x, y, size=40, color="navy", alpha=0.5)
p.circle("x", "y", size=40, color="navy", alpha=0.5, source=source)
p.line([xvalues[0], xvalues[1]], [yvalues[0], yvalues[1]], line_width=2)
p.line([xvalues[1], xvalues[2]], [yvalues[1], yvalues[2]], line_width=2)
p.line([xvalues[2], xvalues[3]], [yvalues[2], yvalues[3]], line_width=2)
p.line([xvalues[3], xvalues[4]], [yvalues[3], yvalues[4]], line_width=2)


output_file("image.html", title="image.py example")
show(p)
