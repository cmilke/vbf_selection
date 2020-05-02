from functools import partial
from uproot_methods import TLorentzVector
import itertools
import random


###########
# Utility #
###########

make_pairs = lambda vectors: [ (vec_i, vec_j) for vec_i, vec_j in itertools.combinations(vectors, 2) ]


###########
# Filters #
###########

delta_eta_cut = lambda d_eta_cut, pairs: [ pair for pair in pairs if abs(pair[0].eta - pair[1].eta) > d_eta_cut ]
all_pairs = lambda pairs: pairs


#############
# Selectors #
#############

def feature_rank(rank, pairs, key):
    pair_ranking = sorted(pairs, key=key, reverse=True)
    if rank > len(pair_ranking)-1: return pair_ranking[-1]
    else: return pair_ranking[rank]

mjj_rank = lambda rank, pairs: feature_rank(rank, pairs, lambda pair: (pair[0]+pair[1]).mass)
random_jets = lambda pairs: random.sample(pairs, 1)


##################
# Discriminators #
##################

# Pair Taggers
mjj = lambda pair: (pair[0] + pair[1]).mass

def pair_tagger( filter_func, selector, discriminator, vectors ):
    viable_pairs = filter_func( make_pairs(vectors) )
    if len(viable_pairs) == 0:
        return -1
    else:
        return discriminator( selector(viable_pairs) )

# General Taggers
def total_invariant_mass(vectors):
    total_vector = TLorentzVector(0,0,0,0)
    for vec in vectors: total_vector += vec
    return total_vector.mass




Tagger_options = {
	'mjN': total_invariant_mass,
	'mjjmax': partial( pair_tagger, all_pairs, partial(mjj_rank,0), mjj ),
    'mjjSL': partial( pair_tagger, all_pairs, partial(mjj_rank,1), mjj ),
    'Deta3_mjjmax': partial( pair_tagger, partial(delta_eta_cut,3) , partial(mjj_rank,0), mjj )
}
