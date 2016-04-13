from collections import Counter
from itertools import chain

from bokeh.charts import Bar, Line
from bokeh.embed import components
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models import ColumnDataSource, CustomJS
import numpy as np
import pandas as pd
from urlparse import urlparse

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

def most_common_url_bar(df):
    p = Bar(df.groupby('hostname').count().sort_values('url',ascending=False).reset_index(),
            label='hostname', values='url', xlabel='Sites', ylabel='Occurences')
    return p

def pages_queried_timeseries(df, rule='30S'):
    p = Line(df.resample(rule, how='count').cumsum(),
             y='url', xlabel='Time', ylabel='No. Pages Queried')
    return p

def create_plot_components(df):
    bar = most_common_url_bar(df)
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
    return t

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
    return t

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
    return t

def create_table_components(df):
    urls = most_common_url_table(df)
    tlds = site_tld_table(df)
    tags = tags_table(df)
    return components(dict(urls=urls, tlds=tlds, tags=tags))
