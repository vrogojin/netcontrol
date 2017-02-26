from __future__ import division

from copy import deepcopy

from aux.graph import random_graph_ER
from aux.utils import has_duplicates
from matching import max_matching
from matrix import is_controllable
from heuristics import get_heuristics




#=======
# parameters I/O
#===============

def load_parameters(filename) :
    with open(filename, 'r') as hfile :
        lines = [line.split() for line in hfile if line.strip() and line[0] != "#"]
        params = [{
            'cut_to_driven' : line[0] == 'T',
            'cut_non_branching' : line[1] == 'T',
            'repeat' : int(line[2]),
            'heuristics' : get_heuristics(line[3]),
            'name' : line[0] + line[1] + line[2] + line[3],
        } for line in lines]
        return params



class TCInfo :
	### initialize state ###
	
	def __init__(self, _V, _E, _targets, _control_path, _controllable) :
		# save input graph
		self.n = len(_V)
		self.V = deepcopy(_V)
		self.E = deepcopy(_E)
		self.controllable = deepcopy(_controllable)
		# pred[node] = list of predecessors of node
		self.pred = { v : [] for v in self.V }
		for (u, v) in self.E :
			self.pred[v].append(u)
		# control_path[target] = control path from target towards driven
		# * for controlled targets, append None to the end of the path
		# * this is the main data structure, can extract others from this
		# @ elements at the same index are all distinct (if not None)
		if _control_path :
			self.control_path = deepcopy(_control_path)
		else :
			self.control_path = { t : [t] for t in _targets }
		# control_of[target] = driven node that controls target
		self.control_of = self.compute_control_of()
		# controlled_by[driven] = list of targets controlled by driven
		self.controlled_by = self.compute_controlled_by()
		# path_v[node] = { index : target }
		# - target = target whose path contains node
		# - index = index of node in path of target
		# @ each node can appear in at most one path for a given index
		self.path_v = self.compute_path_v()
		# path_e[edge] = { index : target }
		# - target = target whose path contains edge
		# - index = index of edge in path of target (index of first node)
		self.path_e = self.compute_path_e()
		# current step and corresponding targets
		# @ current_targets = path_of[uncontrolled target][current_step]
		# @ path of uncontrolled targets must have length = current_step + 1
		self.current_step = 0
		self.current_targets = self.compute_current_targets()
		# test that everything was initialized properly
		assert self.is_consistent()

	### compute parts of the internal state ###

	# compute 'control_of' based on 'control_path'
	def compute_control_of(self) :
		return { t : self.control_path[t][-2] for t in self.control_path if self.control_path[t][-1] is None }
	
	# compute 'controlled_by' based on 'control_of'
	def compute_controlled_by(self) :
		ret = {}
		for t, d in self.control_of.items() :
			if d not in ret :
				ret[d] = {t}
			else :
				ret[d].add(t)
		return ret
	
	# compute 'path_v' based on 'control_path'
	def compute_path_v(self) :
		ret = { v : {} for v in self.V }
		for t, path in self.control_path.items() :
			for i in range(len(path)) :
				v = path[i]
				if v is not None :
					ret[v][i] = t
		return ret

	# compute 'path_e' based on 'control_path'
	def compute_path_e(self) :
		ret = { (v, u) : {} for u, v in self.E }
		for t, path in self.control_path.items() :
			for i in range(len(path) - 1) :
				e = (u, v) = (path[i], path[i + 1])
				if v is not None :
					ret[e][i] = t
		return ret

	# compute 'current_targets' based on 'control_path' and 'control_of'
	def compute_current_targets(self) :
		return { self.control_path[t][self.current_step] for t in self.control_path if t not in self.control_of and len(self.control_path[t]) == self.current_step + 1 }

	### test state for consistency ###

	# relies on assertions to test that the data structures are ok
	# run with '-O' to disable assertions
	def is_consistent(self, ignore_current = False) :
		# make sure that graph is consistent across representations
		for v in self.V :
			for u in self.pred[v] :
				assert (u, v) in self.E
		# tests for control_path to make sure it is consistent
		for t, path in self.control_path.items() :
			assert t in self.V, str(t) + ' not in ' + str(self.V)
			for i in range(len(path) - 1) :
				assert (path[i + 1], path[i]) in self.E or path[i + 1] is None, 'edge ' + str((path[i], path[i + 1])) + ' not in E'
		# test for all other data structures
		assert self.control_of == self.compute_control_of()
		assert self.controlled_by == self.compute_controlled_by()
		assert self.path_v == self.compute_path_v()
		assert self.path_e == self.compute_path_e()
		if not ignore_current :
			assert self.current_targets == self.compute_current_targets()
		return True

	### functions related to the algorithm ###
	
	def is_final(self) :
		return  not self.current_targets
	
	def advance_step(self) :
		assert not self.current_targets
		self.current_step += 1
		self.current_targets = self.compute_current_targets()
	
	# sets a current target as driven
	def set_driven(self, v) :
		assert v in self.current_targets
		assert v not in self.controlled_by
		t = self.path_v[v][self.current_step]
		self.control_path[t].append(None)
		self.control_of[t] = v
		self.controlled_by[v] = {t}
		self.current_targets.remove(v)
		assert self.is_consistent()
	
	# adds an edge for the control of a current target
	def add_edge(self, v, u) :
		assert (u, v) in self.E # valid edge
		assert v in self.current_targets
		t = self.path_v[v][self.current_step]
		self.control_path[t].append(u)
		self.path_v[u][self.current_step + 1] = t
		self.path_e[(v, u)][self.current_step] = t
		self.current_targets.remove(v)
		if u in self.controlled_by :
			self.control_path[t].append(None)
			self.control_of[t] = u
			self.controlled_by[u].add(t)
		assert self.is_consistent()
		
	# removes control of target
	# returns True if target was only controlled by driven
	def remove_control_of(self, t) :
		assert self.control_path[t][-1] is None
		self.control_path[t].pop()
		d = self.control_path[t][-1]
		del self.control_of[t]
		self.controlled_by[d].remove(t)
		if not self.controlled_by[d] :
			del self.controlled_by[d]
			ret = True
		else :
			ret = False
		assert self.is_consistent(ignore_current = True)
		return ret
	
	# removes node from path
	def remove_edge_from(self, t) :
		assert t in self.control_path
		assert len(self.control_path[t]) >= 2
		v = self.control_path[t].pop()
		u = self.control_path[t][-1]
		del self.path_v[v][len(self.control_path[t])]
		del self.path_e[(u, v)][len(self.control_path[t]) - 1]
		assert self.is_consistent(ignore_current = True)

	# remove edges up to a given node
	def shorten_path(self, t, d) :
		assert d in self.control_path[t]
		while d in self.control_path[t][:-1] :
			self.remove_edge_from(t)
		assert self.is_consistent(ignore_current = True)
	
	# set path controlled (by its last node)
	def set_controlled(self, t) :
		assert t in self.control_path
		assert t not in self.control_of
		d = self.control_path[t][-1]
		self.control_of[t] = d
		if d not in self.controlled_by :
			self.controlled_by[d] = set()
		self.controlled_by[d].add(t)
		self.control_path[t].append(None)
		assert self.is_consistent()
	
	# updates control paths to account for later driven nodes
	# returns number of driven nodes 
	def update_control_paths(self, d) :
		if d not in self.controlled_by :
			return 0
		count = 0
		for t in set(self.path_v[d].values()) :
			if t in self.controlled_by[d] :
				# target already controlled by d, just check for repetitions
				if d in self.control_path[t][:-2] :
					self.remove_control_of(t)
					self.shorten_path(t, d)
					self.set_controlled(t)
			elif t in self.control_of :
				# target controlled, but by another driver node
				if self.remove_control_of(t) :
					count += 1
				self.shorten_path(t, d)
				self.set_controlled(t)
			else :
				# target not controlled before
				self.shorten_path(t, d)
				self.set_controlled(t)
		assert self.is_consistent()
		return count

	### partition the predecessors of a node, for heuristics ###

	# Define types of predecessor nodes. First approach considers the
	# predecessor nodes independently of the current node, whereas the
	# second one (denoted with @) considers the current node as well.
	#
	# Use concatenation to denote intersection of several sets.
	def compute_hpred(self, nodes) :
		assert set(nodes) <= set(self.current_targets) # don't compute this for already driven nodes
		ret = {}
		for v in nodes :
			ret[v] = { h : set() for h in ['#P', '#N', '@C', '@P', '@N', '@O', '@L', '@A', 'T', 'N', 'D', 'C', 'P', 'O', 'L', 'A', 'K', 'X' ] }
			tv = self.path_v[v][self.current_step]
			# types of nodes w.r.t. (v, u) -- edge
			for u in self.pred[v] :
				# constranints related to paths and control
				if not self.path_e[(v, u)] :
					ret[v]['@N'].add(u) # New predecessor
				elif any(t in self.control_of for t in self.path_e[(v, u)].values()) :
					ret[v]['@C'].add(u) # Control path predecessor
				else :
					ret[v]['@P'].add(u) # Previously seen predecessor
				# constraints related to closing loops
				if tv in self.path_e[(v, u)].values() :
					ret[v]['@O'].add(u) # follows loop on current path
				elif has_duplicates(self.path_e[(v, u)].values()) :
					ret[v]['@L'].add(u) # follows loop on another path
				else :
					ret[v]['@A'].add(u) # acyclic
			# combine for finer grained sets
			ret[v]['@CO'] = ret[v]['@C'] & ret[v]['@O']
			ret[v]['@CL'] = ret[v]['@C'] & ret[v]['@L']
			ret[v]['@CA'] = ret[v]['@C'] & ret[v]['@A']
			ret[v]['@PO'] = ret[v]['@P'] & ret[v]['@O']
			ret[v]['@PL'] = ret[v]['@P'] & ret[v]['@L']
			ret[v]['@PA'] = ret[v]['@P'] & ret[v]['@A']
			# types of nodes w.r.t. u -- predecessor node
			for u in self.pred[v] :
				# no constraint
				ret[v]['T'].add(u)
				# node is controllable
				if u in self.controllable:
					ret[v]['K'].add(u)
				else:
					ret[v]['X'].add(u)
				# constraints related to paths and control
				if not self.path_v[u] :
					ret[v]['N'].add(u) # new node
				elif u in self.controlled_by :
					ret[v]['D'].add(u) # driven node
				elif any(t in self.control_of for t in self.path_v[u].values()) :
					ret[v]['C'].add(u) # controlled node
				else :
					ret[v]['P'].add(u) # previously seen node
				# constraints related to cycles
				if u in self.control_path[tv] :
					ret[v]['O'].add(u) # node closes cycle on current path
				elif has_duplicates(self.path_v[u].values()) :
					ret[v]['L'].add(u) # node closes a cycle on another path
				else :
					ret[v]['A'].add(u) # acyclic
			# combine various constraints for finer grained sets
			ret[v]['DO'] = ret[v]['D'] & ret[v]['O']
			ret[v]['DL'] = ret[v]['D'] & ret[v]['L']
			ret[v]['DA'] = ret[v]['D'] & ret[v]['A']
			ret[v]['CO'] = ret[v]['C'] & ret[v]['O']
			ret[v]['CL'] = ret[v]['C'] & ret[v]['L']
			ret[v]['CA'] = ret[v]['C'] & ret[v]['A']
			ret[v]['PO'] = ret[v]['P'] & ret[v]['O']
			ret[v]['PL'] = ret[v]['P'] & ret[v]['L']
			ret[v]['PA'] = ret[v]['P'] & ret[v]['A']
			# would it be useful to also add intersections of the two types of constraints?
			# types of nodes w.r.t. v -- current node
			if v in self.controllable:
				ret[v]['#K'] = set(self.pred[v])
				ret[v]['#X'] = set()
			else:
				ret[v]['#K'] = set()
				ret[v]['#X'] = set(self.pred[v])
			# combine current node constraints with other constraints
			ret[v]['#XA'] = ret[v]['#X'] & ret[v]['A']
			ret[v]['#XK'] = ret[v]['#X'] & ret[v]['K']
			ret[v]['#XD'] = ret[v]['#X'] & ret[v]['D']
			ret[v]['#XC'] = ret[v]['#X'] & ret[v]['C']
			ret[v]['#XP'] = ret[v]['#X'] & ret[v]['P']
			ret[v]['#KK'] = ret[v]['#K'] & ret[v]['K']
			ret[v]['#KD'] = ret[v]['#K'] & ret[v]['D']
			ret[v]['#KC'] = ret[v]['#K'] & ret[v]['C']
			ret[v]['#KP'] = ret[v]['#K'] & ret[v]['P']
			#TODO this can be remove, did not bring any added value
			if self.path_v[v].values() == [tv]:
				ret[v]['#N'] = set(self.pred[v])
				ret[v]['#P'] = set()
			else:
				ret[v]['#N'] = set()
				ret[v]['#P'] = set(self.pred[v])
			# combine current node constraints with predecessor constraints
			ret[v]['#NA'] = ret[v]['#N'] & ret[v]['A']
		return ret
		
	### compute maximal matching according to formula for heuristics ###
	
	def get_maximal_matching(self, heuristic) :
		if self.current_step < self.n - 1 :
			return self.compute_maximal_matching(heuristic, self.current_targets)
		else :
			return [], list(self.current_targets)
	
	#@profile
	def compute_maximal_matching(self, heuristics, targets) :
		#@profile
		def compute_maximum(ms, hs) :
			init_matchings, init_hs = compute_maximal(ms)
			# generate bipartite graph
			left = list(free)
			right = unmatched
			adj = { v : [] for v in left }
			for v in right :
				for h in init_hs + hs :
					for u in ppred[v][h] :
						if u in free :
							adj[u].append(v)
			# get maximum matching
			k, left_to_right, right_to_left = max_matching(left, right, adj, initial = init_matchings)
			# update free nodes, unmatched nodes, and matchings
			ret_matchings = []
			ret_hs = init_hs + hs
			for (u, v) in left_to_right.items() :
				if v is not None :
					ret_matchings.append((u, v))
					if (u, v) not in init_matchings :
						free.remove(u)
						unmatched.remove(v)
			# return matching
			return ret_matchings, ret_hs
		#@profile
		def compute_maximal(mlist) :
			ret_matchings = []
			ret_hs = []
			for (ms, hs) in mlist :
				new_matchings, new_hs = compute_maximum(ms, hs)
				ret_matchings.extend(new_matchings)
				ret_hs.extend(new_hs)
			return ret_matchings, ret_hs
		assert set(targets) <= set(self.V)
		unmatched = list(targets)
		ppred = self.compute_hpred(unmatched)
		# TODO: make sure that this makes sense !!!
		free = { v for v in self.V if self.current_step + 1 not in self.path_v[v] }
		matching = compute_maximal(heuristics)[0]
		is_set = lambda x : len(x) == len(set(x))
		l, r = zip(*matching) if matching else ([], [])
		assert is_set(l) and is_set(r)
		return matching, unmatched

	def display(self) :
		# print the graph
		print 'Graph:'
		print '-', self.n, 'nodes:', self.V
		print '- edges:', self.E
		print
		# print current step info
		print 'Current step:', self.current_step
		print 'Current targets:', self.current_targets
		print
		# print control paths
		print 'Control paths:'
		for t, path in self.control_path.items() :
			print path
		print
		# print control of each target
		print 'Control for each target:'
		for t in self.control_path :
			print t, ':', self.control_of[t] if t in self.control_of else None, ' ',
		print
		# print targets controlled by each driven
		print 'Targets controlled by each driven:'
		for d, controlled in self.controlled_by.items() :
			print d, ':', list(controlled)
		print



