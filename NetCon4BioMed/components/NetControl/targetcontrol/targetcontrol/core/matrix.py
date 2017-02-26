from __future__ import division

from random import random
from sympy import *
init_printing()

from aux.graph import random_graph_ER



# generate the A matrix for a given graph
# - V, E = graph vertices and edges
# - ids = True if vertices are already indices: V = range(|V|)
# - value = type of values to put in the matrix:
#   - 'symbol' = symbolic values
#   - 'sympy' = SymPy reals
#   - 'python' = Python reals
# - sparse = True if the generated matrix is sparse
# - init_first = True if the matrix is first initialized with zero
def get_A(V, E, ids = False, value = 'python', sparse = True, init_first = True) :
	n = len(V)
	m = len(E)
	if ids :
		E_ids = E
	else :
		V_id = {V[i] : i for i in range(n)}
		E_ids = [(V_id[v], V_id[u]) for (u, v) in E]
	if sparse :
		if value == 'symbol' : # SymPy symbol
			return SparseMatrix(n, n, {E_ids[k] : symbols('e' + str(k)) for k in range(m)})
		elif value == 'sympy' : # SymPy real
			return SparseMatrix(n, n, {E_ids[k] : Float(random()) for k in range(m)})
		elif value == 'python' : # Python real
			return SparseMatrix(n, n, {E_ids[k] : random() for k in range(m)})
	else : # dense
		if value == 'symbol' : # SymPy symbol
			if init_first : # initialize the matrix with zeroes first
				A = zeros(n, n)
				for k in range(m) :
					i, j = E_ids[k]
					A[j, i] = symbols('e' + str(k))
				return A
			else : # use lambda to generate each value directly
				sym = {}
				for k in range(m) :
					sym[E_ids[k]] = symbols('e' + str(k))
				E_ids = set(E_ids)
				return Matrix(n, n, lambda i, j : sym[(j, i)] if (j, i) in E_ids else 0)
		elif value == 'sympy' : # SymPy real
			if init_first : # initialize the matrix with zeroes first
				A = zeros(n, n)
				for (i, j) in E_ids :
					A[j, i] = Float(random())
				return A
			else : # use lambda to generate each value directly
				E_ids = set(E_ids) # speeds up membership test
				return Matrix(n, n, lambda i, j : Float(random()) if (j, i) in E_ids else 0)
		elif value == 'python' : # Python real
			if init_first : # initialize the matrix with zeroes first
				A = zeros(n, n)
				for (i, j) in E_ids :
					A[j, i] = random()
				return A
			else : # use lambda to generate each value directly
				E_ids = set(E_ids) # speeds up membership test
				return Matrix(n, n, lambda i, j : random() if (j, i) in E_ids else 0)
#
# profile this to test the speed of various parameter combinations
# conclusions from profiling
# - dense matrices take more time to be generated
# - initializing with zero and then adding the nonzero values is faster
# - Python reals faster for sparse matrices, but slower for dense ones?
#@profile
def profile_get_A() :
	for i in range(20) :
		V, E = random_graph_ER(n = 100, m = 200)
		# sparse
		As1  = get_A(V, E, value = 'symbol', sparse = True)
		As2  = get_A(V, E, value = 'sympy',  sparse = True)
		As3  = get_A(V, E, value = 'python', sparse = True)
		# dense symbolic
		Ad1  = get_A(V, E, value = 'symbol', sparse = False, init_first = True)
		Ad1b = get_A(V, E, value = 'symbol', sparse = False, init_first = False)
		# dense SymPy float
		Ad2  = get_A(V, E, value = 'sympy',  sparse = False, init_first = True)
		Ad2b = get_A(V, E, value = 'sympy',  sparse = False, init_first = False)
		# dense Python float
		Ad3  = get_A(V, E, value = 'python', sparse = False, init_first = True)
		Ad3b = get_A(V, E, value = 'python', sparse = False, init_first = False)
