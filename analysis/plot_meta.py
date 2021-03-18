import collections


class PlotInfo(collections.namedtuple('_PLOT_FIELDS', 
                                      ['color', 'facecolor', 'label', 'marker', 'size', 
                                       'linewidth', 'linestyle', 'zorder'])):
    __slots__ = ()



'''
PlotInfo for all penalized regression methods
'''
def regression_methods():
    plotmeta = dict()
    plotmeta['ridge'] = \
        PlotInfo(color     = "#616B77", # Shuttle Gray
                 facecolor = "#616B77",
                 label     = "Ridge",
                 marker    = "v",
                 size      = 8,
                 linewidth = 2,
                 linestyle = "solid",
                 zorder    = 10,
                )
    plotmeta['lasso'] = \
        PlotInfo(color     = "#93BFEB", # Perano Blue
                 facecolor = 'None',
                 label     = "Lasso",
                 marker    = "^",
                 size      = 8,
                 linewidth = 2,
                 linestyle = "solid",
                 zorder    = 20,
                )
    plotmeta['elastic_net'] = \
        PlotInfo(color     = "#367DC4", # Boston Blue
                 facecolor = "#367DC4",
                 label     = "Elastic Net",
                 marker    = "^",
                 size      = 8,
                 linewidth = 2,
                 linestyle = "solid",
                 zorder    = 30,
                )
    plotmeta['mr_ash'] = \
        PlotInfo(color     = "#CC4300", # Grenadier Red
                 facecolor = "#CC4300",
                 label     = "Mr.Ash",
                 marker    = "o",
                 size      = 8,
                 linewidth = 2,
                 linestyle = "solid",
                 zorder    = 40,
                )
    plotmeta['mr_ash_init'] = \
        PlotInfo(color     = "#CC4300", # Grenadier Red
                 facecolor = "None",
                 label     = "Mr.Ash(init)",
                 marker    = "o",
                 size      = 8,
                 linewidth = 2,
                 linestyle = "solid",
                 zorder    = 40,
                )
    
    return plotmeta
