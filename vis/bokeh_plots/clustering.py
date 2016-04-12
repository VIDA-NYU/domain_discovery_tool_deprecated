import json
from functools import partial

from bokeh.io import vform
from bokeh.plotting import figure, show, output_file, save, hplot, vplot
from bokeh.plotting import ColumnDataSource
from bokeh.models import HoverTool, Circle, CustomJS, LassoSelectTool
from bokeh.models.widgets import RadioButtonGroup, Button
from bokeh.models.widgets.inputs import TextInput, Select
from bokeh.embed import components

FIGURE_WIDTH=1000
FIGURE_HEIGHT=400
MIN_BORDER_LEFT=10
MIN_BORDER_RIGHT=10
MIN_BORDER_TOP=10
MIN_BORDER_BOTTOM=10
NEUTRAL_COLOR = "#7F7F7F"
POSITIVE_COLOR = "blue"
NEGATIVE_COLOR = "crimson"
CUSTOM_COLOR = "green"
CIRCLE_SIZE=10

def colormap(key):
    color = {
        "Irrelevant": NEGATIVE_COLOR,
        "Relevant": POSITIVE_COLOR,
        "Custom": CUSTOM_COLOR
    }.get(key, NEUTRAL_COLOR)
    return color


def selection_plot(response, tag_colors):
    # Let's move these into a settings file somewhere?
    # height/width could potentially be driven by the request?


    # Include color data in the ColumnDataSource to allow for changing the color on
    # the client side.
    urls = [x[0] for x in response["pages"]]
    xdata = [x[1] for x in response["pages"]]
    ydata = [x[2] for x in response["pages"]]
    tags = [x[3] for x in response["pages"]]
    color = []
    custom_tags = ["Custom tags"]

    for tag in tags:
        if tag:
            t = tag[len(tag) - 1]
            if t not in ["Relevant", "Irrelevant", ""]:
                if t not in custom_tags:
                    custom_tags.append(t)
                if((tag_colors != None) and (t in tag_colors["colors"])):
                    color.append(tag_colors["colors"][t])
                else:
                    color.append(colormap("Custom"))
            else:
                color.append(colormap(t))
        else:
            color.append(colormap(None))
    source = ColumnDataSource(
        data=dict(
            x=xdata,
            y=ydata,
            urls=urls,
            tags=tags,
            color=color,
        )
    )
    # Callback code for CDS.
    source.callback = CustomJS(code="""
        var inds = cb_obj.get('selected')["1d"].indices;
        var data = cb_obj.get('data');
        BokehPlots.showPages(inds);
    """)


    # Create the figure with FIGURE_WIDTH and FIGURE_HEIGHT
    p = figure(
        tools="hover,wheel_zoom,reset",
        width=FIGURE_WIDTH,
        height=FIGURE_HEIGHT,
        responsive=True,
        tags=["clusterPlot"],
        min_border_bottom=MIN_BORDER_BOTTOM,
        min_border_top=MIN_BORDER_TOP,
        min_border_left=MIN_BORDER_LEFT,
        min_border_right=MIN_BORDER_RIGHT,
    )

    # Ensure that the lasso only selects with mouseup, not mousemove.
    p.add_tools(
        LassoSelectTool(select_every_mousemove=False),
    )

    # These turn off the x/y axis ticks
    p.axis.visible = None

    # These turn the major grid off
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    # Plot non-selected circles with a particular style using CIRCLE_SIZE and
    # 'color' list
    p.circle("x", "y", size=13, line_width=2, line_alpha=1,
            line_color=None, fill_alpha=1, color='color', source=source,
            name="urls")
    nonselected_circle = Circle(fill_alpha=0.1, line_alpha=0.1, fill_color='color',
            line_color='color')
    renderer = p.select(name="urls")
    renderer.nonselection_glyph = nonselected_circle


    # Create buttons and their callbacks, use button_code string for callbacks.
    button_code = """
        event.preventDefault();
        var inds = source.get('selected')["1d"].indices;
        var data = source.get('data');
        var selected = [];
        tag = "%s";
        for(var i = 0; i < inds.length; i++){
            selected.push({
                x: data.x[inds[i]],
                y: data.y[inds[i]],
                url: data.urls[inds[i]],
                tags: data.tags[inds[i]],
                color: data.color[inds[i]],
                selected: true,
                possible: false,
            });
        }
        BokehPlots.updateTags(selected, tag, "Apply");
        source.trigger("change");
    """

    textinput_code = """
        event.preventDefault();
        var inds = source.get('selected')["1d"].indices;
        var data = source.get('data');
        var selected = [];
        var tag = cb_obj.get("value");

        // Reinitialise to the default value
        cb_obj.set("value", "Add custom tag...")

        if(tag.indexOf("Add custom tag...") < 0) {
        //Update the custom tags selection list
        var options = custom_tags_select.get("options");
        if(options.indexOf(tag) < 0){
            options.push(tag);
            custom_tags_select.set("options", options);
        }

        for(var i = 0; i < inds.length; i++){
            selected.push({
                x: data.x[inds[i]],
                y: data.y[inds[i]],
                url: data.urls[inds[i]],
                tags: data.tags[inds[i]],
                color: data.color[inds[i]],
                selected: true,
                possible: false,
            });
        }
        BokehPlots.updateTags(selected, tag, "Apply");
        source.trigger("change");
        }
    """

    selectinput_code = """
    event.preventDefault();
    var inds = source.get('selected')["1d"].indices;
    var data = source.get('data');
    var selected = [];
    var tag = cb_obj.get("value");

    cb_obj.set("value", "Enter tags...")
    if(tag.indexOf("Add custom tag...") < 0) {
    for(var i = 0; i < inds.length; i++){
         selected.push({
            x: data.x[inds[i]],
            y: data.y[inds[i]],
            url: data.urls[inds[i]],
            tags: data.tags[inds[i]],
            color: data.color[inds[i]],
            selected: true,
            possible: false,
         });
    }
    BokehPlots.updateTags(selected, tag, "Apply");
    source.trigger("change");
    }
    """

    # Create buttons and their callbacks, use button_code string for callbacks.
    crawl_code = """
        event.preventDefault();
        var inds = source.get('selected')["1d"].indices;
        var data = source.get('data');
        var selected = [];
        var crawl = '%s';
        for(var i = 0; i < inds.length; i++){
            selected.push(data.urls[inds[i]]);
        }
        BokehPlots.crawlPages(selected, crawl);
        source.trigger("change");
    """

    # Supply color with print formatting.
    but_relevant = Button(label="Relevant", type="success")
    but_relevant.callback = CustomJS(args=dict(source=source),
                    code=button_code % ("Relevant"))

    but_irrelevant = Button(label="Irrelevant", type="success")
    but_irrelevant.callback = CustomJS(args=dict(source=source),
                    code=button_code % ("Irrelevant"))

    but_neutral = Button(label="Neutral", type="success")
    but_neutral.callback = CustomJS(args=dict(source=source),
                    code=button_code % ("Neutral"))

    custom_tag_input = TextInput(value="Add custom tag...")
    custom_tag_input.callback = CustomJS(args=dict(source=source),
                                         code=textinput_code % ())

    custom_tag_select = Select(value="Custom tags", options=custom_tags)
    custom_tag_select.callback = CustomJS(args=dict(source=source),
                                          code=selectinput_code % ())
    custom_tag_input.callback.args["custom_tags_select"] = custom_tag_select

    but_backward_crawl = Button(label="Backlinks", type="success")
    but_backward_crawl.callback = CustomJS(args=dict(source=source),
                                           code=crawl_code % ("backward"))

    but_forward_crawl = Button(label="Forwardlinks", type="success")
    but_forward_crawl.callback = CustomJS(args=dict(source=source),
                                          code=crawl_code % ("forward"))


    # Adjust what attributes are displayed by the HoverTool
    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [
        ("urls", "@urls"),
    ]
    tags = hplot(but_neutral, but_relevant, but_irrelevant, custom_tag_input, custom_tag_select)
    tags_crawl = hplot(but_backward_crawl, but_forward_crawl)
    layout = vplot(p, tags, tags_crawl)

    # Combine script and div into a single string.
    plot_code = components(layout)
    return plot_code[0] + plot_code[1]


