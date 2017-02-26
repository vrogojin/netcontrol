from __future__ import division

from sys import maxint as inf
from random import random
from collections import deque

from aux.utils import subsets, maximal



#=======
# brute-force implementations for matchings
# consider all subsets of edges and choose the good ones
#=======================================================

# brute-force maximal matchings for a given set of edges
# - note that it returns a generator
def brute_all(E) :
	for es in subsets(E) :
		if not es :
			U, V = [], []
		else :
			U, V = zip(*es)
		if len(U) == len(set(U)) and len(V) == len(set(V)) :
			yield es

# brute-force maximal matchings
def brute_maximal(E) :
	matchings = list(brute_all(E))
	return maximal(matchings)

# brute-force maximum matchings
# - only used for testing the generating approach for small graphs
def brute_maximum(E) :
	matchings = list(brute_all(E))
	m = max([len(matching) for matching in matchings])
	return m, [matching for matching in matchings if len(matching) == m]



#=======
# implementations based on generating the matchings incrementally
#================================================================

# generate all maximal matching by exploring each edge
def generate_maximal(E) :
	ret = [set()]
	for (u1, v1) in E :
		new_ret = []
		new_matchings = []
		for matching in ret :
			if any([u == u1 or v == v1 for (u, v) in matching]) :
				# cannot add edge (u1, v1) to the matching without breaking it
				new_ret.append(matching)
				new_matching = {(u, v) for (u, v) in matching if u != u1 and v != v1} | {(u1, v1)}
				new_matchings.append(new_matching)
			else :
				#can add edge (u1, v1) to get a larger matching
				new_matching = matching | {(u1, v1)}
				new_matchings.append(new_matching)
		# need to make sure we keep just the maximal matchings
		new_ret.extend(maximal(new_matchings))
		ret = new_ret
	return ret

# generate maximum matching by choosing from the maximal ones
def generate_maximum(E) :
	maximal_matchings = generate_maximal(E)
	m = max([len(matching) for matching in maximal_matchings])
	return m, [matching for matching in maximal_matchings if len(matching) == m]



#=======
# Implementation of the Hopcroft-Karp algorithm for finding a maximum matching
#=============================================================================

RAND = lambda x: random()

# Computes a maximum matching in a bipartite graph
# using the Hopcroft-Karp algorithm - O(E * sqrt(V))
# pseudocode taken from the Wikipedia page
#
# inputs:
# - U, V = sets of nodes (left side, right side)
# - Adj = adjacency list for each node
# Outputs:
# - matching = number of matched nodes
# - Pair_U, Pair_V - the maximum matching as two dictionaries
#     one shows the right matches for each of the left nodes
#     the other shows the left matches for each of thr right nodes
#     in particular, left and right nodes may have the same name
#@profile
def max_matching(U, V, Adj, initial = []) :
	# breadth first search
	#@profile
	def BFS () :
		Q = deque(u for u in U if Pair_U[u] is None)
		Dist.update({u : 0 if Pair_U[u] is None else inf for u in U})
		Dist[None] = inf
		while Q :
				u = Q.popleft()
				if Dist[u] < Dist[None] :
#					Adj[u].sort(key = lambda x : random())
					for v in Adj[u] :
						if Dist[Pair_V[v]] == inf :
							Dist[Pair_V[v]] = Dist[u] + 1
							Q.append(Pair_V[v])
		return Dist[None] != inf
	# depth first search
	#@profile
	def DFS(u) :
		if u is not None :
#			Adj[u].sort(key = lambda x : random())
			for v in Adj[u] :
				if Dist[Pair_V[v]] == Dist[u] + 1 :
					if DFS(Pair_V[v]) :
						Pair_V[v] = u
						Pair_U[u] = v
						return True
			Dist[u] = inf
			return False
		return True
	# permute adjacency lists for randomization
	for u in Adj:
		Adj[u].sort(key = RAND)
	# the actual algorithm
	Dist = {}
	Pair_U = { u : None for u in U }
	Pair_V = { v : None for v in V }
	# support for starting with an initial matching --> TEST THIS !!!
	for (u, v) in initial :
		Pair_U[u] = v
		Pair_V[v] = u
	matching = len(initial)
	while BFS() :
		for u in U :
			if Pair_U[u] is None :
				if DFS(u) :
					matching = matching + 1
	return matching, Pair_U, Pair_V



#=======
# package tests
#==============

def test_generate_maximal() :
	print '### <generate_maximal>'
	for i in range(20) :
		V, E = random_graph_ER(n = 5, m = 10)
		bm = brute_maximal(E)
		gm = generate_maximal(E)
		if any([g for g in gm if g not in bm]) or any([b for b in bm if b not in gm]) :
			print "[Fail]:", E
			break
		else :
			print '[Pass]'
	print

def test_generate_maximum() :
	print '### <generate_maximum>'
	for i in range(5) :
		V, E = random_graph_ER(n = 7, m = 15)
		m1, bm = brute_maximum(E)
		m2, gm = generate_maximum(E)
		if m1 != m2 or any([g for g in gm if g not in bm]) or any([b for b in bm if b not in gm]) :
			print "[Fail]:", E
			break
		else :
			print '[Pass]'
	print

def test_max_matching() :
	print '### <max_matching>'
	for i in range(20) :
		V, E = random_graph_ER(n = 5, m = 10)
		Adj = {v : [] for v in V}
		for (u, v) in E :
			Adj[u].append(v)
		m1, gm = generate_maximum(E)
		m2, matching, _ = max_matching(V, V, Adj)
		mm = {(u, v) for (u, v) in matching.items() if v is not None}
		if m1 != m2 or mm not in gm :
			print "[Fail]", m1, 'vs', m2, ':', mm
			print '      ', E
		else :
			print '[Pass]'
	print

def test_max_matching_randomization() :
	print '### <max_matching> randomization'
	print 'should see several different maximum matchings'
	V, E = random_graph_ER(n = 50, m = 200)
	Adj = {v : [] for v in V}
	for (u, v) in E :
		Adj[u].append(v)
	old_matching = None
	for i in range(20) :
		m, matching, _ = max_matching(V, V, Adj)
		if matching != old_matching :
			print m, '->', [(u, v) for (u, v) in matching.items() if v is not None]
			old_matching = matching
	print

def test_max_matching_initial() :
	print '### <max_matching> initial'
	V, E = random_graph_ER(n = 50, m = 200)
	Adj = {v : [] for v in V}
	for (u, v) in E :
		Adj[u].append(v)
	m, left_to_right, _ = max_matching(V, V, Adj)
	initial = sample([(u, left_to_right[u]) for u in V if left_to_right[u] is not None], m // 2)
	m2, left_to_right, right_to_left = max_matching(V, V, Adj, initial = initial)
	for (u, v) in initial :
		if left_to_right[u] is None or right_to_left[v] is None :
			print '[Fail]'
			print
			return
	print '[Pass]'
	print

if __name__ == '__main__' :
	from random import sample
	from graph import random_graph_ER
	test_generate_maximal()
	test_generate_maximum()
	test_max_matching()
	test_max_matching_randomization()
	test_max_matching_initial()
	print 'done'
