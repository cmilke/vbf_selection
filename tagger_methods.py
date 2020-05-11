from functools import partial
from uproot_methods import TLorentzVector
import itertools
import random


###########
# Utility #
###########

make_pairs = lambda vectors: [ (vec_i, vec_j) for vec_i, vec_j in itertools.combinations(vectors, 2) ]
mjj = lambda pair: (pair[0] + pair[1]).mass


###########
# Filters #
###########

delta_eta_filter = lambda d_eta_cut, pairs: [ pair for pair in pairs if abs(pair[0].eta - pair[1].eta) > d_eta_cut ]
all_pairs = lambda pairs: pairs


##################
# Discriminators #
##################

def leading_invariant_mass( num_candidates, vectors):
    return max( [ mjj(pair) for pair in make_pairs(vectors) ] )

def minimum_invariant_mass( num_candidates, vectors):
    return min( [ mjj(pair) for pair in make_pairs(vectors) ] )

def subleading_invariant_mass( num_candidates, vectors):
    mjjs = [ mjj(pair) for pair in make_pairs(vectors) ]
    mjjs.sort(reverse=True)
    return mjjs[1] if num_candidates > 2 else mjjs[0]

def delta_eta_cut_mjj_tagger( d_eta_cut, num_candidates, vectors ):
    viable_pairs = delta_eta_filter( d_eta_cut, make_pairs(vectors) )
    if len(viable_pairs) == 0: return 9999
    else: return max( [ mjj(pair) for pair in viable_pairs ] )

def total_invariant_mass(num_candidates, vectors):
    total_vector = TLorentzVector(0,0,0,0)
    for vec in vectors: total_vector += vec
    return total_vector.mass

def smart_total_invariant_mass(num_candidates, vectors):
    mjNs = []
    for num_jets in range(2,num_candidates+1):
        for vec_collecton in itertools.combinations(vectors, num_jets):
            total_vector = TLorentzVector(0,0,0,0)
            for vec in vec_collecton: total_vector += vec
            mjNs.append(total_vector.mass)
    return max(mjNs)



Tagger_options = {
	'mjjmax': leading_invariant_mass,
	'mjjmin': minimum_invariant_mass,
    'mjjSL': subleading_invariant_mass,
	'mjN': total_invariant_mass,
	'imjN': smart_total_invariant_mass,
    'Deta3_mjjmax': partial(delta_eta_cut_mjj_tagger, 3)
}
