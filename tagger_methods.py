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

mjj_rank = lambda rank, pairs: sorted(pairs, key=lambda pair: (pair[0]+pair[1]).mass, reverse=True)[rank]
delta_eta_rank = lambda rank, pairs: sorted(pairs, key=lambda pair: abs(pair[0].eta-pair[1].eta), reverse=True)[rank]
random_jets = lambda pairs: random.sample(pairs, 1)


##################
# Discriminators #
##################

# Pair Taggers
mjj = lambda pair: (pair[0] + pair[1]).mass

def std_tagger( filter_func, selector, discriminator, vectors ):
    viable_pairs = filter_func( make_pairs(vectors) )
    if len(viable_pairs) == 0:
        return -999
    else:
        return discriminator( selector(viable_pairs) )


# General Taggers
def total_invariant_mass(vectors):
    total_vector = TLorentzVector(0,0,0,0)
    for vec in vectors: total_vector += vec
    return total_vector.mass


#Tagger_options = {
#	'mjN': total_invariant_mass, #TODO
#	'mjj_from_leading_pt': partial(stdTag, leading_pt_jets, mjj), #TODO
#	'mjjmax': partial( stdTag, partial(mjj_rank,0), mjj),
#    'Deta_mjjmax': 
#	'mjjSL': partial( stdTag, partial(mjj_rank,1), mjj), #TODO
#	'mjj_of_random_jets': partial( stdTag, random_jets, mjj) #TODO
#}


Tagger_options = {
	'mjN': total_invariant_mass,
	'mjjmax': partial( std_tagger, all_pairs, partial(mjj_rank,0), mjj ),
    'Deta3_mjjmax': partial( std_tagger, partial(delta_eta_cut,3) , partial(mjj_rank,0), mjj )
}
