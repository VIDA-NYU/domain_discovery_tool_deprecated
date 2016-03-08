# from bokeh.plotting import figure, output_file, show
# 
# data = {u'ak47': 95, u'glock': 92, u'm16': 90, u'rpg': 91, u'ar15': 92, u'pkm': 92}
# output_file("line.html")
# 
# p = figure(plot_width=400, plot_height=400)
# 
# # add a circle renderer with a size, color, and alpha
# # p.circle([0, 1.5, 3], [0, 1, 0], size=20, color="navy", alpha=0.5)
# # p.circle([0, 0, 3, 3], [0, 2, 2, 0], size=20, color="navy", alpha=0.5)
# # p.circle([0, 1, 2, 3, 4], [2, 0, 4, 0 ,2], size=20, color="navy", alpha=0.5)
# p.circle([0, 1, 2, 3, 4, 5], [0, 1, 2, 2, 1, 0], size=20, color="navy", alpha=0.5)
# 
# 
# # show the results
# show(p)
import networkx as nx

import pandas as pd

from bokeh.plotting import show, output_file, figure
from bokeh.models import ColumnDataSource


G = nx.Graph()
G.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
H = nx.circular_layout(G)
df = pd.DataFrame(H)


p = figure(plot_width=400, plot_height=400)

for x in df:
    p.circle(df[x][0], df[x][1], size=20, color="navy", alpha=0.5)

output_file("image.html", title="image.py example")
show(p)