#profile_get_A()
#
# profile this to test the speed of computing the rank for different kinds of matrices
# conclusions from profiling:
# - simplify = True only matters (as computation time) for symbolic matrices
#   * probably only makes sense for those, maybe for rationals too
# - numeric rank is computed faster than symbolic one
# - seems that rank computation is slower for sparse matrices (reasonable)
#@profile
def profile_rank_A() :
	for i in range(25) :
		V, E = random_graph_ER(n = 10, m = 20)
		# compute matrices
		As1 = get_A(V, E, value = 'symbol', sparse = True)
		As2 = get_A(V, E, value = 'sympy',  sparse = True)
		As3 = get_A(V, E, value = 'python', sparse = True)
		Ad1 = get_A(V, E, value = 'symbol', sparse = False)
		Ad2 = get_A(V, E, value = 'sympy',  sparse = False)
		Ad3 = get_A(V, E, value = 'python', sparse = False)
		# compute ranks
		ks1 = As1.rank()
		ks1b = As1.rank(simplify = True)
		ks2 = As2.rank()
		ks2b = As2.rank(simplify = True)
		ks3 = As3.rank(iszerofunc = lambda x : abs(x) < 1e-10)
		ks3b = As3.rank(iszerofunc = lambda x : abs(x) < 1e-10, simplify = True)
		kd1 = Ad1.rank()
		kd1b = Ad1.rank(simplify = True)
		kd2 = Ad2.rank()
		kd2b = Ad2.rank(simplify = True)
		kd3 = Ad3.rank(iszerofunc = lambda x : abs(x) < 1e-10)
		kd3b = Ad3.rank(iszerofunc = lambda x : abs(x) < 1e-10, simplify = True)
		# print statistics
		print ks1, ks1b, ' ', ks2, ks2b, ' ', ks3, ks3b, ' | ', kd1, kd1b, ' ', kd2, kd2b, ' ', kd3, kd3b
#profile_rank_A()

# generate the B matrix for a set of driven nodes
# - V = vertices of the graph
# - driven = set of driven nodes
# - ids = True if vertices are already indices: V = range(|V|)
# - value = type of values to put in the matrix:
#   - 'symbol' = symbolic values
#   - 'sympy' = SymPy reals
#   - 'python' = Python reals
# - sparse = True if the generated matrix is sparse
def get_B(V, driven, ids = False, value = 'python', sparse = True) :
	n = len(V)
	d = len(driven)
	if ids :
		driven_ids = driven
	else :
		V_id = {V[i] : i for i in range(n)}
		driven_ids = [V_id[v] for v in driven]
	if sparse :
		if value == 'symbol' : # SymPy symbol
			return SparseMatrix(n, d, {(driven_ids[k], k) : symbols('d' + str(k)) for k in range(d)})
		elif value == 'sympy' : # SymPy real
			return SparseMatrix(n, d, {(driven_ids[k], k) : Float(random()) for k in range(d)})
		elif value == 'python' : # Python real
			return SparseMatrix(n, d, {(driven_ids[k], k) : random() for k in range(d)})
	else : # dense value
		if value == 'symbol' : # SymPy symbol
			B = zeros(n, d)
			for k in range(d) :
				B[driven_ids[k], k] = symbols('d' + str(k))
			return B
		elif value == 'sympy' : # SymPy real
			B = zeros(n, d)
			for k in range(d) :
				B[driven_ids[k], k] = Float(random())
			return B
		elif value == 'python' : # Python real
			B = zeros(n, d)
			for k in range(d) :
				B[driven_ids[k], k] = random()
			return B
#
def test_get_B() :
	V, E = random_graph_ER(n = 10, m = 20)
	pprint(get_B(V, V))

