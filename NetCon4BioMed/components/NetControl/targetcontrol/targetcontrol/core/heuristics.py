from __future__ import division

from aux.utils import sublists
from pyparsing import Word, Forward, Literal, Group, ZeroOrMore, Empty, ParseResults



'''
In the representation of heuristics, we use one characters to encode 
various sets of edges that can be considered when running the maximum 
matching algorithm. Say 'a' and 'b' encode two kinds of edges. Then 
there are several ways in which we can combine 'a' and 'b' into a single
matching:
* '(->ab)' = run a maximum matching using 'a' and 'b' edges together
* '(->a)(->b)' = run a maximum matching that only consideres 'a' edges, 
then a maximum matching of the uncovered nodes with the 'b' edges (this 
gives a _maximal_ matching)
* '((->a)->b)' = run a maximum matching that only considers 'a' edges; 
use this matching as initialization to compute a maximum matching that 
considers both 'a' and 'b' edges

Heuristics language:
* types of edges:
  - edges of an elementary type: a string of letters, e.g. 'a'
  - edges of type 'a' or 'b' (union): 'a.b'
* a single maximum matching with edges of type 't': '(->t)'
* concatenation of heuristics 'p' and 'q' = run 'p', then remove the 
matched nodes and run 'q', then return the union of the matched nodes 
(maximal matching): 'pq'
* most general form - run heuristics 'p', then 'q' (concatenation), then
use the result as initialization to get a maximum matching that 
additionally uses edges of type 'a' or 'b': '(pq->a.b)'
   
The language presented above can be described by the following grammar:
	<type> = <elementary> <type> | ''
	<heuristics> ::= <step> <heuristics> | ''
	<step> ::= '(' heuristics '->' <type> ')'

'''



#=======
# heuristics constructors
#========================

# types are represented as lists of strings
# steps are represented as pairs
# heuristics are represented as lists of steps

# use + for concatenating types
# use + for concatenating heuristics

# general constructor for heuristics
def H(steps, types) :
	assert steps != [] or types != []
	return [(steps, types)]

# constructor for a single maximum matching
# assumes 'types' is not empty
def Hi(types) :
	assert types != []
	return H([], types)

# constructor to turn (possibly maximal) heuristics into maximum one
# assumes 'steps' is not empty
def Hc(steps) :
	assert steps != []
	return H(steps, [])



#=======
# convert heuristics to string and back
#======================================

# generates a string that represents the corresponding heuristics using
# the language described above
def hstr(heuristics) :
	def hstr_list(heurs) :
		ret = ''
		for (steps, types) in heurs :
			ret += hstr_step(steps, types)
		return ret
	def hstr_step(steps, types) :
		ret = '(' + hstr_list(steps) + '->'
		if types != [] :
			ret += types[0]
			for t in types[1 :] :
				ret += '.' + t
		ret += ')'
		return ret
	return hstr_list(heuristics)

# get heuristics from its string representation
def get_heuristics(s) :
	etype = Word('\@#TNDCPOLAKX')
	sep = Literal('.').suppress()
	ctype = Group(etype + ZeroOrMore(sep + etype) | Empty())
	heur = Forward()
	lparen = Literal('(').suppress()
	rparen = Literal(')').suppress()
	arrow = Literal('->').suppress()
	step = (lparen + heur.setResultsName('h') + arrow + ctype.setResultsName('t') + rparen).addParseAction(lambda toks : (toks.h.asList(), toks.t.asList()))
	heur << Group(ZeroOrMore(step))
	return heur.parseString(s)[0]



#=======
# generate lists of heuristics
#=============================

# generate heuristics for two types, assumes ordering A <= B
# for A < B take the slice [1 :]
def h_AB(A, B) :
	if not A :
		yield Hi(B) # (->B)
	elif not B :
		yield Hi(A) # (->A)
	else :
		yield Hi(A + B)         # (->A.B)
		yield H(Hi(A), B)       # ((->A)->B)
		yield Hc(Hi(A) + Hi(B)) # ((->A)(->B)->)
		yield Hi(A) + Hi(B)     # (->A)(->B)

# generate heuristics for one type and one heuristics
def h_aB(a, B) :
	yield H(a, B)       # a->B
	yield Hc(a + Hi(B)) # (a(->B)->)
	yield a + Hi(B)     # a(->B)
#
def h_Ab(A, b) :
	yield Hc(Hi(A) + b) # ((->A)b->)
	yield Hi(A) + b     # (->A)b

