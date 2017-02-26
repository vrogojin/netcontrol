from __future__ import division

import sqlite3
import matplotlib.pyplot as plt
from plotting import plot
from batch_run import read_run_config, read_heuristics_config, generate_run_config
from heuristics import hstr

import ast
from os import path

import sys
import glob
import getopt

#@profile
def run_analysis(db_filename, heu_filename, in_filename, data = "driven"):
    # parameter configuration for analysis
    in_config = ast.literal_eval(open(in_filename, 'r').read())
    tfractions = in_config['tfractions']
    scenarios = in_config['scenarios']

    # read heuristics configuration file and extract paramters
    params = read_heuristics_config(heu_filename)

    # read inputs configuration file and extract (graphs, targets) pairs
    inputs = generate_run_config(db_filename, **in_config) # pylint: disable=star-args

    # prepare plot
    fig, ax = plt.subplots(nrows=len(scenarios), ncols=1)
    if len(scenarios) == 1:
        ax = [ax]

    # open database and prepare to read data
    with sqlite3.connect(db_filename) as connection:
        c = connection.cursor()

        # draw each plot separately
        ymax = 0 # to scale all plots to the same axes
        for i in range(len(scenarios)):
            s = scenarios[i]
            # plot reference line
            if data == "driven":
                ax[i].plot([0, 1], [0, 1], color='black')
            # plot line for each heuristics
            for param in params:
                # read data from database
                runs_dict = {}
                for (gs, ts) in inputs[i]:
                    # extract full driven information
                    full_driven = {g[0] : g[1] for g in gs}
                    # collect runs info
                    runs = c.execute(
                        '''SELECT graph_id, targets_id, {} FROM runs
                           WHERE graph_id IN ({})
                                 AND targets_id IN ({})
                                 AND heuristics = ?
                                 AND cut_to_driven = ?
                                 AND cut_non_branching = ?
                                 AND repeat = ?
                               '''.format(data if data == "driven" else "ptime",
                               "'" + "','".join(g[0] for g in gs) + "'",
                                "'" + "','".join(ts) + "'"),
                        (hstr(param['heuristics']),
                         1 if param['cut_to_driven'] else 0,
                         1 if param['cut_non_branching'] else 0,
                         param['repeat']
                         )).fetchall()
                    for (g, t, d) in runs:
                        if (g, t) not in runs_dict:
                            runs_dict[(g, t)] = []
                        if data == "driven":
                            runs_dict[(g, t)].append(d / full_driven[g])
                        else: # data == "time"
                            runs_dict[(g, t)].append(d)
                # aggregate data for plotting
                y = []
                for itf in range(len(tfractions)):
                    res = []
                    for (gs, ts) in inputs[i]: # each number of nodes
                        res_g = []
                        for g in gs: # each graph
                            res_t = []
                            for t in ts[s['tcount'] * s['tgroup'] * itf : s['tcount'] * s['tgroup'] * (itf + 1)]: # each target
                                if s['rcount'] is not None:
                                    res_r = runs_dict[(g[0], t)][s['roffset'] : s['roffset'] + s['rcount'] * s['rgroup']]
                                else:
                                    res_r = runs_dict[(g[0], t)][s['roffset'] :]
                                assert len(res_r) == s['rcount'] * s['rgroup'], str(len(res_r)) + ' ' + in_filename
                                # group and aggregate runs
                                res_rg = []
                                aggregate = min if 'rmethod' in s and s['rmethod'] == "min" else lambda x: sum(x) / len(x)
                                for irg in range(s['rcount']):
                                    res_rg.append(aggregate(res_r[irg * s['rgroup']: (irg + 1) * s['rgroup']]))
                                res_t.append(res_rg)
                            # group and aggregate targets
                            res_tg = []
                            for itg in range(s['tcount']):
                                if s['tgroup'] == 1:
                                    res_tg.extend(res_t[itg])
                                else:
                                    t_sum = 0
                                    for it in range(s['tgroup']):
                                        t_sum += sum(res_t[itg * s['tgroup'] + it])
                                    res_tg.append(t_sum / s['tgroup'] / s['rcount'])
                            res_g.append(res_tg)
                        # group and aggregate graphs
                        res_gg = []
                        for igg in range(s['gcount']):
                            if s['ggroup'] == 1:
                                res_gg.extend(res_g[igg])
                            else:
                                g_sum = 0
                                for ig in range(s['ggroup']):
                                    g_sum += sum(res_g[igg * s['ggroup'] + ig])
                                res_gg.append(g_sum / s['ggroup'] / s['tcount'])
                        res.extend(res_gg)
                    y.append(res)
                # plot data
                plot([0] + tfractions, [[0]] + y, ax[i], label=param['name'], **s['plot'])
            ax[i].legend(loc='upper left', prop={'size' : 10})
            ycrt = ax[i].get_ylim()[1]
            ymax = max(ymax, ycrt)
        # scale to use the same axes for all plots
        for i in range(len(scenarios)):
            ax[i].set_ylim([0, ymax])
        fig.suptitle(path.basename(in_filename)[:-3])
        plt.savefig(in_filename[:-3] + '.jpg')
        plt.show()


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:h:i:p:", ["database=", "heuristics=", "input=", "plot-type="])
    except getopt.GetoptError:
        print "analyze.py (-d | --database=)<db_filename> (-h | --heuristics=)<h_filename> (-i | --input=)<in_filename> [-p | --plot-type=] time|driven"
        sys.exit(0)
    in_filenames = []
    h_filename = ""
    db_filename = ""
    plot_type = "driven"
    for opt, arg in opts:
        if opt in ("-d", "--database"):
            db_filename = arg
        elif opt in ("-h", "--heuristics"):
            h_filename = arg
        elif opt in ("-i", "--input"):
            in_filenames = list(glob.glob(arg))
        elif opt in ("-p", "--plot-type"):
            plot_type = arg
        else:
            print "unrecognized option: {}".format(opt)
    print db_filename, h_filename, in_filenames
    for in_filename in in_filenames:
        run_analysis(db_filename, h_filename, in_filename, data = plot_type)