# compute controllability matrix
# - V, E = graph vertices and edges
# - driven = set of driven nodes
# - targets = set of target nodes
# - ids = True if vertices are already indices: V = range(|V|)
# - value = type of values to put in the matrix:
#   - 'symbol' = symbolic values
#   - 'sympy' = SymPy reals
#   - 'python' = Python reals
# - sparse = True if the generated matrix is sparse
# - join = True if C is computed by repeated join operations
# - min_memory = True if C only contains one line for each target
#@profile
def get_controllability(V, E, driven, targets, ids = False, value = 'python', sparse = True, join = False, min_memory = True) :
	n = len(V)
	m = len(E)
	d = len(driven)
	t = len(targets)
	if ids :
		E_ids = E
		driven_ids = driven
		target_ids = targets
	else :
		V_id = {V[i] : i for i in range(n)}
		E_ids = [(V_id[v], V_id[u]) for (u, v) in E]
		driven_ids = [V_id[v] for v in driven]
		target_ids = [V_id[v] for v in targets]
	A = get_A(V, E_ids, ids = True, value = value, sparse = sparse)
	B = get_B(V, driven_ids, ids = True, value = value, sparse = sparse)
	if min_memory : # don't allocate more than t lines for the controllability matrix
		if join : # don't allocate full C, join fragments as they are computed
			AiB = B.copy()
			C = AiB.extract(target_ids, range(d))
			for i in range(1, n) :
				AiB = A * AiB
				C = C.row_join(AiB.extract(target_ids, range(d)))
			return C
		else : # initialize first, no join needed
			if sparse :
				C = SparseMatrix(t, d * n, {}) 
			else :
				C = zeros(t, d * n)
			AiB = B.copy()
			C[:, 0 : d] = AiB.extract(target_ids, range(d))
			for i in range(1, n) :
				AiB = A * AiB
				C[:, d * i : d * (i + 1)] = AiB.extract(target_ids, range(d))
			return C
	else : # allocate full C, extract relevant lines at the end
		if join : # don't allocate full C, join fragments as they are computed
			AiB = B.copy()
			C = AiB.copy()
			for i in range(1, n) :
				AiB = A * AiB
				C = C.row_join(AiB)
			return C
		else : # initialize first, no join needed
			if sparse :
				C = SparseMatrix(n, d * n, {}) 
			else :
				C = zeros(n, d * n)
			AiB = B.copy()
			C[:, 0 : d] = AiB
			for i in range(1, n) :
				AiB = A * AiB
				C[:, d * i : d * (i + 1)] = AiB
			return C.extract(target_ids, range(d * n))
#
# conclusion of profiling the method for computing the controllability matrix
# - better to not allocate the full C if only few targets
#   * difference more significant for numeric matrices
# - better to use sparse matrices rather than dense ones
# - join does not seem to bring such a significant overhead
#@profile
def profile_get_controllability_method(value = 'symbol', sparse = True) :
	from random import sample
	for i in range(5) :
		V, E = random_graph_ER(n = 25, m = 50)
		driven = sample(V, 5)
		targets = sample(V, 5)
		C1 = get_controllability(V, E, driven, targets, value = value, sparse = sparse, join = False, min_memory = True)
		C2 = get_controllability(V, E, driven, targets, value = value, sparse = sparse, join = False, min_memory = False)
		C3 = get_controllability(V, E, driven, targets, value = value, sparse = sparse, join = True, min_memory = True)
		C4 = get_controllability(V, E, driven, targets, value = value, sparse = sparse, join = True, min_memory = False)
#profile_get_controllability_method(value = 'symbol', sparse = False)
#
# conclusions from profiling
# - rank seems to be the same regardless of simplification or using numbers
#   * note that the test graphs are small though
# - rank computation is significantly slower for symbolic matrices
# - simplification makes symbolic rank computation faster (double check this)
# - no difference between rref and rank for numeric matrices
# - rref is faster for symbolic matrices than computing the rank (why is that?)
#@profile
def profile_rank_C() :
	from random import sample
	for i in range(25) :
		V, E = random_graph_ER(n = 15, m = 30)
		driven = sample(V, 5)
		targets = sample(V, 5)
		# compute matrices
		C1 = get_controllability(V, E, driven, targets, value = 'symbol')
		C2 = get_controllability(V, E, driven, targets, value = 'sympy')
		C3 = get_controllability(V, E, driven, targets, value = 'python')
		# SymPy symbols
		k1a = C1.rank()
		k1b = C1.rank(simplify = True)
		k1c = len(C1.rref()[1])
		k1d = len(C1.rref(simplify = True)[1])
		# SymPy real
		k2a = C2.rank()
		k2b = C2.rank(simplify = True)
		k2c = len(C2.rref()[1])
		k2d = len(C2.rref(simplify = True)[1])
		# Python real
		k3a = C3.rank(iszerofunc = lambda x : abs(x) < 1e-10)
		k3b = C3.rank(iszerofunc = lambda x : abs(x) < 1e-10, simplify = True)
		k3c = len(C3.rref(iszerofunc = lambda x : abs(x) < 1e-10)[1])
		k3d = len(C3.rref(iszerofunc = lambda x : abs(x) < 1e-10, simplify = True)[1])
		# print statistics
		print k1a, k1b, k1c, k1d, ' ', k2a, k2b, k2c, k2d, ' ', k3a, k3b, k3c, k3d
