from collections import Counter
from itertools import chain, combinations

from bokeh.charts import Bar
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.io import VBox
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models import ColumnDataSource, CustomJS, DatetimeTickFormatter, HoverTool
import networkx as nx
import numpy as np
import pandas as pd
from urlparse import urlparse

from .utils import DATETIME_FORMAT, empty_plot_on_empty_df

MIN_BORDER=10

js_callback = CustomJS(code="""
    var data_table_ids = ['urls', 'tlds', 'tags', 'queries'];

    setTimeout(function() { //need timeout to wait for class change
      var global_state = {};
      for (i=0; i<data_table_ids.length; i++) {
        global_state[data_table_ids[i]] = get_table_state(data_table_ids[i]);
      }

      global_state['datetimepicker_start'] = $('#datetimepicker_start').data('date') || ''
      global_state['datetimepicker_end'] = $('#datetimepicker_end').data('date') || ''
      $.ajax({
        type: "POST",
        url: '/update_cross_filter_plots' + window.location.search, //session info
        data: JSON.stringify(global_state),
        contentType: "application/json",
        dataType: "json",
        success: function(response) {
          $("#plot_area").html(response);
        }
      });
    }, 10);

    var get_table_state = function(id) {
      var current = $("#".concat(id)).find(".bk-slick-cell.l0.selected");
      var active_cells = [];
      for (j = 0; j < current.length; j++) {
        active_cells.push(current[j].innerText);
      }
      return active_cells;
    };
""")

def parse_es_response(response):
    df = pd.DataFrame(response, columns=['query', 'retrieved', 'url', 'tag'])
    df['query'] = df['query'].apply(lambda x: x[0])
    df['retrieved'] = pd.DatetimeIndex(df.retrieved.apply(lambda x: x[0]))
    df['url'] = df.url.apply(lambda x: x[0])
    df['hostname'] = [urlparse(x).hostname.lstrip('www.') for x in df.url]
    df['tld'] = [x[x.rfind('.'):] for x in df.hostname]
    df['tag'] = df.tag.apply(lambda x:"" if isinstance(x, float) else x[0]) # fill nan with []

    return df.set_index('retrieved').sort_index()

def calculate_graph_coords(df, groupby_column):
    df2 = df.groupby(groupby_column).count().sort_index()

    graph = nx.Graph()
    graph.add_nodes_from(df2.index)
    graph_coords = nx.circular_layout(graph)

    return pd.concat([df2, pd.DataFrame(graph_coords, index=["x", "y"]).T], axis=1)

def calculate_query_correlation(df, groupby_column):
    key_combos = combinations(df[groupby_column].unique(), r=2)

    correlation = dict()

    for i in key_combos:
        k0 = df[df[groupby_column].isin([i[0]])]['hostname']
        k1 = df[df[groupby_column].isin([i[1]])]['hostname']
        correlation[i] = len(set(k0).intersection(k1))
    return correlation

@empty_plot_on_empty_df
def most_common_url_bar(df, plot_width=600, plot_height=200, top_n=10):

    bars = df[['hostname','url']].groupby('hostname').count().sort_values('url', ascending=False)
    bars['y'] = bars.url / 2.

    if top_n:
        bars = bars.iloc[:top_n]

    source = ColumnDataSource(bars)

    p = figure(plot_width=plot_width, plot_height=plot_height,
               tools='box_zoom, reset',
               min_border_left=50, min_border_right=50,
               min_border_top=MIN_BORDER, min_border_bottom=MIN_BORDER,
               x_range=(0,bars.url.max()), y_range=bars.index.tolist()[::-1]
               )
    p.ygrid.grid_line_color = None
    p.xaxis.axis_label = "Frequency of Pages Scraped"
    p.logo=None

    p.rect(x='y', y='hostname', height=0.8, width='url', source=source)

    return p

@empty_plot_on_empty_df
def site_tld_bar(df, plot_width=600, plot_height=200):

    bars = df[['tld','url']].groupby('tld').count().sort_values('url', ascending=False)
    bars['y'] = bars.url / 2.

    source = ColumnDataSource(bars)

    p = figure(plot_width=plot_width, plot_height=plot_height,
               tools='box_zoom, reset',
               min_border_left=50, min_border_right=50,
               min_border_top=MIN_BORDER, min_border_bottom=MIN_BORDER,
               x_range=(0,bars.url.max()), y_range=bars.index.tolist()[::-1]
               )
    p.ygrid.grid_line_color = None
    p.xaxis.axis_label = "Site TLDS"
    p.logo=None

    p.rect(x='y', y='tld', height=0.8, width='url', source=source)

    return p