# generate heuristics for three types, assumes A <= B <= C
def h_ABC(A, B, C) :
	if not A :
		yield h_AB(B, C)
	elif not B :
		yield h_AB(A, C)
	elif not C :
		yield h_AB(B, C)
	else :
		yield Hi(A + B + C)                 # (->A.B.C)
		yield H(Hi(A + B), C)               # ((->A.B)->C)
		yield H(H(Hi(A), B), C)             # (((->A)->B)->C)
		yield H(Hc(Hi(A) + Hi(B)), C)       # (((->A)(->B)->)->C)
		yield H(Hi(A) + Hi(B), C)           # ((->A)(->B)->C)
		yield H(Hi(A), B + C)               # ((->A)->B.C)
		yield Hc(Hi(A) + Hi(B + C))         # ((->A)(->B.C)->)
		yield Hc(Hi(A) + H(Hi(B), C))       # ((->A)((->B)->C)->)
		yield Hc(Hi(A) + Hc(Hi(B) + Hi(C))) # ((->A)((->B)(->C)->)->)
		yield Hc(Hi(A + B) + Hi(C))         # ((->A.B)(->C)->)
		yield Hc(H(Hi(A), B) + Hi(C))       # (((->A)->B)(->C)->)
		yield Hc(Hc(Hi(A) + Hi(B)) + Hi(C)) # (((->A)(->B)->)(->C)->)
		yield Hc(Hi(A) + Hi(B) + Hi(C))     # ((->A)(->B)(->C)->)
		yield Hi(A) + Hi(B + C)             # (->A)(->B.C)
		yield Hi(A) + H(Hi(B), C)           # (->A)((->B)->C)
		yield Hi(A) + Hc(Hi(B) + Hi(C))     # (->A)((->B)(->C)->)
		yield Hi(A + B) + Hi(C)             # (->A.B)(->C)
		yield H(Hi(A), B) + Hi(C)           # ((->A)->B)(->C)
		yield Hc(Hi(A) + Hi(B)) + Hi(C)     # ((->A)(->B)->)(->C)
		yield Hi(A) + Hi(B) + Hi(C)         # (->A)(->B)(->C)

# generate two-matchings heuristics for a set of elementary types
# order_only == True : only generate (->A)(->B) for each split A, B
def g_X(X, order_only = False) :
	yield Hi(X)
	for A in sublists(X)[1:-1] :
		B = [b for b in X if b not in A]
		if order_only :
			yield Hi(A) + Hi(B)
		else :
			for x in list(h_AB(A, B))[1:] :
				yield x

# generate three-matchings heuristics for two sets of elementary types
# the third split will be in X or Y, assumes X <= Y is preserved
def g_XY(X, Y, order_only = False) :
	if order_only :
		yield Hi(X) + Hi(Y)
	else :
		for xy in h_AB(X, Y) :
			yield xy
	for A in sublists(X)[1 : -1] :
		B = [b for b in X if b not in A]
		if order_only :
			yield Hi(A) + Hi(B) + Hi(Y)
		else :
			for xy in list(h_ABC(A, B, Y))[1:] :
				yield xy
	for B in sublists(Y)[1 : -1] :
		C = [c for c in Y if c not in B]
		if order_only :
			yield Hi(X) + Hi(B) + Hi(C)
		else :
			for xy in list(h_ABC(X, B, C))[1:] :
				yield xy	



#=======
# package tests
#==============

if __name__ == '__main__' :
	print '# simple examples'
	print hstr(Hi(['A']))
	print hstr(Hc(Hi(['A'])))
	print hstr(H(Hi(['A']), ['B', 'C']))
	print
	print '# heuristics from string'
	h = H(Hi(['A']), ['C', '@L'])
	print h
	print hstr(h)
	print get_heuristics(hstr(h))
	exit(0)
	print
	print '# two-matchings heuristics'
	print ', '.join(hstr(h) for h in h_aB(Hi(['A']), ['B'])), '==', ', '.join(hstr(h) for h in list(h_AB(['A'], ['B']))[1 :])
	print ', '.join(hstr(h) for h in h_Ab(['A'], Hi(['B']))), '==', ', '.join(hstr(h) for h in list(h_AB(['A'], ['B']))[2 :])
	print
	print '# heuristics for two types'
	for h in h_AB(['A', 'B'], ['C', 'D']) :
		print hstr(h)
	print
	print '# heuristics for three types'
	for h in h_ABC(['A'], ['B'], ['C']) :
		print hstr(h)
	print
	print '# two-matchings heuristics for A, B -- all'
	for h in g_X(['A', 'B']) :
		print hstr(h)
	print
	print '# two-matchings heuristics for A, B, C -- order only'
	for h in g_X(['A', 'B', 'C'], order_only = True) :
		print hstr(h)
	print
	print '# three-matchings heuristics for [A, B], [X, Y] -- all'
	for h in g_XY(['A', 'B'], ['X', 'Y']) :
		print hstr(h)
	print
	print '# three-matchings heuristics for [A, B], [X, Y] -- order only'
	for h in g_XY(['A', 'B'], ['X', 'Y'], order_only = True) :
		print hstr(h)