#profile_rank_C()
#
# conclusions from profiling
# - working with numeric matrices is significantly faster
# - rank computation does not distinguish Sympy reals from Python reals
#   * as far as time is concerned
#   * results seem to be the same, but matrix size is small in this test
# - Python reals work better for computing the controllability matrix, for some reason
#@profile
def test_generic_rank() :
	from random import sample
	for i in range(5) :
		V, E = random_graph_ER(n = 25, m = 50)
		driven = sample(V, 10)
		targets = sample(V, 10)
		# compute matrices
		C1 = get_controllability(V, E, driven, targets, value = 'symbol')
		C2 = get_controllability(V, E, driven, targets, value = 'sympy')
		C3 = get_controllability(V, E, driven, targets, value = 'python')
		# compute ranks
		k1 = len(C1.rref(simplify = True)[1])
		k2 = len(C2.rref()[1])
		k3 = len(C3.rref()[1])
		# statistics
		print k1, k2, k3
#test_generic_rank()
#
#@profile
def test_generic_rank_numeric() :
	from random import sample
	for i in range(5) :
		V, E = random_graph_ER(n = 100, m = 200)
		driven = sample(V, 25)
		targets = sample(V, 25)
		# compute matrices
		Ca = get_controllability(V, E, driven, targets, value = 'sympy')
		Cb = get_controllability(V, E, driven, targets, value = 'python')
		# compute ranks
		ka = len(Ca.rref()[1])
		kb = len(Cb.rref()[1])
		# statistics
		print ka, kb
#test_generic_rank_numeric()



# computes the rank of the controllability matrix taking advantage of previous observations
# - uses Python floats for the matrices
# - computes parts of C at a time, finds the rank then appends to linearly independent part
# - use of join here should not slow down the method
#@profile
def is_controllable(V, E, driven, targets) :
	n = len(V)
	m = len(E)
	d = len(driven)
	t = len(targets)
	V_id = {V[i] : i for i in range(n)}
	E_ids = [(V_id[v], V_id[u]) for (u, v) in E]
	driven_ids = [V_id[v] for v in driven]
	target_ids = [V_id[v] for v in targets]
	# compute matrices
	A = get_A(V, E_ids, ids = True)
	B = get_B(V, driven_ids, ids = True)
	# compute the rank of the controllability matrix
	zerotest = lambda x : abs(x) < 1e-10
	print 'Computing rank (n = ' + str(n) + ') ........ ' +  ('[0/' + repr(t) + '] 0').ljust(SIZE),
	AiB = B.copy()
	C = AiB.extract(target_ids, range(d))
	indeps = C.rref(iszerofunc = zerotest)[1]
	C = C.extract(range(t), indeps)
	for i in range(1, n) :
		print '\b' * (SIZE + 1) + ('[' + repr(len(indeps)) + '/' + repr(t) + '] ' + repr(i)).ljust(SIZE),
		AiB = A * AiB
		C = C.row_join(AiB.extract(target_ids, range(d)))
		indeps = C.rref(iszerofunc = zerotest)[1]
		C = C.extract(range(t), indeps)
		if len(indeps) == t :
			print '\b' * (SIZE + 1) + ('[' + repr(len(indeps)) + '/' + repr(t) + '] ' + repr(i)).ljust(SIZE),
			return True
	return False



SIZE = 20

