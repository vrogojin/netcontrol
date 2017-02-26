from __future__ import division

from random import random, sample, choice



#=======
# Functions for generating random graphs
#=======================================

# generate a random Erdos-Renyi graph
# - n, V = nodes (number of, list of)
# - m, p, k = edges to generate (number, probability, average degree)
# - directed = directed or undirected graph
# - loops = allow self loops when generating the graph
#@profile
def random_graph_ER(n = None, V = None, m = None, p = None, k = None, directed = True, loops = True, fast = True) :
	# set number of vertices and their names
	assert n is not None or V is not None
	if n is None :
		assert V is not None
		n = len(V)
	if V is None :
		assert n is not None
		V = range(n)
	# compute number of edges to be generated
	total = (n * n if directed else n * (n - 1) // 2) - (0 if loops else n)
	assert m is not None or p is not None or k is not None
	if p is not None :
		assert m is None and k is None
		m = int(round(p * total))
	if k is not None :
		assert m is None and p is None
		m = int(round(k * n))
		
	if fast: # computation for large number of nodes and edges
		def generate():
			while True:
				u = choice(V)
				v = choice(V)
				if not loops and u == v:
					continue
				if directed:
					return (u, v)
				else:
					return (min(u, v), max(u, v))
		E = set()
		while len(E) < m:
			E.add(generate())
		return V, E
	# set possible edges
	if directed :
		if loops :
			edges = [(u, v) for u in V for v in V]
		else :
			edges = [(u, v) for u in V for v in V if u != v]
	else :
		if loops :
			edges = [(V[i], V[j]) for j in range(n) for i in range(j + 1)]
		else :
			edges = [(V[i], V[j]) for j in range(n) for i in range(j)]
	# return the graph
	return V, sample(edges, m)

# generate a random Barabasi-Albert graph
# TODO



#=======
# Graph I/O
#==========

# save graph to file
# - V, E = graph nodes and edges
# - filename = name of output file
# - header = information about vertices:
#   - None = don't save any information, will infer nodes from edges
#   - 'number' = write the number of vertices on the first line
#   - 'list' = write the full list of nodes on the first line, separated by spaces
def save_graph(V, E, filename, header = 'list') :
	with open(filename, 'w') as outfile :
		if header == 'list' :
			for v in V :
				outfile.write(str(v) + ' ')
			outfile.write('\n')
		elif header == 'number' :
			outfile.write(str(len(V)) + '\n')
		for (u, v) in E :
			outfile.write(str(u) + ' ' + str(v) + '\n')

# load graph from file
# - filename = name of input file
# - header = how to read information about vertices:
#   - None = no header, infer vertices from edges
#   - 'number' = header contains the number of vertices
#   - 'list' = write the full list of nodes on the first line, separated by spaces
#   - 'guess' = check whether the first line seems to be a header or not
# - force_int = True if node names are to be read as integers
def load_graph(filename, header = 'list', convert = lambda x : x, sep = ' ') :
	with open(filename, 'r') as infile :
		first_line = infile.readline().strip()
		lines = [line.strip() for line in infile.readlines() if line.strip()]
		v_info = first_line.strip().split(sep)
		if header == 'number' or header == 'guess' and len(v_info) == 1 :
			# read first line as number of nodes
			V = range(int(v_info[0]))
		elif header == 'list' or header == 'guess' and len(v_info) > 2 :
			# read first line as list of nodes
			V = [convert(v) for v in v_info]
		else :
			# there is no header, put the first line with the others
			V = []
			lines.insert(0, first_line)
		# print [line.split() for line in lines if '\t' not in line]
		E = []
		for line in lines:
			xs = line.strip().split(sep)
			if xs == []:
				break
			else:
				E.append((convert(xs[0]), convert(xs[1])))
		#E = [(convert(u), convert(v)) for line in lines if line.strip() for (u, v) in [line.strip().split(sep)[:2]]]
		if V == [] :
			V = set()
			for u, v in E :
				V.add(u)
				V.add(v)
			V = list(V)
		return V, E



#=======
# Functions for generating random targets
#========================================

# generate a random list of targets
# - n, V = nodes (number of, list of)
# - t = number of targets
def random_targets(n = None, V = None, t = None) :
	# set number of vertices and their names
	assert n is not None or V is not None
	if n is None :
		assert V is not None
		n = len(V)
	if V is None :
		assert n is not None
		V = range(n)
	# generate targets
	assert t is not None
	assert t <= n
	return sample(V, t)



#=======
# Targets I/O
#============

# save targets to file
# - targets = list of targets
# - filename = name of output file
# - sep = separator
def save_targets(targets, filename, sep = ' ') :
	with open(filename, 'w') as outfile :
		outfile.write(sep.join(str(t) for t in targets))

# load targets from file
# - filename = name of input file
# - sep = separator
# - force_int = true if entries are to be read as integers
def load_targets(filename, sep = ' ', convert = lambda x : x) :
	with open(filename, 'r') as infile :
		lines = infile.readlines()
		assert len(lines) == 1 or sep == None
		if sep is None:
			targets = [t.strip() for t in lines if t.strip()]
		else:
			targets = lines[0].split(sep)
		return [convert(t) for t in targets]



#=======
# package tests
#==============

def test_random_graph_ER() :
	print '### <random_graph_ER>'
	V, E = random_graph_ER(n = 10, m = 5)
	assert len(V) == 10 and len(E) == 5
	print V
	print E
	print '[Pass]'
	print

def test_graph_io() :
	print '### graph_io'
	filename = 'test'
	V, E = random_graph_ER(n = 20, m = 40)
	save_graph(V, E, filename, header = 'list')
	print '[Pass]' if (V, E) == load_graph(filename, header = 'list', convert = int) else '[Fail]'
	print '[Pass]' if (V, E) == load_graph(filename, header = 'guess', convert = int) else '[Fail]'
	save_graph(V, E, filename, header = 'number')
	print '[Pass]' if (V, E) == load_graph(filename, header = 'number', convert = int) else '[Fail]'
	print '[Pass]' if (V, E) == load_graph(filename, header = 'guess', convert = int) else '[Fail]'
	save_graph(V, E, filename, header = None)
	print '[Pass]' if E == load_graph(filename, header = None, convert = int)[1] else '[Fail]'
	print '[Pass]' if E == load_graph(filename, header = 'guess', convert = int)[1] else '[Fail]'
	os.remove(filename)
	print

def test_random_targets() :
	print '### <random_targets>'
	targets = random_targets(n = 10, t = 5)
	assert len(targets) == 5
	print targets
	print '[Pass]'
	print

def test_targets_io() :
	print '### targets_io'
	filename = 'test'
	targets = random_targets(n = 50, t = 15)
	save_targets(targets, filename, sep = ' ')
	print '[Pass]' if targets == load_targets(filename, sep = ' ', convert = int) else '[Fail]'
	save_targets(targets, filename, sep = ', ')
	print '[Pass]' if targets == load_targets(filename, sep = ', ', convert = int) else '[Fail]'
	targets = random_targets(V = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'], t = 5)
	save_targets(targets, filename, sep = ' ')
	print '[Pass]' if targets == load_targets(filename, sep = ' ') else '[Fail]'
	save_targets(targets, filename, sep = ', ')
	print '[Pass]' if targets == load_targets(filename, sep = ', ') else '[Fail]'
	print

if __name__ == '__main__' :
	import os
	test_random_graph_ER()
	test_graph_io()
	test_random_targets()
	test_targets_io()
	print 'done'



####### update or remove #######

# test for connected components (more general than that, test for disjoint sets of targets, as far as reachability is concerned)
#@profile
def split_graph(pred, targets) :
	print 'computing ancestors ... ' + ' '.ljust(SIZE),
	anc = {}
	for i in range(len(targets)) :
		print '\b' * (SIZE + 1) + repr(i).ljust(SIZE),
		t = targets[i]
		queue = pred[t]
		anc[t] = {t}
		while queue :
			u = queue.pop(0)
			if u not in anc :
				anc[t].add(u)
				for v in pred[u] :
					if v not in anc[t] and v not in queue :
						queue.append(v)
	print '\b' * (SIZE + 1) + '[ok]'
	print 'grouping targets ... ' + ' '.ljust(SIZE),
	groups = []
	queue = [({t}, anc[t]) for t in targets]
	while queue :
		print '\b' * (SIZE + 1) + repr(len(queue)).ljust(SIZE),
		ts1, bs1 = queue.pop(0)
		updated = False
		for k in range(len(groups)) :
			(ts2, bs2) = groups[k]
			if bs1 & bs2 :
				queue.append((ts1 | ts2, bs1 | bs2))
				del groups[k]
				updated = True
				break
		if not updated :
			groups.append((ts1, bs1))
	print '\b' * (SIZE + 1) + '[ok]'
	print 'groups: ', len(groups)
	for (ts, bs) in groups :
		print str(len(ts)) + '/' + str(len(bs)),
	print
	print
