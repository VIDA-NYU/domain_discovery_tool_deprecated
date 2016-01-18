from urlparse import urlparse
from collections import Counter
from operator import itemgetter
import datetime

import numpy as np

from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Panel, Tabs, Button, DataTable, DateFormatter, TableColumn
from bokeh.models.widgets.layouts import HBox, VBox
from bokeh.charts import Bar
from bokeh.io import vform, vplot


PLOT_ELEMENTS = 10
BAR_WIDTH = 0.4


def pages_timeseries_parse(response):
    parse_datetime = lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f")

    parsed_dates = [parse_datetime(x[1]).date() for x in response]
    date_counts = sorted(Counter(parsed_dates).items(), key=itemgetter(0))

    dates = [x[0] for x in date_counts]

    # Get a cumulative sum of the number of pages fetched.
    fetched = np.cumsum([y[1] for y in date_counts])

    return dates, fetched


def pages_timeseries(response):
    source = pages_timeseries_parse(response)
    plot = figure(plot_width=584, x_axis_type="datetime")
    plot.line(x=source[0], y=source[1])
    return Panel(child=plot, title="Fetched")


def domains_dashboard(response, extra_plots=None):
    """
    Domains dashboard plot function. Takes an arguments for extra plots which
    will be added in a tab with the other plots.
    """
    # Parsed Response Data
    urls = [x[0][0] for x in response["pages"]]
    parsed_urls = [urlparse(x).hostname for x in urls]

    # Domain names Bar chart.
    domains = Counter(parsed_urls).most_common(PLOT_ELEMENTS)
    xdomains = [x[0] for x in domains]
    ydomains = [y[1] for y in domains]

    source_domains = ColumnDataSource(data=dict(x=xdomains, y=ydomains))
    bar_domains = Bar(source_domains.data, values="y", label="x", title="Most Common Domains by Number",
            bar_width=BAR_WIDTH, height=584)
    panel_domains = Panel(child=bar_domains, title="Domains")

    # Domain Information Table
    columns_domain = [
            TableColumn(field="x", title="Domain"),
            TableColumn(field="y", title="Count"),
        ]
    data_table_domain = DataTable(source=source_domains, columns=columns_domain, width=400,
            height=280)

    # Top level Domains Bar Chart
    endings = Counter([x[x.rfind("."):] for x in parsed_urls]).most_common(PLOT_ELEMENTS)
    xendings = [x[0] for x in endings]
    yendings = [y[1] for y in endings]

    source_top_level = ColumnDataSource(data=dict(x=xendings, y=yendings))
    bar_top_level = Bar(source_top_level.data, values="y", label="x",
            title="Most Common URL Endings by Number", bar_width=BAR_WIDTH, height=584)
    panel_top_level = Panel(child=bar_top_level, title="Endings")

    # Top level domains table
    columns_top_level = [
            TableColumn(field="x", title="Top Level Domain"),
            TableColumn(field="y", title="Count"),
        ]
    data_table_top_level = DataTable(source=source_top_level,
            columns=columns_top_level, width=400, height=280)

    # Add the plots and charts to a vform and organize them with VBox and HBox
    plot_tabs = Tabs(tabs=[panel_domains, panel_top_level, extra_plots])

    # Take the two tables and the graph, turn them into VBox, then organize them
    # side by side in an HBox.
    vbox_tables = VBox(children=[data_table_domain, data_table_top_level])
    vbox_plots = VBox(children=[plot_tabs])
    hbox_dashboard = HBox(children=[vbox_tables, vbox_plots])
    return components(vplot(hbox_dashboard))
