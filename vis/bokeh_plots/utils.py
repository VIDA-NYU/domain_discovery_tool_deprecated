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

FONT = "Helvetica"
FONT_SIZE = "10pt"

NODATA_COLOR = "#eeeeee"
GRAY = "#CCCCCC"
DARK_GRAY = "#6B6B73"
BLUE = "#2b83ba"
RED = "#d7191c"

AXIS_FORMATS = dict(
    minor_tick_in=None,
    minor_tick_out=None,
    major_tick_in=None,
    major_label_text_font=FONT,
    major_label_text_font_size="8pt",
    axis_label_text_font=FONT,
    axis_label_text_font_style="italic",
    axis_label_text_font_size="8pt",

    axis_line_color=DARK_GRAY,
    major_tick_line_color=DARK_GRAY,
    major_label_text_color=DARK_GRAY,

    major_tick_line_cap="round",
    axis_line_cap="round",
    axis_line_width=1,
    major_tick_line_width=1,
)
PLOT_FORMATS = dict(
    toolbar_location=None,
    # outline_line_color="#FFFFFF",
    title_text_font=FONT,
    title_text_align='right',
    title_text_color=DARK_GRAY,
    title_text_font_size="9pt",
    title_text_baseline='bottom',
    # min_border_left=5,
    # min_border_right=10,
    # min_border_top=25,
    # min_border_bottom=0,
    min_border_left=0,
    min_border_right=0,
    min_border_top=0,
    min_border_bottom=0,
)
LINE_FORMATS = dict(
    line_cap='round',
    line_join='round',
    line_width=2
)
FONT_PROPS_SM = dict(
    text_font=FONT,
    text_font_size='8pt',
)
FONT_PROPS_MD = dict(
    text_font=FONT,
    text_font_size='10pt',
)
FONT_PROPS_LG = dict(
    text_font=FONT,
    text_font_size='12pt',
)
BLANK_AXIS = dict(
    minor_tick_in=None,
    minor_tick_out=None,
    major_tick_in=None,
    major_label_text_font=FONT,
    major_label_text_font_size="8pt",
    axis_label_text_font=FONT,
    axis_label_text_font_style="italic",
    axis_label_text_font_size="8pt",

    axis_line_color='white',
    major_tick_line_color='white',
    major_label_text_color='white',
    axis_label_text_color='white',

    major_tick_line_cap="round",
    axis_line_cap="round",
    axis_line_width=1,
    major_tick_line_width=1,
)

def make_empty_plot(plot_width, plot_height):
    return figure(plot_width=plot_width, plot_height=plot_height,
                  tools="", logo=None)

def empty_plot_on_empty_df(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args[0]) == 0:
            return make_empty_plot(func.func_defaults[0],
                                   func.func_defaults[1])
        return func(*args, **kwargs)
    return wrapper
