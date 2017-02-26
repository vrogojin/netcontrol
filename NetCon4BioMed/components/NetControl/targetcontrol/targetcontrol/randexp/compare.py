from __future__ import division

import matplotlib as mpl
import matplotlib.pyplot as plt
import random

import sqlite3
import pickle


def scatter_compare(data, xnames, ynames, znames, **kwd):
    if not znames:
        grid_enhanced_scatter(data, [[(x, y) for x in xnames] for y in ynames], **kwd)
    for zname in znames:
        if xnames:
            xy_names = [[(x, y) for x in xnames] for y in xnames]
            for i in range(len(xnames)):
                xy_names[i][i] = (xnames[i], zname)
        else: # if ynames
            xy_names = [[(x, y) for x in ynames] for y in ynames]
            for i in range(len(ynames)):
                xy_names[i][i] = (zname, ynames[i])
        grid_enhanced_scatter(data, xy_names, **kwd)

def grid_enhanced_scatter(data, xy_names, **kwd):
    nrows = len(xy_names)
    ncols = len(xy_names[0])
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols)
    if nrows == 1 and ncols == 1:
        ax = [[ax]]
    elif nrows == 1:
        ax = [ax]
    elif ncols == 1:
        ax = [[x] for x in ax]
    for row in range(nrows):
        for col in range(ncols):
            xname, yname = xy_names[row][col]
            enhanced_scatter(ax[row][col], data, xname, yname, **kwd)
    plt.show()

def enhanced_scatter(ax, data, xname, yname, 
        mname = None, mvalues = None, markers = mpl.markers.MarkerStyle.filled_markers,
        cname = None, cnumeric = False, cvalues = None, cmap = plt.cm.gist_rainbow, alpha=1.0):
    # setup colors
    if cname is None:
        value = lambda d, name: 0
    elif not cnumeric:
        index = {None: None}
        count = 0
        for d in data:
            val = d[cname]
            if val not in index:
                index[val] = count
                count += 1
        value = lambda d, name: index[d[name]]
    else:
        value = lambda d, name: d[name]
    if not cnumeric and cvalues is not None:
        convert = lambda x: [cvalues[value(d, cname)] if value(d, cname) is not None else None for d in x]
    else:
        norm = mpl.colors.Normalize(clip = False)
        norm.autoscale([value(d, cname) for d in data if value(d, cname) is not None])
        convert = lambda x: mpl.cm.ScalarMappable(norm = norm, cmap = cmap).to_rgba([value(d, cname) for d in x])
    # plot
    if mname == None:
        mvalues = [None]
        selected = lambda d, val: True
    else:
        if mvalues is None:
            mvalues = list({d[mname] for d in data})
        selected = lambda d, val: d[mname] == val
    for mi in range(len(mvalues)):
        # setup marker
        mv = mvalues[mi]
        # setup x and y values
        x = [d[xname] for d in data if selected(d, mv)]
        y = [d[yname] for d in data if selected(d, mv)]
        # setup colors
        c = convert([d for d in data if selected(d, mv)])
        ax.scatter(x, y, marker = markers[mi], edgecolor = c, color = c, alpha=alpha)
        #ax.hexbin(x, y, bins=10)

hnames = pickle.load(open("hnames.txt", "r"))

def test1():
    data = pickle.load(open("sdata.txt", "r"))

    print "plotting...",

    #scatter_compare(data, ["nodes"], ["scaled_full_driver"], [], cname="degree", cnumeric=True, alpha=0.2)
    #scatter_compare(data, ["full_driver"], ["scaled_min_driven"], [], cname="degree", cnumeric=True, alpha=0.2)
    #scatter_compare(data, ["full_driver"], ["scaled_min_driven"], [], cname="nodes", cnumeric=True, alpha=0.2)

    #for deg in [2, 3, 4, 5]:
    #    scatter_compare([d for d in data if d["degree"] == deg], ["full_driver"], ["scaled_min_driven"], [], cname="scaled_targets", cnumeric=True, alpha=0.2)
#    for deg in [2, 3, 4, 5]:
#        scatter_compare([d for d in data if d["degree"] == deg], ["scaled_targets"], ["scaled_min_driven"], [], cname="scaled_targets", cnumeric=True, alpha=0.02)
#    scatter_compare([d for d in data if d["degree"] in [2, 3, 4, 5, 6]], ["scaled_targets"], ["scaled_min_driven"], [], cname="degree", cnumeric=True, alpha=0.02)
    
    for hname in hnames:
        print hname
        scatter_compare(data, ["scaled_targets"], [hname], [], alpha=0.01)

def test2():
    data = pickle.load(open("jdata.txt", "r"))
    scatter_compare(data, ["scaled_full_driver"], ["scaled_min_driven"], [], cname="heuristics")

test1()




#scatter_compare(data, ["full_driver"], ["full_driven"], [], cname="nodes", cnumeric=True, alpha=0.1)
#scatter_compare(data, ["nodes"], ["full_driver"], [], cname="degree", cnumeric=True, alpha=0.1)
#scatter_compare(data, ["nodes"], ["scaled_full_driver"], [], cname="degree", cnumeric=True, alpha=0.1)
#scatter_compare(data, ["degree"], ["scaled_full_driver"], [], cname="nodes", cnumeric=True, alpha=0.1)


#    scatter_compare(data, [], list(hnames), ["targets"], cname="data_id", cnumeric=False)

#scatter_compare(data, ["scaled_full_driven"], hnames, [], cname="nodes", cnumeric=True, alpha=0.2)
#scatter_compare(data, ["scaled_full_driven"], hnames, [], cname="degree", cnumeric=True, alpha=0.2)
#scatter_compare(data, ["scaled_full_driven"], hnames, [], cname="scaled_targets", cnumeric=True, alpha=0.2)

# good
#scatter_compare(data, ["scaled_full_driven"], ["scaled_min_driven"], [], cname="nodes", cnumeric=True, alpha=0.2)
#scatter_compare(data, ["scaled_full_driven"], ["scaled_min_driven"], [], cname="degree", cnumeric=True, alpha=0.2)
#scatter_compare(data, ["scaled_full_driven"], ["scaled_min_driven"], [], cname="scaled_targets", cnumeric=True, alpha=0.2)


#scatter_compare(data, ["scaled_targets"], ["scaled_min_driven"], [], cname="nodes", cnumeric=True, alpha=0.2)
#scatter_compare(data, ["scaled_targets"], ["scaled_min_driven"], [], cname="degree", cnumeric=True, alpha=0.2)
#scatter_compare(data, ["scaled_targets"], ["scaled_min_driven"], [], cname="scaled_targets", cnumeric=True, alpha=0.2)

print "OK"
    



#grid_enhanced_scatter(data, [[("x", "y"), ("y", "x")]], mname="type", mvalues=None, cname="type", cnumeric=False, cvalues=None)