def empty_plot():
    p = figure(
        tools="hover,wheel_zoom,reset",
        width=FIGURE_WIDTH,
        height=FIGURE_HEIGHT,
        responsive=True,
        tags=["clusterPlot"],
        min_border_bottom=MIN_BORDER_BOTTOM,
        min_border_top=MIN_BORDER_TOP,
        min_border_left=MIN_BORDER_LEFT,
        min_border_right=MIN_BORDER_RIGHT,
    )

    # Ensure that the lasso only selects with mouseup, not mousemove.
    p.add_tools(LassoSelectTool(select_every_mousemove=False))

    # These turn off the x/y axis ticks
    p.axis.visible = None

    # These turn the major grid off
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    # Plot non-selected circles with a particular style using CIRCLE_SIZE and
    # 'color' list
    but_relevant = Button(label="Relevant", type="success")
    but_irrelevant = Button(label="Irrelevant", type="success")
    but_neutral = Button(label="Neutral", type="success")
    custom_tag_input = TextInput(value="Add custom tag...")
    custom_tag_select = Select(value="Custom tags", options=["Custom tags"])
    but_backward_crawl = Button(label="Backlinks", type="success")
    but_forward_crawl = Button(label="Forwardlinks", type="success")

    tags = hplot(but_relevant, but_irrelevant, but_neutral, custom_tag_input, custom_tag_select)
    tags_crawl = hplot(but_backward_crawl, but_forward_crawl)
    layout = vform(p, tags, tags_crawl)

    # Combine script and div into a single string.
    plot_code = components(layout)
    return plot_code[0] + plot_code[1]
