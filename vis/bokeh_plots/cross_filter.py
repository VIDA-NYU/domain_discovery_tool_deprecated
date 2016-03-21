import itertools

from bokeh.charts import Bar, Line
from bokeh.embed import components
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models import ColumnDataSource
import numpy as np
import pandas as pd
from urlparse import urlparse

def create_queryframe(pages, dates):
    dates = pd.DataFrame(dates, columns=['url', 'timestamp'])
    dates['timestamp'] = pd.DatetimeIndex(dates.timestamp)

    pages = pd.DataFrame(pages["pages"], columns=['url', 'x', 'y', 'tags'])
    pages['url'] = [x[0] for x in pages.url]

    df = pd.merge(left=dates, right=pages, on='url', how='left')
    df['hostname'] = [urlparse(x).hostname.lstrip('www.') for x in df.url]
    df['tld'] = [x[x.rfind('.'):] for x in df.hostname]
    df.set_index('timestamp', inplace=True)

    return df

def most_common_url_bar(df):
    p = Bar(df.groupby('hostname').count().sort('url',ascending=False).reset_index(),
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
                                .sort('url',ascending=False)
                                .reset_index())
    columns = [TableColumn(field="hostname", title="Site Name"),
               TableColumn(field="url", title="Count")]
    t = DataTable(source=source, columns=columns,
                  row_headers=False, width=400, height=280)
    return t

def site_tld_table(df):
    source = ColumnDataSource(df.groupby('tld')
                                .count()
                                .sort('url',ascending=False)
                                .reset_index())
    columns = [TableColumn(field="tld", title="Ending"),
               TableColumn(field="url", title="Count")]
    t = DataTable(source=source, columns=columns,
                  row_headers=False, width=400, height=280)
    return t

def create_table_components(df):
    urls = most_common_url_table(df)
    tlds = site_tld_table(df)
    return components(dict(urls=urls, tlds=tlds))