# computes solutions for minimum driven set, via matrices
#@profile
def min_driven_set(V, E, targets) :
	# computes score based on:
	# - d = number of driven nodes in old set
	# - k1 = rank corresponding to old driven set
	# - k2 = rank corresponding to the newly added driven node
	def get_score(dd, k1, k2) :
		return (k1 ** 2 + k2 ** 2) / dd ** 0.5
	n = len(V)         # number of nodes
	t = len(targets)   # number of targets

	print 'Generating A and B .......',
	# compute matrices A and B
	V_id = {V[i] : i for i in range(n)}
	E_ids = [(V_id[v], V_id[u]) for (u, v) in E]
	### numeric version, test for speed
	A = SparseMatrix(n, n, {E_ids[k] : random() for k in range(len(E_ids))})
	B = SparseMatrix(n, n, {(i, i) : random() for i in range(n)})
	### sparse matrix version
	#A = SparseMatrix(n, n, {E_ids[k] : symbols('e' + str(k)) for k in range(len(E_ids))})
	#B = SparseMatrix(n, n, {(i, i) : symbols('d' + str(i)) for i in range(n)})
	### sparse matrix + numeric
	#B = SparseMatrix(n, n, {(i, i) : S(1) / prime(i + 1) for i in range(n)})
	#A = SparseMatrix(n, n, {E_ids[k] : S(1) / prime(k + n + 1) for k in range(len(E_ids))})
	### dense matrix -- very slow
	#A = zeros(n, n)
	#for k in range(len(E_ids)) :
	#	i, j = E_ids[k]
	#	A[i, j] = symbols('e' + str(k))
	#B = zeros(n, n)
	#for i in range(n) :
	#	B[i, i] = symbols('d' + str(i))
	print '[ok]'

	# computes TC for A and full B
	print 'Computing full TC ........ ' +  ' '.ljust(SIZE),
	target_ids = [i for i in range(n) if V[i] in targets]
	TCfull = SparseMatrix(t, n * n, {})
	### compute for full B -- very slow for large matrices
	AiB = B.copy()
	TCfull[:, 0 : n] = AiB.extract(target_ids, range(n))
	for i in range(1, n) :
		print '\b' * (SIZE + 1) + repr(i).ljust(SIZE),
		AiB = A * AiB
		TCfull[:, n * i : n * (i + 1)] = AiB.extract(target_ids, range(n))
	print '\b' * (SIZE + 1) + '[ok]'
	### compute for one column of B at a time -- compare with above
	#Zero = zeros(n, 1)
	#for j in range(n) :
	#	AiBj = B[:, j]
	#	TCfull[:, j] = AiBj.extract(target_ids, range(1))
	#	for i in range(1, n) :
	#		print '\b' * (SIZE + 1) + (repr(j) + ': ' + repr(i)).ljust(SIZE),
	#		AiBj = A * AiBj
	#		if AiBj == Zero :
	#			break
	#		TCfull[:, n * i + j] = AiBj.extract(target_ids, range(1))
	#print '\b' * (SIZE + 1) + '[ok]'

	# computes column indices for a basis for TC corresponding to
	# each column of B
	bases_Bi = []
	print 'Rank of TC for B[:, i] ... ' + ' '.ljust(SIZE),
	for i in range(n) :
		print '\b' * (SIZE + 1) + repr(i).ljust(SIZE),
		Ci = TCfull.extract(range(t), [n * j + i for j in range(n)])
		_, basis = Ci.rref()
		if len(basis) == t :
			yield [V[i]]
			return
		bases_Bi.append([n * k + i for k in basis])
	nonempty_ids = [i for i in range(n) if bases_Bi[i]]
	print '\b' * (SIZE + 1) + '[ok]'

	d = t + 1
	candidates = [(get_score(1, len(bases_Bi[i]), len(bases_Bi[j])), 
					[i, j], 
					bases_Bi[i] + bases_Bi[j])
					for i in nonempty_ids for j in nonempty_ids if i != j]
	count = 0
	print ' '.ljust(SIZE),
	while candidates :
		candidates.sort()
		score, driven_set, bases_union = candidates.pop()
		if len(driven_set) >= d :
			print '\b' * (SIZE + 1) + (repr(count) + '/' + repr(len(candidates))).ljust(SIZE),
			continue
		count += 1
		print '\b' * (SIZE + 1) + (repr(count) + '/' + repr(len(candidates))).ljust(SIZE),
		TC = TCfull.extract(range(t), bases_union)
		_, basis = TC.rref()
		rank = len(basis)
		if rank == t :
			d = len(driven_set) # implicitly len(driven_set) < d from above
			print
			yield [V[i] for i in driven_set]
			continue
		for new in nonempty_ids :
			if new not in driven_set :
				candidates.append((
						get_score(len(driven_set), rank, len(bases_Bi[new])), 
						driven_set + [new], 
						[bases_union[b] for b in basis] + bases_Bi[new]))



#=======
# package tests
#==============

if __name__ == '__main__' :
	# graph vertices
	V = ['d', 'c', 'j', 'l', 'i', 'v', 'h', 'g']
	# graph edges
	E = [('d', 'c'), ('d', 'j'), ('j', 'l'), ('c', 'v'), ('c', 'i'), ('i', 'g'), ('v', 'h')]
	# target set
	targets = ['v', 'g', 'h', 'l']
	# driven set
	driven = ['d', 'v']
	# compute minimum driven set
	for solution in min_driven_set(V, E, targets) :
		print(solution)
	print 'done'
