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


#############
# Selectors #
#############

def feature_rank(rank, pairs, key):
    pair_ranking = sorted(pairs, key=key, reverse=True)
    if rank > len(pair_ranking)-1: return pair_ranking[-1]
    else: return pair_ranking[rank]

mjj_rank = lambda rank, pairs: feature_rank(rank, pairs, mjj)
random_jets = lambda pairs: random.sample(pairs, 1)


##################
# Discriminators #
##################

mjj_tagger = lambda rank, vectors: mjj( mjj_rank(rank,make_pairs(vectors)) )

def delta_eta_cut_mjj_tagger( d_eta_cut, vectors ):
    viable_pairs = delta_eta_filter( d_eta_cut, make_pairs(vectors) )
    if len(viable_pairs) == 0:
        return 9999
    else:
        return mjj( mjj_rank(0,viable_pairs) )

def total_invariant_mass(vectors):
    total_vector = TLorentzVector(0,0,0,0)
    for vec in vectors: total_vector += vec
    return total_vector.mass




Tagger_options = {
	'mjN': total_invariant_mass,
	'mjjmax': partial(mjj_tagger, 0),
    'mjjSL': partial(mjj_tagger, 1),
    'Deta3_mjjmax': partial(delta_eta_cut_mjj_tagger, 3)
}
