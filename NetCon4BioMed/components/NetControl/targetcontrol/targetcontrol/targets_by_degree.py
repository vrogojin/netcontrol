"""Generates target files by sorting the nodes based on their degree.

Usage:
	targets_by_degree [-r NUM_RANDOMS] [-T | -S]-g GRAPH_FILE

The script generates several targets file for a given graph file, by
sorting the nodes of the graph based on their (in, out, or overall)
degree. Additionally, a number of NUM_RANDOMS (default is 1) files
will be generated. The generated files are the following:
- targets_in_asc.txt   -- nodes sorted ascending by in degree
- targets_in_desc.txt  -- nodes sorted descending by in degree
- targets_out_asc.txt  -- nodes sorted ascending by out degree
- targets_out_desc.txt -- nodes sorted descending by out degree
- targets_deg_asc.txt  -- nodes sorted ascending by overall degree
- targets_deg_desc.txt -- nodes sorted descending by overall degree
- targets_rand_X.txt   -- nodes sorted randomly

Arguments:

-r | --num-randoms=N   -- number of random targets files to generate
-h | --help            -- print this information and exit
-T | --tab-separated   -- tab-separated list of edges
-S | --space-separated -- space-separated list of edges (default)
"""


from __future__ import division

import getopt
import random
import sys
from os import path

from aux import graph



def generate_targets(filename, randoms = 1, separator = " "):
	# load graph from file
	V, E = graph.load_graph(g_filename, header = None, sep = separator)
	# compute in degree and out degree for each node
	in_deg = {v: 0 for v in V}
	out_deg = {v: 0 for v in V}
	for (u, v) in E:
		in_deg[v] += 1
		out_deg[u] += 1
	# sorting strategies
	strategy = {
		"in_asc": lambda x: (in_deg[x], x),
		"in_desc": lambda x: (-in_deg[x], x),
		"out_asc": lambda x: (out_deg[x], x),
		"out_desc": lambda x: (-out_deg[x], x),
		"deg_asc": lambda x: (in_deg[x] + out_deg[x], x),
		"deg_desc": lambda x: (-in_deg[x] - out_deg[x], x),
	}
	strategy.update({"rand_" + str(i + 1): lambda x: random.random() for i in range(num_randoms)})
	# compute folder location for graph (also where targets are saved)
	g_folder = path.dirname(g_filename)
	# compute targets file for each sorting strategy
	for name in strategy:
		t_filename = path.join(g_folder, "targets_" + name + path.extsep + "txt")
		V.sort(lambda x, y: cmp(strategy[name](x), strategy[name](y)))
		graph.save_targets(V, t_filename)

if __name__ == "__main__":
	run_str = "Try 'targets_by_degree --help' for more information."
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hr:ST", ["num-randoms=", "space-separated", "tab-separated", "help"])
	except getopt.GetoptError as err:
		print err
		print run_str
		sys.exit(0)
	separator = " "
	num_randoms = 1
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print __doc__
		elif opt in ("-S", "--space-separated"):
			separator = " "
		elif opt in ("-T", "--tab-separated"):
			separator = "\t"
		elif opt in ("-r", "--num-randoms"):
			num_randoms = int(arg)
		else:
			print "unrecognized option: {}".format(opt)
	if len(args) != 1:
		print "Please provide exactly one graph."
		sys.exit(0)
	g_filename = args[0]
	generate_targets(g_filename, randoms = num_randoms, separator=separator)
