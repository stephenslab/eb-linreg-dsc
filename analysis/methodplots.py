import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import math

from pymir import mpl_stylesheet
from pymir import mpl_utils
from pymir import pd_utils

import methodprops


mpl_stylesheet.banskt_presentation()

def single_plot_score_methods(ax, resdf, colname, methods, pve, rho, dims, sfracs, use_median = False):
    xvals  = [max(1, int(x * dims[1])) for x in sfracs]
    xscale = 'log10'
    yscale = 'log10'
    for method in methods:
        score = [0 for x in sfracs]
        mconditions  = [f"$(fit) == {method}"]
        mconditions += [f"$(simulate.pve) == {pve}"]
        mconditions += [f"$(simulate.rho) == {rho}"]
        for i, sfrac in enumerate(sfracs):
            sfrac_condition = f"$(simulate.sfrac) == {sfrac}"
            dfselect = pd_utils.select_dfrows(resdf, mconditions + [sfrac_condition])
            scores   = dfselect[colname].to_numpy()
            if use_median:
                score[i] = np.median(scores[~np.isnan(scores)])
            else:
                score[i] = np.mean(scores[~np.isnan(scores)])

        # Plot xvals vs score
        pm = methodprops.plot_metainfo()[method]
        xx = mpl_utils.scale_array(xvals, xscale)
        yy = mpl_utils.scale_array(score, yscale)
        ax.plot(xx, yy, label = pm.label,
                color = pm.color, lw = pm.linewidth / 2, ls = pm.linestyle,
                marker = pm.marker, ms = pm.size / 1.2, mec = pm.color, mfc = pm.facecolor,
                mew = pm.linewidth, zorder = pm.zorder
               )

    mpl_utils.set_soft_ylim(ax, 1.0, 1.2, scale = yscale)
    mpl_utils.set_xticks(ax, scale = xscale, tickmarks = xvals)
    mpl_utils.set_yticks(ax, scale = yscale, kmin = 3, kmax = 4, forceticks = [1.0])
    mpl_utils.decorate_axes(ax, hide = ["top", "right"], ticklimits = True)
    return


def single_plot_computational_time(ax, data, colname, whichmethods, pve, rho, dims, sfrac):
    yscale = 'linear'
    xscale = 'log10'
    ylabels = list()
    for i, method in enumerate(whichmethods):
        # Select relevant rows
        mconditions  = [f"$(fit) == {method}"]
        mconditions += [f"$(simulate.pve) == {pve}"]
        mconditions += [f"$(simulate.rho) == {rho}"]
        mconditions += [f"$(simulate.sfrac) == {sfrac}"]
        dfselect = pd_utils.select_dfrows(data, mconditions)

        # Plotting style
        pm           = methodprops.plot_metainfo()[method]
        boxprops     = dict(linewidth = 0, color = pm.color, facecolor = pm.color)
        medianprops  = dict(linewidth = 0, color = pm.color)
        whiskerprops = dict(color = pm.color)    
        flierprops   = dict(marker = 'o', markerfacecolor = pm.color, markersize=4, 
                            markeredgewidth = 0, markeredgecolor = pm.color)

        # Boxplot
        times = dfselect[colname].to_numpy()
        xx    = mpl_utils.scale_array(times, xscale)
        ax.boxplot(xx, positions = [i+1], showfliers = True, showcaps = False, widths = 0.6, 
                   vert=False, patch_artist=True, notch = False,
                   boxprops = boxprops, medianprops = medianprops, 
                   whiskerprops = whiskerprops, flierprops = flierprops
                  )
        ylabels.append(pm.label)
        
        # Background barplot
        xleft = mpl_utils.scale_array(0.1, xscale)
        xmean = mpl_utils.scale_array(np.mean(times), xscale) - xleft
        ax.barh(i+1, xmean, left = xleft,
                align='center', color = pm.color, linewidth = 0, height = 0.6, alpha = 0.2)

    ax.tick_params(labelcolor = "#333333", left=False)
    ax.set_yticklabels(ylabels, rotation = 0)
    mpl_utils.set_soft_xlim(ax, 0.09, 40, scale = xscale)
    mpl_utils.set_xticks(ax, scale = xscale, kmin = 3, kmax = 4, spacing = 'log10')
    mpl_utils.decorate_axes(ax, hide = ["top", "right", "left"], ticklimits = True)
    return


def create_figure_prediction_error(whichmethods, data, dims, rho_list, pve_list, sfracs, use_median = False):
    
    # Define main settings
    leg_hprop = 0.4
    axwidth   = 6
    wspace    = 0.2
    hspace    = 0.5

    # Number of rows required to show all plots
    ncol = len(rho_list)
    nrow = len(pve_list)
    nplot = ncol * nrow
    #nplot = len(pve_list) * len(rho_list)
    #nrow = math.ceil(nplot / ncol)
    figw = ncol * axwidth

    # Figure height depends on number of rows
    # Height of all rows + height of legend axis + reserved space between rows
    figh = nrow * axwidth + leg_hprop * axwidth + hspace * (nrow - 1) * axwidth

    fig = plt.figure(figsize = (figw, figh)) 
    gs = gridspec.GridSpec(nrow + 1, ncol, height_ratios = [leg_hprop] + [1 for x in range(nrow)])
    gs.update(wspace=wspace, hspace=hspace)

    # Subplots
    axlist = list()
    for i, pve in enumerate(pve_list):
        for j, rho in enumerate(rho_list):
            ax = fig.add_subplot(gs[i + 1, j])

            # Plot for this pve and rho
            single_plot_score_methods(ax, data, 'score1', whichmethods, pve, rho, dims, sfracs, use_median = use_median)
            ax.tick_params(labelcolor = "#333333")

            # Subplot title
            ax.text(0.05, 1.1, f"pve = {pve:g}" + "\n" + r"$\rho$ = {:g}".format(rho),
                    va='top', ha='left', transform=ax.transAxes)

            axlist.append(ax)

    # Legend
    ax0 = fig.add_subplot(gs[0, :])
    ax0.tick_params(bottom = False, left = False, labelbottom = False, labelleft = False)
    mhandles, mlabels = axlist[0].get_legend_handles_labels()
    ax0.legend(handles = mhandles, labels = mlabels, 
               ncol = 2, handlelength = 2,
               loc = 'upper left', bbox_to_anchor = (0, 1.0),
               frameon = True, framealpha = 1.0, borderpad = 0.8)
    mpl_utils.decorate_axes(ax0, hide = ["all"], ticklimits = False)


    # Axes labels at center of subplots
    ylab_idx = ncol * int(nrow / 2)
    ylab_offset = (1 + hspace / 2) if nrow % 2 == 0 else 0.5
    xlab_idx = nplot - 1
    xlab_offset = - wspace / 2 if nplot % 2 == 0 else 0.5
    axlist[ylab_idx].set_ylabel(r"Prediction Error (RMSE / $\sigma$)", y = ylab_offset)
    axlist[xlab_idx].set_xlabel(r"Number of non-zero coefficients (s)", x = xlab_offset)

    plt.show()
    return
