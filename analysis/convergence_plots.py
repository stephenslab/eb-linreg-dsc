import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pymir import mpl_stylesheet
from pymir import mpl_utils
from pymir import pd_utils

import methodprops

import numpy as np


def get_dimensions(nblocks, nrow, ncol, wspace, hspace, padheight, figwidth = 12, aspectratio = 1.0):
    axwidth  = figwidth / (ncol + (ncol - 1) * wspace)
    axheight = axwidth * aspectratio
    blockheight = nrow * axheight + (nrow - 1) * axheight * hspace
    figheight   = blockheight * nblocks + padheight * (nblocks - 1)
    return figheight, blockheight, axheight, axwidth

def get_block_gridspec(figh, nblocks, blockh, padh, nrow, ncol, debug = False):
    blockfrac = blockh / figh
    padfrac   = padh / figh
    gslist    = [None for x in range(nblocks)]
    for i in range(nblocks):
        top = 1.0 - (i * (padfrac + blockfrac))
        bottom = top - blockfrac
        if ((i == nblocks - 1) and (np.isclose(bottom, 0))): bottom = 0
        if debug: print (top, bottom)
        gslist[i] = gridspec.GridSpec(nrow, ncol, top = top, bottom = bottom)
    return gslist



def add_block_axes(fig, nrow, ncol, wspace, hspace, axwidth, axheight, gs, sharey = False):
    gs.update(wspace = wspace, hspace = hspace)
    axlist = [None for i in range(nrow * ncol)]
    for i in range(nrow):
        for j in range(ncol):
            if j == 0:
                axlist[i * ncol + j] = fig.add_subplot(gs[i,j])
            else:
                if sharey:
                    axlist[i * ncol + j] = fig.add_subplot(gs[i,j], sharey = axlist[i * ncol])
                else:
                    axlist[i * ncol + j] = fig.add_subplot(gs[i,j])
    return axlist


def create_single_method_score_distribution_plot(data, method, dim_list, rho_list, pve_list, sfracs, colname):
    ncol    = 4
    nrow    = 2
    wspace  = 0.2
    hspace  = 1.5
    aspect  = 0.7
    xscale  = 'log10'
    yscale  = 'log10'
    nan_pos = -1.5
    figw    = 12

    figh, blockh, axh, axw = get_dimensions(1, nrow, ncol, wspace, hspace, 0, aspectratio = aspect)
    fig  = plt.figure(figsize = (figw, figh))
    gs   = gridspec.GridSpec(nrow, ncol)
    gs.update(wspace = wspace, hspace = hspace)

    pm = methodprops.plot_metainfo()[method]
    figtitle = f"{pm.label}"
    xlab_offset = - wspace / 2 if ncol % 2 == 0 else 0.5
    ylab_offset = (1 + hspace / 2) if nrow % 2 == 0 else 0.5

    axrow = list()
    for i, dim in enumerate(dim_list):
        xvals  = [max(1, int(x * dim[1])) for x in sfracs]
        axlist = list()
        allscores = list()
        resdf  =  pd_utils.select_dfrows(data, [f"$(simulate.dims) == '({dim[0]},{dim[1]})'"])
        for j, rho in enumerate(rho_list):
            for k, pve in enumerate(pve_list):
                colnum = j * 2 + k
                if len(axlist) == 0:
                    ax = fig.add_subplot(gs[i, colnum])
                    ax.text(0, 1.3, f"n = {dim[0]}",
                            va = 'bottom', ha = 'left', transform = ax.transAxes)
                else:
                    ax = fig.add_subplot(gs[i, colnum], sharey = axlist[0])
                ax.text(0.5, 1.05, f"pve = {pve:g}, " + r"$\rho$ = {:g}".format(rho),
                        va = 'bottom', ha = 'center', transform = ax.transAxes)

                # Main plot
                mconditions  = [f"$(fit) == {method}"]
                mconditions += [f"$(simulate.rho) == {rho}"]
                mconditions += [f"$(simulate.pve) == {pve}"]
                for s, sfrac in enumerate(sfracs):
                    scondition = [f"$(simulate.sfrac) == {sfrac}"]
                    dfselect   = pd_utils.select_dfrows(resdf, mconditions + scondition)
                    scores     = dfselect[colname].to_numpy()
                    num_nan    = np.sum(np.isnan(scores))
                    xpos       = mpl_utils.scale_list([xvals[s]], scale = xscale)
                    yvals      = mpl_utils.scale_array(scores[~np.isnan(scores)], scale = yscale)
                    ax.scatter(xpos * len(yvals), yvals, alpha = 0.5)
                    ax.text(xpos[0], nan_pos, f"{num_nan}", ha='center', va='bottom')

                # Tick marks and axes decoration
                mpl_utils.set_xticks(ax, scale = xscale, tickmarks = xvals, rotation = 90)
                ax.tick_params(labelcolor = "#333333", left = False)
                if len(axlist) > 0: ax.tick_params(labelleft = False)
                mpl_utils.decorate_axes(ax, hide = ["left", "right", "top"], ticklimits = True, pads = [34, 10])
                mpl_utils.set_xticks(ax, scale = xscale, tickmarks = xvals, rotation = 90)
                for side, border in ax.spines.items():
                    if side == "top": border.set_visible(True)
                ax.grid(which = 'major', axis = 'y', ls = 'dotted')
                axlist.append(ax)
        '''
        Following indices are now hard-coded
        '''
        axlist[2].set_xlabel(r"Number of non-zero coefficients (s)", x = xlab_offset)
        mpl_utils.set_yticks(axlist[0], scale = yscale, spacing = 'log10')
        axlist[0].text(0, nan_pos, f'nan', ha='right', va='bottom')
        axrow.append(axlist)

    axrow[1][0].set_ylabel(r"Prediction Error (RMSE / $\sigma$)", y = ylab_offset)
    axrow[0][2].set_title(figtitle, x = xlab_offset, pad = 40)

    plt.show()
    return


