from collections import Counter
from itertools import chain

from bokeh.charts import Bar
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.io import VBox
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models import ColumnDataSource, CustomJS
import numpy as np
import pandas as pd
from urlparse import urlparse

from .utils import empty_plot_on_empty_df

MIN_BORDER=10

js_callback = CustomJS(code="""
    var data_table_ids = ['urls', 'tlds', 'tags'];

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

def create_queryframe(pages, dates):
    dates = pd.DataFrame(dates, columns=['url', 'timestamp'])
    dates['timestamp'] = pd.DatetimeIndex(dates.timestamp)

    pages = pd.DataFrame(pages["pages"], columns=['url', 'x', 'y', 'tags'])
    pages['url'] = [x[0] for x in pages.url]

    df = pd.merge(left=dates, right=pages, on='url', how='left')
    df['hostname'] = [urlparse(x).hostname.lstrip('www.') for x in df.url]
    df['tld'] = [x[x.rfind('.'):] for x in df.hostname]
    df['tags'] = df.tags.apply(lambda x:[] if isinstance(x, float) else x) # fill nan with []

    df.set_index('timestamp', inplace=True)

    return df

@empty_plot_on_empty_df
def most_common_url_bar(df, title="Frequency of Pages Scraped",
                        plot_width=600, plot_height=400, top_n=10):

    bars = df[['hostname','url']].groupby('hostname').count().sort_values('url', ascending=False)
    bars['y'] = bars.url / 2.

    if top_n:
        bars = bars.iloc[:10]

    source = ColumnDataSource(bars)

    p = figure(plot_width=plot_width, plot_height=plot_height, title=title,
               tools='box_zoom, reset',
               min_border_left=50, min_border_right=50,
               min_border_top=MIN_BORDER, min_border_bottom=MIN_BORDER,
               x_range=bars.index.tolist(), y_range=(0,bars.url.max()))
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 0.785
    p.logo=None

    p.rect(x='hostname', y='y', height='url', width=0.8, source=source)

    return p

@empty_plot_on_empty_df
def pages_queried_timeseries(df, title="No. Pages Queried",
                             plot_width=600, plot_height=200, rule='1T'):

    ts = df[['url']].resample(rule, how='count').cumsum()

    ts = pd.concat([ts[:1], ts]) # prepend 0-value for Line chart compat
    ts.iloc[0]['url'] = 0

    source = ColumnDataSource(ts)

    p = figure(plot_width=plot_width, plot_height=plot_height, title=title,
               x_axis_type='datetime', tools='box_zoom, reset',
               min_border_left=MIN_BORDER, min_border_right=10,
               min_border_top=MIN_BORDER, min_border_bottom=10)
    p.logo=None

    p.line(x='timestamp', y='url', line_width=3, line_alpha=0.8, source=source)

    return p

def create_plot_components(df, **kwargs):
    bar = most_common_url_bar(df, **kwargs)
    ts = pages_queried_timeseries(df)
    return components(dict(bar=bar, ts=ts))

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
    data = Counter(list(chain(*df.tags.tolist())))
    tags = [k for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True)]
    counts = [v for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True)]

    source = ColumnDataSource(data=dict(count=counts, tags=tags),
                              callback=js_callback)

    columns = [TableColumn(field='tags', title="Tags"),
               TableColumn(field='count', title="Count"),
               ]

    t = DataTable(source=source, columns=columns, row_headers=False,
                  width=400, height=140)
    return VBox(t)

def create_table_components(df):
    urls = most_common_url_table(df)
    tlds = site_tld_table(df)
    tags = tags_table(df)
    return components(dict(urls=urls, tlds=tlds, tags=tags))
