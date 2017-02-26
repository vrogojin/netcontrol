from __future__ import division

from Tkinter import Tk
from tkFileDialog import askopenfilename

from control import target_control_newer, H, Hi

Tk().withdraw()
graph_file = askopenfilename()
targets_file = askopenfilename()

def geth() :
	V, s, D, d, C, c, T, t, P, p, N, n, A, l = [[x] for x in ['V', 's', 'D', 'd', 'C', 'c', 'T', 't', 'P', 'p', 'N', 'n', 'A', 'l']]
	__C, __c, __P, __p, __N, __n, __A, __l = [[x] for x in ['=C', '=c', '=P', '=p', '=N', '=n', '=A', '=l']]
	_C, _P, _N = [[x] for x in [':C', ':P', ':N']]
	return { 'heuristic' : H(H(H(Hi(D + C), P + T), N), l), 'cut_to_driven' : True, 'cut_non_branching' : True, 'repeat' : 1 }
params = geth()

# read graph
str_edges = [line.split() for line in open(graph_file).readlines()]
E = [(int(edge[0]), int(edge[1])) for edge in str_edges if len(edge) >= 2]
V = set()
for (u, v) in E :
	V.add(u)
	V.add(v)
V = list(V)
n = len(V)

# read targets
line_str = [line.split() for line in open(targets_file).readlines()]
targets_all = [int(line[1]) for line in line_str if len(line) >= 2]
targets_all = [target for target in targets_all if target in V]

ctrl_info = target_control_newer(V, E, targets_all, **params)

with open(graph_file[:-4] + '_path.txt', 'w') as rfile :
	for t, path in ctrl_info['path'].items() :
		assert path[0] == t
		assert path[-1] is None
		for v in path[:-1] :
			rfile.write(str(v) + ' ')
		rfile.write('\n')
