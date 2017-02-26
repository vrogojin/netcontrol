"""Runs the target control algorithm and saves the best results.

Usage:
    target_control -g GRAPH_FILE -t TARGETS_FILE

Runs the target control algorithm, cycling through a predefined list of
heuristics or, if provided, through heuristics loaded from a text file.
Optionally, a file containing controllable (i.e. drug-targetable) nodes
can be provided and heuristics may account for such nodes.

Each result is assessed based on the total number of driven nodes D and
the number of non-controllable driven nodes N (both numbers are to be
minimized). A result (D, N) from a run is considered better than the
previous results if at least one of the following holds:
- the value of D is lower than the minimum D obtained so far
- the value of N is lower than the minimum N obtained so far
- the value of D is not larger than the D value corresponding to the
minimum N obtained so far and, moreover, the value of N is lower than
the minimum N obtained so far for the same D (or is the first such
value)
- same as the above, swapping N and D.

Whenever a better result is encountered, it is saved in two text files:
- TARGETS_FILE_D_N_x_count.txt: driven nodes and the number of targets
they control, each driven node on a separate line. List is split into
controllable driven nodes and uncontrollable ones, with a new line
separating the two classes and a header line for each class.
- TARGETS_FILE_D_N_x_details.txt: the first line indicates the heuristics
which was used for obtaining the result in the file. A blank line
follows, then the names of the driven nodes, each on a separate line.
After another blank line, the control path for each target is provided.

The program will generate up to 3 files for the same (N, D) pair, the
'x' in the file name stands for the corresponding index.

The program runs until stopped and provides the following progress
information:
- whenever a better result is found, the corresponding (N, D) pair is
shown, alone on a separate line, for visibility
- results which are worse than the current bests are shown by a '*'
- results which are as good as one of the current bests are indicated
by a '@' (if N or D is equal to the current best value) or by a '#'
- a dot '.' is used to separate consecutive runs through the list of
heuristics.

In case of malformed/erroneous input, additional output will be
generated.

Arguments:

-g | --graph=PATH        -- path to graph file

-t | --targets=PATH      -- path to targets file

-C | --controllable=PATH -- path to file containing controllable nodes

-h | --help              -- print th    #outdir = kwargs.outdiris message and exit

-H | --heuristics=PATH   -- path to file containing heuristics. See the
'config/heuristics' folder for a selection of already tested heuristics.

--ref-driven=N           -- reference value D to use for the number of
driven nodes
-- ref-uncontrollable=N  -- reference value N to use for the number
of uncontrollable driven nodes.
"""

from aux.graph import load_graph, load_targets
from core.control import target_control, min_extra_driven, load_parameters
from core.heuristics import hstr, get_heuristics
import getopt
import sys
import tempfile
import time
import shutil
import argparse
import anduril
from anduril.args import *
from os import path

if __name__ == "__main__" :
    cf = anduril.CommandFile.from_file(sys.argv[1])
    g_filename = cf.get_input('graph')
    t_filename = cf.get_input('targets')
    h_filename = cf.get_input('heuristics')
    c_filename = cf.get_input('controllable')
    trials = int(cf.get_parameter('trials'))
    convergence = int(cf.get_parameter('convergence'))
    argD = cf.get_parameter('min')
    argS =  cf.get_parameter('max')
    detail_output = cf.get_output('detail')
    count_output = cf.get_output('count')
    full_output = cf.get_output('full')
    ref_extra = None
    ref_all = None
    
    print trials
        
    V, E = load_graph(g_filename, header = None, sep = "\t")
    targets = load_targets(t_filename, sep = None)
    tmpdir = tempfile.mkdtemp()
    opt_driven = c_filename is None or argD
    opt_target = not c_filename is None or argS 
    best = {"D":None , "S":None}
    fname = path.split(t_filename)[1]
    
    
    best_fname = ""
    # sanity check: all targets should be in V
    targets_not_found = [v for v in targets if v not in V]
    if targets_not_found:
        print "[error]: the following targets were not found in the graph: {}".format(", ".join(str(v) for v in targets_not_found))
        sys.exit(-1)
    params = load_parameters(h_filename)
    if c_filename is None:
        controllable = []
    else:
        controllable = load_targets(c_filename, sep = None)
    print "{} nodes, {} edges, {} targets, {} controllable, at least {} extra".format(
            len(V), len(E), len(targets), len(controllable), min_extra_driven(V, E, targets, controllable))
    try:
        best_all = {ref_extra: None} if ref_extra is not None else {}
        best_extra = {ref_all: None} if ref_all is not None else {}
        cnt = 0
        last_update = 0
        
        times_found = {}
        while True:
            cnt = cnt + 1
            if cnt>trials or cnt - last_update > convergence:
                break
            for par in params:
                better_D = better_S = False
                res = target_control(V, E, targets, controllable=controllable, **par)
                count_all = len(res["driven"])
                count_extra = len(set(res["driven"]) - set(controllable))
                count_target = sum([len(res["controlled"][t]) for t in res["controlled"] if t in controllable])

                better = False

                if opt_driven:
                    if best["D"] is None or count_all < best["D"]:
                        best["D"] = count_all
                        better_D = True
                if opt_target:
                    if best["S"] is None or count_target > best["S"]:
                        best["S"] = count_target
                        better_S=True
                better = better_D or better_S

                if not better:
                    continue
                else:
                    print count_all, count_target
                    suffix = ""
                    last_update = cnt

                best_fname = filename_base = "{}__{}_{}".format(fname, count_all, count_target)
                # save driven nodes and control paths
                with open(path.join(tmpdir ,filename_base + "_details.txt"), "w") as outfile:
                    outfile.write(par["name"] + "\n")
                    outfile.write("\n")
                    outfile.writelines(str(t) + "\n" for t in res["driven"])
                    outfile.write("\n")
                    outfile.writelines(" <- ".join(str(u) for u in res["path"][t][:-1]) + "\n" for t in res["path"])
                # tab separated list of driven nodes with the number of targets they control
                with open(path.join(tmpdir, filename_base + "_count.txt"), "w") as outfile:
                    outfile.write("Driven\tTargets\n")
                    outfile.writelines(str(t) + "\t" + str(len(res["controlled"][t])) + "\n" for t in res["controlled"] if t in controllable)
                    outfile.write("\nExtra\tTargets\n")
                    outfile.writelines(str(t) + "\t" + str(len(res["controlled"][t])) + "\n" for t in res["controlled"] if t not in controllable)
            print ".",
    except KeyboardInterrupt:
        sys.exit(0)

    # write output files here
    shutil.make_archive(path.join(tmpdir, "full_solutions"), "zip", tmpdir)
    shutil.copy(path.join(tmpdir, "full_solutions.zip"), full_output)
    shutil.copy(path.join(tmpdir, best_fname + "_details.txt"), detail_output)
    shutil.copy(path.join(tmpdir, best_fname + "_count.txt"), count_output)
    
    sys.exit(0)
    print args
    