# Computes target control information
#
# Inputs :
# - V = graph vertices
# - E = graph edges
# - targets = set of target nodes
# - hlist = list of pairs (string, bool) identifying heuristics
#   - string is a name identifying the heuristic
#   - bool indicates whether matching edges are to be enforced or not
# Output : dictionary with the following values
# - 'driven' = the list of driven nodes
# - 'path' = control path for each target (dictionary)
# - 'cycles' = set of driven nodes that close cycles
# - 'control' = list of targets controlled by each driven node (dictionary)
#@profile
def target_control(V, E, targets, heuristics = None, controllable = [], repeat = 1, cut_to_driven = True, cut_non_branching = False, verbose = False, test = False, **kwd) :
	# count the nodes removed by the cut_paths optimization
	# will report this number in the verbose version
	cut_paths_count = 0
	# count the path reduction caused by non-branching control
	# as well as the driven nodes saved by this optimization
	# report this in verbose mode
	cut_non_branching_paths = 0
	cut_non_branching_nodes = 0

	init_control_path = None

	### run algorithm ###
	runs = 0
	while runs < repeat :
		state = TCInfo(V, E, targets, init_control_path, controllable)
		while not state.is_final() :
			matched, unmatched = state.get_maximal_matching(heuristics)
			for v in unmatched :
				state.set_driven(v)
			for (u, v) in matched :
				state.add_edge(v, u)
			
			### OPTIMIZATION: cut paths containing a later found driven node ###
			if cut_to_driven :
				for v in unmatched :
					cut_paths_count += state.update_control_paths(v)

			state.advance_step()
				
		# test that all is still in order
		assert state.is_consistent()

		### OPTIMIZATION: reduce paths that don't branch ###
		if cut_non_branching :
			ready = False
			while not ready :
				ready = True
				for d in state.controlled_by.keys() :
					if d in state.control_path :
						# d is also a target, can't reduce control paths
						continue
					if d not in state.controlled_by :
						# d was already removed from the driven set
						continue
					nexts = { state.control_path[t][-3] for t in state.controlled_by[d] }
					if len(nexts) == 1 :
						# next state is same for all paths starting at d
						ready = False
						d_new = list(nexts)[0]
						cut_non_branching_paths += 1
						for t in list(state.controlled_by[d]) :
							state.remove_control_of(t)
							state.shorten_path(t, d_new)
							state.set_controlled(t)
						cut_non_branching_nodes += state.update_control_paths(d_new)
			assert state.is_consistent()
		runs += 1
		if verbose :
			print 'driven nodes for run', runs, ':', len(state.controlled_by)
		if runs < repeat :
			# prepare for continuation
			for d in state.controlled_by.keys() :
				if len(state.controlled_by[d]) == 1 :
					t = list(state.controlled_by[d])[0]
					state.remove_control_of(t)
					state.shorten_path(t, t)
			assert state.is_consistent()
			init_control_path = state.control_path

	if test :
		if is_controllable(V, E, state.controlled_by.keys(), targets) :
			print 'PASS'
		else :
			print 'FAIL'

	if verbose :
		if cut_to_driven :
			print 'driven nodes saved by cutting paths:', cut_paths_count
		if cut_non_branching :
			print 'non-branching paths reduced:', cut_non_branching_paths
			print 'non-branching paths saved nodes:', cut_non_branching_nodes
	return { 
		'driven' : state.controlled_by.keys(), 
		'path' : state.control_path, 
		'controlled': state.controlled_by,
		'control' : state.control_of }

