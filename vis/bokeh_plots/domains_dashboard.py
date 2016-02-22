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


DOMAIN_PLOT_LIMIT = 10
DOMAIN_TABLE_LIMIT = None

ENDING_PLOT_LIMIT = 10
ENDING_TABLE_LIMIT = None

BAR_WIDTH = 0.4


def pages_timeseries(response):
    parse_datetime = lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f")
    parsed_dates = [parse_datetime(x[1]) for x in response]
    dates = sorted(parsed_dates)
    plot = figure(plot_width=584, x_axis_type="datetime", x_axis_label="Dates",
            y_axis_label="Number Fetched")
    plot.line(x=dates, y=range(len(dates)))
    return Panel(child=plot, title="Fetched")


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
    source = ColumnDataSource(data=dict(x=response.keys(), y=response.values()))
    queries_bar = Bar(source.data, values="y", label="x",
            title="Queries", bar_width=BAR_WIDTH,
            height=584, xlabel="Query", ylabel="Occurences")
    return queries_bar


def queries_dashboard(response):
    table = VBox(children=[queries_table(response)])
    plot = VBox(children=[queries_plot(response)])
    return components(vplot(HBox(children=[table, plot])))


def domains_dashboard(response, extra_plots=None):
    """
    Domains dashboard plot function. Takes an arguments for extra plots which
    will be added in a tab with the other plots.
    """
    # Parsed Response Data
    urls = [x[0][0] for x in response["pages"]]
    parsed_urls = [urlparse(x).hostname for x in urls]

    # Domain names Bar chart.
    domains_counter = Counter(parsed_urls).most_common(DOMAIN_PLOT_LIMIT)
    xdomains = [x[0] for x in domains_counter]
    ydomains = [y[1] for y in domains_counter]
    source_domains = ColumnDataSource(data=dict(x=xdomains, y=ydomains))

    bar_domains = Bar(source_domains.data, values="y", label="x", title="Most Common Sites by Number",
            bar_width=BAR_WIDTH, height=584, xlabel="Sites",
            ylabel="Occurences")
    panel_domains = Panel(child=bar_domains, title="Sites")

    # Domain Information Table
    table_domains_counter = Counter(parsed_urls).most_common(DOMAIN_TABLE_LIMIT)
    xdomains_table = [x[0] for x in table_domains_counter]
    ydomains_table = [y[1] for y in table_domains_counter]
    source_table_domains = ColumnDataSource(data=dict(x=xdomains_table,
        y=ydomains_table))

    columns_domain = [
            TableColumn(field="x", title="Site Name"),
            TableColumn(field="y", title="Count"),
        ]
    data_table_domain = DataTable(source=source_table_domains, columns=columns_domain, width=400,
            height=280)

    # Top level Domains Bar Chart
    endings_counter = Counter([x[x.rfind("."):] for x in parsed_urls]).most_common(ENDING_PLOT_LIMIT)
    xendings = [x[0] for x in endings_counter]
    yendings = [y[1] for y in endings_counter]
    source_top_level = ColumnDataSource(data=dict(x=xendings, y=yendings))

    bar_top_level = Bar(source_top_level.data, values="y", label="x",
            title="Most Common URL Endings by Number", bar_width=BAR_WIDTH,
            height=584, xlabel="Endings", ylabel="Occurences")
    panel_top_level = Panel(child=bar_top_level, title="Endings")

    # Top level domains table
    table_endings_counter = Counter([x[x.rfind("."):] for x in parsed_urls]).most_common(ENDING_TABLE_LIMIT)
    xendings_table = [x[0] for x in table_endings_counter]
    yendings_table = [y[1] for y in table_endings_counter]
    source_table_top_level = ColumnDataSource(data=dict(x=xendings_table, y=yendings_table))

    columns_top_level = [
            TableColumn(field="x", title="Ending"),
            TableColumn(field="y", title="Count"),
        ]
    data_table_top_level = DataTable(source=source_table_top_level,
            columns=columns_top_level, width=400, height=280)

    # Add the plots and charts to a vform and organize them with VBox and HBox
    plot_tabs = Tabs(tabs=[panel_domains, panel_top_level, extra_plots])

    # Take the two tables and the graph, turn them into VBox, then organize them
    # side by side in an HBox.
    vbox_tables = VBox(children=[data_table_domain, data_table_top_level])
    vbox_plots = VBox(children=[plot_tabs])
    hbox_dashboard = HBox(children=[vbox_tables, vbox_plots])
    return components(vplot(hbox_dashboard))