def create_single_setting_score_evolution_plot(data, method, dim, sfrac, pve, rho_list):
    mpl_stylesheet.banskt_presentation(fontsize = 12)

    ncol    = 10
    nrow    = 2
    wspace  = 0.05
    hspace  = 0.05
    axwidth = 1.2
    aspect  = 1
    xscale  = 'linear'
    yscale  = 'log10'
    fgap    = 0.05
    pm      = methodprops.plot_metainfo()[method]

    figw  = ncol * axwidth
    axheight = axwidth * aspect
    subfigh  = nrow * axheight + hspace * (nrow - 1) * axheight
    figh  = (subfigh * 2) / (1 - fgap)
    fig   = plt.figure(figsize = (figw, figh))

    # Hard-coded Gridspec
    gs    = [None for x in rho_list]
    gs[0] = gridspec.GridSpec(nrow, ncol, top = 1.0, bottom = 0.5 + fgap)
    gs[1] = gridspec.GridSpec(nrow, ncol, top = 0.5 - fgap, bottom = 0.0)
    nplot = ncol * nrow * len(gs)

    axlist = [list() for x in rho_list]
    for ig, rho in enumerate(rho_list):
        gs[ig].update(wspace = wspace, hspace = hspace)
        for i, scores in enumerate(data[rho]):
            rownum = int (i / ncol)
            colnum = i - rownum * ncol
            ax = fig.add_subplot(gs[ig][rownum, colnum])
            ax.tick_params(left = False, labelleft = False, bottom = False, labelbottom = False)
            mpl_utils.decorate_axes(ax, hide = ["all"])
            ax.plot(np.arange(scores.shape[0]), np.log10(scores), lw = 1)
            ax.set_facecolor('#E8E8E8')
            axlist[ig].append(ax)
        pcaus    = max(1, int(sfrac * dim[1]))
        figtitle = f"{pm.label} (n = {dim[0]}, p = {dim[1]}, s = {pcaus}, " + r"$\rho$ = " + f"{rho}, pve = {pve})"
    
        xlab_idx    = int(ncol / 2)
        xlab_offset = - wspace / 2 if nplot % 2 != 0 else 0
        axlist[ig][xlab_idx].set_title(figtitle, x = xlab_offset, pad = 10)
    
    #ncol * int(nrow / 2)
    ylab_offset = 1 + figh * fgap
    axlist[1][0].set_ylabel(r"$\log_{10}$(RMSE / $\sigma$)", 
                            y = ylab_offset)
    axlist[1][15].set_xlabel(r"Number of iterations", x = xlab_offset)
    
    plt.show()
    return
