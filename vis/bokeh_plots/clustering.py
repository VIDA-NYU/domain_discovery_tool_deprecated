import json
from functools import partial

from bokeh.io import vform
from bokeh.plotting import figure, show, output_file, save
from bokeh.plotting import ColumnDataSource
from bokeh.models import HoverTool, Circle, CustomJS, LassoSelectTool
from bokeh.models.widgets import RadioButtonGroup, Button
from bokeh.embed import components


FIGURE_WIDTH=600
FIGURE_HEIGHT=400
NEUTRAL_COLOR = "#7F7F7F"
POSITIVE_COLOR = "blue"
NEGATIVE_COLOR = "crimson"
CIRCLE_SIZE=10


def colormap(key):
    color = {
        "Irrelevant": NEGATIVE_COLOR,
        "Relevant": POSITIVE_COLOR,
    }.get(key, NEUTRAL_COLOR)
    return color


def selection_plot(response):
    # Let's move these into a settings file somewhere?
    # height/width could potentially be driven by the request?


    # Include color data in the ColumnDataSource to allow for changing the color on
    # the client side.
    urls = [x[0] for x in response["pages"]]
    xdata = [x[1] for x in response["pages"]]
    ydata = [x[2] for x in response["pages"]]
    tags = [x[3] for x in response["pages"]]
    color = [colormap(x[0]) if x else colormap(None) for x in tags]

    source = ColumnDataSource(
        data=dict(
            x=xdata,
            y=ydata,
            urls=urls,
            tags=tags,
            color=color,
        )
    )


    # Create the figure with FIGURE_WIDTH and FIGURE_HEIGHT
    p = figure(tools="hover", width=FIGURE_WIDTH, height=FIGURE_HEIGHT,
            toolbar_location=None)

    # Ensure that the lasso only selects with mouseup, not mousemove.
    p.add_tools(LassoSelectTool(select_every_mousemove=False))

    # These turn off the x/y axis ticks
    p.axis.visible = None

    # These turn the major grid off
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    # Plot non-selected circles with a particular style using CIRCLE_SIZE and
    # 'color' list
    p.circle("x", "y", size=CIRCLE_SIZE, line_width=2, line_alpha=0.5,
            line_color=None, fill_alpha=0.6, color='color', source=source,
            name="urls")
    nonselected_circle = Circle(fill_alpha=0.2, fill_color='color',
            line_color='color')
    renderer = p.select(name="urls")
    renderer.nonselection_glyph = nonselected_circle


    # Create buttons and their callbacks, use button_code string for callbacks.
    button_code = """
        event.preventDefault();
        var inds = source.get('selected')["1d"].indices;
        var data = source.get('data');
        var selected = [];
        for(var i = 0; i < inds.length; i++){
            selected.push([
                [
                    data.x[inds[i]],
                    data.y[inds[i]],
                    data.urls[inds[i]],
                    data.tags[inds[i]],
                ]
            ]);
            data["color"][inds[i]] = "%s";
        }
        source.trigger("change");
        window.data = data;
        window.inds = inds;
        window.selected = selected;
    """

    # Supply color with print formatting.
    button1 = Button(label="Positive", type="success")
    button1.callback = CustomJS(args=dict(source=source),
            code=button_code % POSITIVE_COLOR)

    button2 = Button(label="Negative", type="success")
    button2.callback = CustomJS(args=dict(source=source),
            code=button_code % NEGATIVE_COLOR)

    button3 = Button(label="Neutral", type="success")
    button3.callback = CustomJS(args=dict(source=source),
            code=button_code % NEUTRAL_COLOR)


    # Adjust what attributes are displayed by the HoverTool
    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [
        ("urls", "@urls"),
        ("tags", "@tags"),
    ]
    layout = vform(p, button1, button2, button3)

    # Combine script and div into a single string.
    plot_code = components(layout)
    return plot_code[0] + plot_code[1]


# To be used for plot testing.
if __name__ == "__main__":
    # plot = selection_plot()
    # with open("points.html", "w") as f:
    #     f.write(plot)
    selection_plot()
