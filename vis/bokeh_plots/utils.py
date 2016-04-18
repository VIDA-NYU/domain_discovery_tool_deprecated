from bokeh.plotting import figure
from functools32 import wraps

DATETIME_FORMAT = dict(
    microseconds=["%m/%d %X"],
    milliseconds=["%X"],
    seconds=["%X"],
    minsec=["%X"],
    minutes=["%H:%M"],
    hourmin=["%H:%M"],
    hours=["%H:%M"],
    days=["%m/%d"],
)

def make_empty_plot(title, plot_width, plot_height):
    return figure(title=title, plot_height=plot_height, plot_width=plot_width,
                  tools="", logo=None)

def empty_plot_on_empty_df(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args[0]) == 0:
            return make_empty_plot(func.func_defaults[0],
                                   func.func_defaults[1],
                                   func.func_defaults[2])
        return func(*args, **kwargs)
    return wrapper
