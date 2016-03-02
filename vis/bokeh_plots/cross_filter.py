import itertools

from bokeh.charts import Bar, Line
from bokeh.embed import components
from bokeh.models.widgets import CheckboxButtonGroup
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

def most_common_url_bar(df, n=10):
    p = Bar(df.groupby('hostname').count().sort('url',ascending=False).reset_index().iloc[:n],
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

def create_interactors(df):
    # unique tags
    unique_tags = pd.unique(itertools.chain(*df.tags.dropna().ravel()))
    if len(unique_tags) == 0:
        unique_tags = np.array(["No tags found"])
    tag_selector = CheckboxButtonGroup(labels=unique_tags.tolist())

    # unique tlds
    tld_selector = CheckboxButtonGroup(labels=df.tld.unique().tolist())

    return components(dict(tags=tag_selector, tlds=tld_selector))
