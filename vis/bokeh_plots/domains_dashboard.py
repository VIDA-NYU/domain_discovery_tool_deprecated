from urlparse import urlparse
from collections import Counter

from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Panel, Tabs, Button, DataTable, DateFormatter, TableColumn
from bokeh.models.widgets.layouts import HBox, VBox
from bokeh.charts import Bar
from bokeh.io import vform, vplot


PLOT_ELEMENTS = 10
BAR_WIDTH = 0.4


def domains_dashboard(response):
    # Parsed Response Data
    urls = [x[0][0] for x in response["pages"]]
    parsed_urls = [urlparse(x).hostname for x in urls]

    # Domain names Bar chart.
    domains = Counter(parsed_urls).most_common(PLOT_ELEMENTS)
    xdomains = [x[0] for x in domains]
    ydomains = [y[1] for y in domains]

    source_domains = ColumnDataSource(data=dict(x=xdomains, y=ydomains))
    bar_domains = Bar(source_domains.data, values="y", label="x", title="Most Common Domains by Number",
            bar_width=BAR_WIDTH)
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
            title="Most Common URL Endings by Number", bar_width=BAR_WIDTH)
    panel_top_level = Panel(child=bar_top_level, title="Endings")

    # Top level domains table
    columns_top_level = [
            TableColumn(field="x", title="Top Level Domain"),
            TableColumn(field="y", title="Count"),
        ]
    data_table_top_level = DataTable(source=source_top_level,
            columns=columns_top_level, width=400, height=280)

    # Add the plots and charts to a vform and organize them with VBox and HBox
    plot_tabs = Tabs(tabs=[panel_domains, panel_top_level])

    vbox_tables = VBox(children=[data_table_domain, data_table_top_level])
    vbox_plots = VBox(children=[plot_tabs])
    hbox_dashboard = HBox(children=[vbox_tables, vbox_plots])
    return components(vplot(hbox_dashboard))
