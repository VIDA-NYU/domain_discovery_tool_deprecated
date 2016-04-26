from __future__ import division
from collections import Counter
from itertools import chain, combinations

from bokeh.charts import Bar
from bokeh.plotting import figure
from bokeh.palettes import Spectral4
from bokeh.embed import components
from bokeh.io import VBox
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models import (ColumnDataSource, CustomJS, DatetimeTickFormatter,
    HoverTool, Range1d, Plot, LinearAxis, Rect, FactorRange, CategoricalAxis,
    DatetimeAxis, Line)
import networkx as nx
import numpy as np
import pandas as pd
from urlparse import urlparse

from .utils import (DATETIME_FORMAT, PLOT_FORMATS, AXIS_FORMATS, LINE_FORMATS,
    empty_plot_on_empty_df)

NX_COLOR = Spectral4[1]

MIN_BORDER=10
MAX_CIRCLE_SIZE = 0.1
MIN_CIRCLE_SIZE = 0.01
MAX_LINE_SIZE = 10
MIN_LINE_SIZE = 1

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

def normalize(seq, max_val, min_val):
    s = seq / seq.max() * max_val
    s[s < min_val] = min_val
    return s

def parse_es_response(response):
    df = pd.DataFrame(response, columns=['query', 'retrieved', 'url', 'tag'])
    df['query'] = df['query'].apply(lambda x: x[0])
    df['retrieved'] = pd.DatetimeIndex(df.retrieved.apply(lambda x: x[0]))
    df['url'] = df.url.apply(lambda x: x[0])
    df['hostname'] = [urlparse(x).hostname.lstrip('www.') for x in df.url]
    df['tld'] = [x[x.rfind('.'):] for x in df.hostname]
    df['tag'] = df.tag.apply(lambda x: "Untagged" if isinstance(x, float) else x[0])

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

    if len(correlation) == 0:
        return correlation

    max_corr = max(correlation.values())
    return {k: v/max_corr for k,v in correlation.items()}

def duplicate_multitag_rows(df, sep=';'):
    """
    Makes copy of column for each tag in multitag
    """
    return pd.DataFrame([row.copy().set_value('tag', i)
                        for _, row in df.iterrows()
                        for i in row.tag.split(';')])

@empty_plot_on_empty_df
def most_common_url_bar(df, plot_width=600, plot_height=200, top_n=10):
    bars = df[['hostname','url']].groupby('hostname').count().sort_values('url', ascending=False)
    bars['y'] = bars.url / 2.

    if top_n:
        bars = bars.iloc[:top_n]

    source = ColumnDataSource(bars)

    plot = Plot(title="Top {} Most Common Sites".format(top_n),
                plot_width=plot_width, plot_height=plot_height,
                x_range=Range1d(0,bars.url.max()),
                y_range=FactorRange(factors=bars.index.tolist()[::-1]),
                **PLOT_FORMATS)
    plot.add_glyph(
        source,
        Rect(x='y', y='hostname', height=0.8, width='url')
    )
    plot.add_layout(LinearAxis(axis_label="Occurences", **AXIS_FORMATS), 'below')
    plot.add_layout(CategoricalAxis(**AXIS_FORMATS), 'left')

    return plot

@empty_plot_on_empty_df
def site_tld_bar(df, plot_width=600, plot_height=200):
    bars = df[['tld','url']].groupby('tld').count().sort_values('url', ascending=False)
    bars['y'] = bars.url / 2.

    source = ColumnDataSource(bars)

    plot = Plot(title="Most Common Top-level Domains",
                plot_width=plot_width, plot_height=plot_height,
                x_range=Range1d(0,bars.url.max()),
                y_range=FactorRange(factors=bars.index.tolist()[::-1]),
                **PLOT_FORMATS)
    plot.add_glyph(
        source,
        Rect(x='y', y='tld', height=0.8, width='url')
    )
    plot.add_layout(LinearAxis(axis_label="Occurences", **AXIS_FORMATS), 'below')
    plot.add_layout(CategoricalAxis(**AXIS_FORMATS), 'left')

    return plot