@empty_plot_on_empty_df
def pages_queried_timeseries(df, plot_width=600, plot_height=200, rule='1T'):

    ts = df[['url']].resample(rule, how='count').cumsum()

    ts = pd.concat([ts[:1], ts]) # prepend 0-value for Line chart compat
    ts.iloc[0]['url'] = 0

    source = ColumnDataSource(ts)

    p = figure(plot_width=plot_width, plot_height=plot_height,
               x_axis_type='datetime', tools='box_zoom, reset',
               min_border_left=MIN_BORDER, min_border_right=MIN_BORDER,
               min_border_top=MIN_BORDER, min_border_bottom=MIN_BORDER)
    p.logo=None
    p.xaxis[0].formatter = DatetimeTickFormatter(formats=DATETIME_FORMAT)
    p.yaxis.axis_label = "Pages Queried"

    p.line(x='retrieved', y='url', line_width=3, line_alpha=0.8, source=source)

    return p

@empty_plot_on_empty_df
def queries_plot(df, plot_width=600, plot_height=300):
    df2 = calculate_graph_coords(df, 'query')

    source = ColumnDataSource(df2)

    line_coords = calculate_query_correlation(df, 'query')

    hover = HoverTool(
        tooltips=[
            ("Query", "@query"),
            ("No. Results", "@url"),
        ],
        names=["nodes"],
    )

    plot = figure(plot_width=plot_width, plot_height=plot_height,
                  tools=[hover, "wheel_zoom", "reset"])
    plot.axis.visible = None
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    plot.logo = None

    # Create connection lines.
    for k, v in line_coords.items():
        plot.line([df2.loc[k[0]]['x'], df2.loc[k[1]]['x']],
                  [df2.loc[k[0]]['y'], df2.loc[k[1]]['y']],
                  line_width=v)

    plot.circle("x", "y", size="url", color="green", alpha=1, source=source,
            name="nodes")

    return plot

@empty_plot_on_empty_df
def tags_plot(df, plot_width=600, plot_height=300):
    df2 = calculate_graph_coords(df, 'tag')

    source = ColumnDataSource(df2)

    line_coords = calculate_query_correlation(df, 'tag')

    hover = HoverTool(
        tooltips=[
            ("Tag", "@tag"),
            ("No. Results", "@url"),
        ],
        names=["nodes"],
    )

    plot = figure(plot_width=plot_width, plot_height=plot_height,
                  tools=[hover, "wheel_zoom", "reset"])
    plot.axis.visible = None
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    plot.logo = None

    # Create connection lines.
    for k, v in line_coords.items():
        plot.line([df2.loc[k[0]]['x'], df2.loc[k[1]]['x']],
                  [df2.loc[k[0]]['y'], df2.loc[k[1]]['y']],
                  line_width=v)

    plot.circle("x", "y", size="url", color="green", alpha=1, source=source,
            name="nodes")

    return plot

def most_common_url_table(df):
    source = ColumnDataSource(df.groupby('hostname')
                                .count()
                                .sort_values('url',ascending=False)
                                .reset_index(),
                              callback=js_callback)
    columns = [TableColumn(field="hostname", title="Site Name"),
               TableColumn(field="url", title="Count")]
    t = DataTable(source=source, columns=columns,
                  row_headers=False, width=400, height=280)
    return VBox(t)

def site_tld_table(df):
    source = ColumnDataSource(df.groupby('tld')
                                .count()
                                .sort_values('url', ascending=False)
                                .reset_index(),
                              callback=js_callback)
    columns = [TableColumn(field="tld", title="Ending"),
               TableColumn(field="url", title="Count")]
    t = DataTable(source=source, columns=columns,
                  row_headers=False, width=400, height=80)
    return VBox(t)

def tags_table(df):
    data = Counter(df.tag.tolist())
    tags = [k for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True)]
    counts = [v for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True)]

    source = ColumnDataSource(data=dict(count=counts, tags=tags),
                              callback=js_callback)

    columns = [TableColumn(field='tags', title="Tags"),
               TableColumn(field='count', title="Count"),
               ]

    t = DataTable(source=source, columns=columns, row_headers=False,
                  width=400, height=120)
    return VBox(t)

def queries_table(df):
    source = ColumnDataSource(df.groupby(by='query')
                                .count()
                                .sort_values('url', ascending=False)
                                .reset_index(),
                              callback=js_callback)

    columns = [TableColumn(field="query", title="Query"),
               TableColumn(field="url", title="Pages")
               ]

    t = DataTable(source=source, columns=columns, row_headers=False,
                  width=400, height=120)
    return VBox(t)

def create_plot_components(df):
    hostnames = most_common_url_bar(df)
    tlds = site_tld_bar(df)
    ts = pages_queried_timeseries(df)
    queries = queries_plot(df)
    tags = tags_plot(df)
    return components(dict(hostnames=hostnames, tlds=tlds, ts=ts, queries=queries, tags=tags))

def create_table_components(df):
    urls = most_common_url_table(df)
    tlds = site_tld_table(df)
    tags = tags_table(df)
    queries = queries_table(df)
    return components(dict(urls=urls, tlds=tlds, tags=tags, queries=queries))