# computes full control (driver and driven)
def full_control(V, E, attempts = 1) :
	n = len(V)
	adj = {u : [] for u in V}
	# run maximum matching several times to get an upper bound for the
	# driven control and the exact number of nodes for driver control
	min_cycles = n
	cycles_list = []
	for i in range(attempts) :
		for (u, v) in E :
			adj[u].append(v)
		matching, left_to_right, right_to_left = max_matching(V, V, adj)
		cycles = 0
		unseen = list(V)
		while unseen :
			u = unseen.pop()
			v = u
			while right_to_left[v] is not None :
				v = right_to_left[v]
				if v in unseen :
					unseen.remove(v)
				if v == u :
					cycles += 1
					break
		cycles_list.append(cycles)
		if cycles < min_cycles :
			min_cycles = cycles
	driver = n - matching if matching < n else 1
	driven = (n - matching) + min_cycles
#	print 'driver:', driver, 'driven:', driven, 'cycles:', cycles_list
	return (driver, driven)



# computes the minimum possible number of extra driven nodes that are
# required in order to control the targets, given a set of controllable
# nodes
def min_extra_driven(V, E, targets, controllable):
	non_controllable_targets = [u for u in targets if u not in controllable]
	adj = {v: [] for v in non_controllable_targets}
	for (u, v) in E:
		if v in adj:
			adj[v].append(u)
	matching, left_to_right, right_to_left = max_matching(non_controllable_targets, V, adj)
	return len(non_controllable_targets) - matching



#=======
# package tests
#==============

if __name__ == '__main__' :
	full_control(*random_graph_ER(n = 50, m = 200))
	exit(0)
	V = ['u', 'u1', 'u2', 'v1', 'v2', 't', 't1']
	E = [('v1', 'u1'), ('v1', 'u'), ('v2', 'u2'), ('v2', 'u'), ('u1', 't1'), ('u', 't')]
	targets = ['t1', 't', 'u', 'u2']
	from heuristics import Hi
	print target_control(V, E, targets, Hi(['T']))
