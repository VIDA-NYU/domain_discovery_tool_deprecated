import json
from functools import partial

from bokeh.io import vform
from bokeh.plotting import figure, show, output_file, save
from bokeh.plotting import ColumnDataSource
from bokeh.models import HoverTool, Circle, CustomJS, LassoSelectTool
from bokeh.models.widgets import RadioButtonGroup, Button
from bokeh.models.widgets.inputs import TextInput, Select
from bokeh.embed import components


FIGURE_WIDTH=1000
FIGURE_HEIGHT=375
CUSTOM_COLOR = "green"
NEUTRAL_COLOR = "#7F7F7F"
POSITIVE_COLOR = "blue"
NEGATIVE_COLOR = "crimson"
CIRCLE_SIZE=10


def colormap(key):
    color = {
        "Irrelevant": NEGATIVE_COLOR,
        "Relevant": POSITIVE_COLOR,
        "Custom": CUSTOM_COLOR
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
    color = []
    custom_tags = ["Custom tags..."]
    
    for tag in tags:
        custom = False
        if tag:
            for t in tag:
                if t not in ["Relevant", "Irrelevant", ""]:
                    custom = True
                    if t not in custom_tags:
                        custom_tags.append(t)
            if not custom:    
                color.append(colormap(tag[0]))
            else:
                color.append(colormap("Custom"))
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
    p = figure(tools="hover", width=FIGURE_WIDTH,
            toolbar_location=None, responsive=True, tags=["clusterPlot"])

    # Ensure that the lasso only selects with mouseup, not mousemove.
    p.add_tools(LassoSelectTool(select_every_mousemove=False))

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
                selected: true,
                possible: false,
            });
            data["color"][inds[i]] = "%s";
        }
        BokehPlots.updateTags(selected, tag, inds);
        source.trigger("change");
    """

    textinput_code = """
        event.preventDefault();
        var inds = source.get('selected')["1d"].indices;
        var data = source.get('data');
        var selected = [];
        var tag = cb_obj.get("value");
    
        //Update the custom tags selection list 
        var options = custom_tags_select.get("options");
        if(options.indexOf(tag) < 0){
            options.push(tag);
            custom_tags_select.set("options", options);
        }

        // Reinitialise to the default value
        cb_obj.set("value", "Enter custom tag here...")

        for(var i = 0; i < inds.length; i++){
            selected.push({
                x: data.x[inds[i]],
                y: data.y[inds[i]],
                url: data.urls[inds[i]],
                tags: data.tags[inds[i]],
                selected: true,
                possible: false,
            });
            data["color"][inds[i]] = "%s";
        }
        BokehPlots.updateTags(selected, tag, inds);
        source.trigger("change");
    """

    selectinput_code = """
    event.preventDefault();
    var inds = source.get('selected')["1d"].indices;
    var data = source.get('data');
    var selected = [];
    var tag = cb_obj.get("value");    

    cb_obj.set("value", "Enter tags...")

    for(var i = 0; i < inds.length; i++){
         selected.push({
            x: data.x[inds[i]],
            y: data.y[inds[i]],
            url: data.urls[inds[i]],
            tags: data.tags[inds[i]],
            selected: true,
            possible: false,
         });
         data["color"][inds[i]] = "%s";
    }
    BokehPlots.updateTags(selected, tag, inds);
    source.trigger("change");
    """

    # Supply color with print formatting.
    but_relevant = Button(label="Relevant", type="success")
    but_relevant.callback = CustomJS(args=dict(source=source),
                    code=button_code % ("Relevant", POSITIVE_COLOR))

    but_irrelevant = Button(label="Irrelevant", type="success")
    but_irrelevant.callback = CustomJS(args=dict(source=source),
                    code=button_code % ("Irrelevant", NEGATIVE_COLOR))

    but_neutral = Button(label="Neutral", type="success")
    but_neutral.callback = CustomJS(args=dict(source=source),
                    code=button_code % ("Neutral", NEUTRAL_COLOR))

    custom_tag_input = TextInput(value="Enter custom tag here...")
    custom_tag_input.callback = CustomJS(args=dict(source=source),
                                  code=textinput_code % (CUSTOM_COLOR))
    
    custom_tag_select = Select(value="Custom tags...", options=custom_tags)
    custom_tag_select.callback = CustomJS(args=dict(source=source),
                                  code=selectinput_code % (CUSTOM_COLOR))
    custom_tag_input.callback.args["custom_tags_select"] = custom_tag_select

    # Adjust what attributes are displayed by the HoverTool
    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [
        ("urls", "@urls"),
    ]
    layout = vform(p,custom_tag_input, custom_tag_select, but_relevant, but_irrelevant, but_neutral)

    # Combine script and div into a single string.
    plot_code = components(layout)
    return plot_code[0] + plot_code[1]


def empty_plot():
    p = figure(tools="hover", height=FIGURE_HEIGHT,
            toolbar_location=None, responsive=True)

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
    custom_tag_input = TextInput(value="Enter custom tag here...")
    custom_tag_select = Select(value="Custom tags...", options=["Custom tags..."])

    layout = vform(p, custom_tag_input, custom_tag_select, but_relevant, but_irrelevant, but_neutral)

    # Combine script and div into a single string.
    plot_code = components(layout)
    return plot_code[0] + plot_code[1]
