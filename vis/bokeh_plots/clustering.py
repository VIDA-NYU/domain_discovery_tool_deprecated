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


def selection_plot():
    # Let's move these into a settings file somewhere?
    # height/width could potentially be driven by the request?

    response={"last_downloaded_url_epoch":1449501703.786,"pages":[[["http://thepioneerwoman.com/cooking/perfect-potato-soup/"],-1.4188703114780365,-3.4650629801381965,[]],[["http://www.thesaurus.com/browse/potato"],1.869833256086278,2.7103163698374013,[]],[["http://www.freshforkids.com.au/veg_pages/potato/potato.html"],-2.3900322521617725,0.2511307418068853,["Relevant"]],[["https://www.organicfacts.net/health-benefits/vegetable/health-benefits-of-potato.html"],-3.6323316888418065,0.10114078448550545,["Relevant"]],[["http://www.mtvernon.wsu.edu/path_team/potato.htm"],3.399281642167659,2.1684229020929227,[]],[["http://www.almanac.com/plant/potatoes"],3.716548352935619,-1.4570552649903332,[]],[["https://www.nlm.nih.gov/medlineplus/ency/article/002875.htm"],-3.9144478253289927,1.1132466666466567,["Relevant"]],[["http://www.bbc.co.uk/food/potato"],6.657663902390018,-2.967323290492098,[]],[["https://en.wikipedia.org/wiki/Potato"],-2.7252328309969793,-0.07771556426591016,["Relevant"]],[["http://cuke.hort.ncsu.edu/cucurbit/wehner/vegcult/potato.html"],-3.626300335574838,1.1982349954829976,["Relevant"]],[["http://www.encyclopedia.com/topic/potato.aspx"],-3.7484545733774217,0.5296117310813545,["Relevant"]],[["http://www.marksdailyapple.com/potatoes-healthy/"],0.8667251319596317,-2.098388269576149,["Irrelevant"]],[["http://potatoes.wsu.edu/"],0.7176122630401875,2.131587326249079,[]],[["http://runescape.wikia.com/wiki/Raw_potato"],0.1762169987298433,-1.5547653407689583,["Irrelevant"]],[["http://knowyourmeme.com/memes/i-can-count-to-potato"],-4.866234700169567,2.8040385961185312,[]],[["http://www.bbcgoodfood.com/glossary/potato"],-0.006432450197992983,-3.3022622880498584,[]],[["http://whatscookingamerica.net/History/PotatoHistory.htm"],-3.235064493924355,0.7952594499431431,["Relevant"]],[["http://whatscookingamerica.net/Q-A/PotatoBaking.htm"],-2.356980559211656,-0.12279170139010472,["Relevant"]],[["http://www.best-potato-recipes.com/"],-0.08898162862986378,-1.2657800006865256,["Irrelevant"]],[["http://www.indepthinfo.com/potato/"],8.518381144741685,2.8211180902434463,[]],[["http://www.livescience.com/45838-potato-nutrition.html"],-3.175570779142773,-0.4842910693037321,["Relevant"]],[["http://42explore.com/potato.htm"],1.496669744850109,-0.7623231039945497,["Irrelevant"]],[["https://en.wikipedia.org/wiki/Sweet_potato"],-2.8827220858777927,-0.45747260437556364,["Relevant"]],[["http://www.marthastewart.com/274750/potato-recipes"],4.796946653831594,-8.75576469674588,[]],[["http://nutritiondata.self.com/facts/vegetables-and-vegetable-products/2552/2"],-3.3122510147938184,-0.9966651207321963,["Relevant"]],[["http://nutritiondata.self.com/facts/vegetables-and-vegetable-products/2770/2"],-3.3122510147938184,-0.9966651207321956,["Relevant"]],[["http://nutrition.about.com/od/askyournutritionist/f/potatoes.htm"],-1.6834183342828435,-3.421540365033865,[]],[["http://www.motherearthnews.com/real-food/when-and-how-to-plant-potatoes.aspx"],0.5354096181662088,-0.7341357448184924,["Irrelevant"]],[["http://www.health-care-clinic.org/vegetables/potato.html"],-2.788382857038525,-0.4279789164449448,["Relevant"]],[["http://potatogenome.berkeley.edu/nsf5/potato_biology/history.php"],-2.3056001279295635,0.6572790243104069,["Relevant"]],[["http://www.thefreedictionary.com/potato"],-0.9126382399147658,-0.45552083576846786,[]],[["http://www.indepthinfo.com/potato/history.shtml"],-0.5937015620500362,1.2444773524798105,[]],[["http://www.food.com/recipe/scalloped-potatoes-85629"],-5.227005129931087,2.8638844788928175,[]],[["http://www.whfoods.com/genpage.php?tname=nutrientprofile&dbid=101"],-5.062956354099639,0.5644309500116559,[]],[["http://www.simplyrecipes.com/recipes/potato_skins/"],1.2858253594872995,-1.7387021141253083,["Irrelevant"]],[["http://www.newworldencyclopedia.org/entry/Potato"],-1.9167090822590986,-0.059207605747832286,["Relevant"]],[["http://idahopotatodrop.com/"],-0.8807675289333637,1.9919555747993938,[]],[["http://www.urbandictionary.com/define.php?term=potatoe"],-1.6986029496857107,0.7006535953387754,[]],[["http://www.foodterms.com/encyclopedia/potato/index.html"],-1.1653977804879025,0.1721935168070797,[]],[["http://www.whfoods.com/genpage.php?tname=foodspice&dbid=48"],-3.5942257283617955,0.20126217624751197,["Relevant"]],[["http://cipotato.org/potato/"],8.518381144741689,2.821118090243449,[]],[["http://www.potatogoodness.com/"],-1.5238585710250916,1.7207570545096231,[]],[["http://dictionary.reference.com/browse/potato"],0.2375471033853415,2.240979478616745,[]],[["http://www.thegardenhelper.com/potato.html"],1.758662620638737,-0.971765038004913,["Irrelevant"]],[["http://www.urbandictionary.com/define.php?term=potato"],8.518381144741689,2.8211180902434494,[]],[["http://www.thefreedictionary.com/couch+potato"],1.1765445652417004,2.3049877698640118,[]],[["http://idioms.thefreedictionary.com/potato"],-2.045179471677792,-0.20146566035466418,["Relevant"]],[["http://minecraft.gamepedia.com/Potato"],8.518381144741689,2.8211180902434494,[]],[["http://science.howstuffworks.com/life/botany/potato-info.htm"],4.059769621265404,-2.778487925821067,[]],[["http://extension.illinois.edu/veggies/potato.cfm"],-2.6753752264492663,-0.2091533351214681,["Relevant"]],[["http://aggie-horticulture.tamu.edu/archives/parsons/vegetables/potato.html"],-2.472021358753835,0.2863085260634518,["Relevant"]],[["http://www2.palomar.edu/users/scrouthamel/potato.htm"],8.518381144741689,2.8211180902434494,[]],[["http://www.history-magazine.com/potato.html"],-0.7628276128922625,-0.12814226492762118,[]],[["http://www.potatogoodness.com/all-about-potatoes/potato-fun-facts-history/"],6.657663902390017,-2.9673232904920988,[]]]}

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
    p = figure(tools="hover", width=FIGURE_WIDTH, height=FIGURE_HEIGHT, toolbar_location=None)

    # Ensure that the lasso only selects with mouseup, not mousemove.
    p.add_tools(LassoSelectTool(select_every_mousemove=False))

    # These turn off the x/y axis ticks
    p.axis.visible = None

    # These turn the major grid off
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    # Plot non-selected circles with a particular style using CIRCLE_SIZE and 'color' list
    p.circle("x", "y", size=CIRCLE_SIZE, line_width=2, line_alpha=0.5, line_color=None, fill_alpha=0.6, color='color', source=source, name="urls")
    nonselected_circle = Circle(fill_alpha=0.2, fill_color='color', line_color='color')
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
    button1.callback = CustomJS(args=dict(source=source), code=button_code % POSITIVE_COLOR)

    button2 = Button(label="Negative", type="success")
    button2.callback = CustomJS(args=dict(source=source), code=button_code % NEGATIVE_COLOR)

    button3 = Button(label="Neutral", type="success")
    button3.callback = CustomJS(args=dict(source=source), code=button_code % NEUTRAL_COLOR)


    # Adjust what attributes are displayed by the HoverTool
    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [
        ("urls", "@urls"),
        ("tags", "@tags"),
    ]
    layout = vform(p, button1, button2, button3)

    # Combine script and div into a single string.
    # plot_code = components(layout)
    # return plot_code[0] + plot_code[1]
    output_file("points.html")
    show(layout)


# To be used for plot testing.
if __name__ == "__main__":
    # plot = selection_plot()
    # with open("points.html", "w") as f:
    #     f.write(plot)
    selection_plot()
