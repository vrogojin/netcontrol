"""Computes target control information for increasing sets of targets.

Usage:
	cumulative_control -g GRAPH_PATH -t TARGETS_PATH -H HEURISTICS_PATH

The script takes a targets file containing all the nodes of the graph
and runs the target control algorithm for top 10% of the targets, then
top 20%, and so on up to 100%. This is done for each heuristics included
in the heuristics file, then the process continues again with the first
heuristics.

The progress of the script is shown by outputing a '*' for each run of
the target control algorithm for a certain heuristics and a certain
percentage of targets. A new line is inserted upon completion of each
heuristics, and an extra new line after going through all heuristics.

Results are saved to the output file whenever the runs for one
heuristics are completed. The saved information is a table (represented
via tab-separated values) containing the following:
- on the first column, the name of the heuristics
- on the following 10 columns, the number of driven nodes obtained
for each target number
- on the following 10 columns, the corresponding runtimes of the
algorithm for each target number.

The results file name is generated by appending "_RES" to the targets
file name. If the file already exists, new results will be appended to
it. The script runs until stopped via Ctrl+C.

Arguments:
-g | --graph=PATH       -- the path for the graph file
-h | --help             --
-H | --heuristics=PATH  -- the path for the heuristics file (default is
"$TC_PATH/config/heuristics/simple_fast.txt")
-S | --space-separated  -- space-saparated list of edges
-t | --targets= PATH    -- the path for the targets file
-T | --tab-separated    -- tab-separated list of edges

Note that this script is unaware of controllable or uncontrollable
nodes. As such, the use of heuristics which make this distinction is
discouraged.
"""


from __future__ import division

import sys
import getopt
import time
from os import path

from aux import graph
from core import control
from core import heuristics
#TODO import something for time

# computes control information in a cumulative way
# the full list of nodes in some order is read from a file, then
# used to compute targets as progressively larger sets of nodes

# for each heuristics, both the computation time and the answer are
# saved and added to a file

# file is created and the header added if it does not exist already

# first column gives the heuristics, then 10 columns for the number of
# driven nodes and 10 columns for the corresponding durations, in this
# order

#@profile
def cumulative_control(g_filename, t_filename, h_filename, separator = " "):
	# read graph and targets from corresponding files
	V, E = graph.load_graph(g_filename, header = None, sep = separator)
	targets_all = graph.load_targets(t_filename, sep = " ")
	# compute target percentage for each .1 increment
	n = len(targets_all)
	if len(V) != n:
		print "targets file does not contain the same number of nodes as the graph"
		sys.exit(-1)
	targets = [targets_all[:int(round(n * (i + 1) / 10.))] for i in range(10)]
	# list of considered heuristics
	params = control.load_parameters(h_filename)
#	hlist = [
#        heuristics.get_heuristics("(->T)"), # avoid cycles
#        heuristics.get_heuristics("(->A)(->T)"), # avoid cycles
#        heuristics.get_heuristics("(->D)(->CA)(->PA)(->N)(->T)"), # linear growth, constant time
#        heuristics.get_heuristics("(->@CA)(->@PA)(->D)(->CA)(->PA)(->N)(->T)"), # better convergence towards full control
#    ]
	# open results file for appending
	r_filename = path.splitext(t_filename)[0] + "_RES" + path.extsep + "txt"
	exists = path.isfile(r_filename)
	with open(r_filename, "a", 0) as results:
		# if newly created file, add header
		if not exists:
			hdr = "\t".join(str(10 * (i + 1)) for i in range(10))
			results.write("Heuristics\t" + hdr + "\t" + hdr + "\n")
		# run tests until stopped, save data
		while True:
			for par in params:
				counts = []
				times = []
				for t in targets:
					# run and time
					start = time.clock()
					res = control.target_control(V, E, t, **par)
					times.append(time.clock() - start)
					counts.append(len(res["driven"]))
					print "*",
				# save results for current heuristics
				results.write(par["name"] + "\t") #TODO remember to change back
				results.write("\t".join(str(_c) for _c in counts) + "\t")
				results.write("\t".join(str(_t) for _t in times) + "\n")
				print
			print

if __name__ == "__main__":
	run_str = "Try 'cumulative control --help' for more information."
	# read command line arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hg:t:TS", ["help", "graph=", "targets=", "tab-separated", "space-separated"])
	except getopt.GetoptError as err:
		print err
		print run_str
		exit(0)
	# process command line arguments
	g_filename = None
	t_filename = None
	h_filename = path.expandvars("$TC_PATH/config/heuristics/simple_fast.txt")
	separator = " "
	for opt, arg in opts:
		if opt in ("-g", "--graph"):
			g_filename = arg
		elif opt in ("-t", "--targets"):
			t_filename = arg
		elif opt in ("-h", "--help"):
			print __doc__
		elif opt in ("-H", "--heuristics"):
			h_filename = arg
		elif opt in ("-S", "--space-separated"):
			separator = " "
		elif opt in ("-T", "--tab-separated"):
			separator = "\t"
		else:
			print "unrecognized option: {}".format(opt)
	# make sure all arguments are available
	if g_filename is None:
		print "Please provide the graph file name."
		print run_str
		sys.exit(0)
	if t_filename is None:
		print "Please provide the targets file name."
		print run_str
		sys.exit(0)
	# run tests for the given inputs
	cumulative_control(g_filename, t_filename, h_filename, separator=separator)