@empty_plot_on_empty_df
def pages_queried_timeseries(df, plot_width=600, plot_height=200, rule='1T'):
    ts = df[['url']].resample(rule, how='count').cumsum()
    ts = pd.concat([ts[:1], ts]) # prepend 0-value for Line chart compat
    ts.iloc[0]['url'] = 0

    source = ColumnDataSource(ts)

    plot = Plot(title="Sites Timeseries",
                plot_width=plot_width, plot_height=plot_height,
                x_range=Range1d(ts.index.min(),ts.index.max()),
                y_range=Range1d(0, ts.iloc[-1].url),
                **PLOT_FORMATS)
    plot.add_glyph(
        source,
        Line(x='retrieved', y='url', **LINE_FORMATS)
    )
    plot.add_layout(DatetimeAxis(**AXIS_FORMATS), 'below')
    plot.add_layout(LinearAxis(**AXIS_FORMATS), 'left')
    #
    # p.line(x='retrieved', y='url', line_width=3, line_alpha=0.8, source=source)

    return plot

@empty_plot_on_empty_df
def queries_plot(df, plot_width=400, plot_height=400):
    df2 = calculate_graph_coords(df, 'query')
    df2["radius"] = normalize(df2.url, MAX_CIRCLE_SIZE, MIN_CIRCLE_SIZE)
    df2["label"] = df2.index + ' (' + df2.url.astype(str) + ')'
    df2["text_y"] = df2.y - df2.radius

    source = ColumnDataSource(df2)

    line_coords = calculate_query_correlation(df, 'query')

    plot = figure(plot_width=plot_width, plot_height=plot_height,
                  x_range=Range1d(-0.25,1.25), y_range=Range1d(-0.25,1.25),
                  tools="", toolbar_location=None,
                #   outline_line_color=None,
                  min_border_left=0,
                  min_border_right=0, min_border_top=0, min_border_bottom=0)

    plot.axis.visible = None
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    plot.logo = None

    # Create connection lines.
    for k, v in line_coords.items():
        plot.line([df2.loc[k[0]]['x'], df2.loc[k[1]]['x']],
                  [df2.loc[k[0]]['y'], df2.loc[k[1]]['y']],
                  line_width=v*MAX_LINE_SIZE, line_color=Spectral4[1])

    plot.circle("x", "y", radius="radius", fill_color=Spectral4[1], line_color='black', line_alpha=0.2, source=source)

    plot.text("x", "text_y", text="label", text_baseline='top', text_align='center', text_alpha=0.6, source=source)

    return plot

@empty_plot_on_empty_df
def tags_plot(df, plot_width=400, plot_height=400):
    df2 = duplicate_multitag_rows(df)
    graph_df = calculate_graph_coords(df2, 'tag')
    graph_df["radius"] = normalize(graph_df.url, MAX_CIRCLE_SIZE, MIN_CIRCLE_SIZE)
    graph_df["label"] = graph_df.index + ' (' + graph_df.url.astype(str) + ')'
    graph_df["text_y"] = graph_df.y - graph_df.radius

    source = ColumnDataSource(graph_df)

    line_coords = calculate_query_correlation(df2, 'tag')

    plot = figure(plot_width=plot_width, plot_height=plot_height,
                  x_range=Range1d(-0.25,1.25), y_range=Range1d(-0.25,1.25),
                  tools="", toolbar_location=None,
                #   outline_line_color=None,
                  min_border_left=0,
                  min_border_right=0, min_border_top=0, min_border_bottom=0)

    plot.axis.visible = None
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    plot.logo = None

    # Create connection lines.
    for k, v in line_coords.items():
        plot.line([graph_df.loc[k[0]]['x'], graph_df.loc[k[1]]['x']],
                  [graph_df.loc[k[0]]['y'], graph_df.loc[k[1]]['y']],
                  line_width=v*MAX_LINE_SIZE, color=NX_COLOR)

    plot.circle("x", "y", radius="radius", color=NX_COLOR, alpha=1, source=source,
                name="nodes")

    plot.text("x", "text_y", text="label", text_baseline='top', text_align='center', text_alpha=0.6, source=source)

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
    df2 = duplicate_multitag_rows(df)

    source = ColumnDataSource(df2.groupby('tag')
                                .count()
                                .sort_values('url', ascending=False)
                                .reset_index(),
                              callback=js_callback)

    columns = [TableColumn(field='tag', title="Tags"),
               TableColumn(field='url', title="Count"),
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
