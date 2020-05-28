from functools import partial
from uproot_methods import TLorentzVector
import itertools
import random
import pickle


###########
# Utility #
###########

make_pairs = lambda vectors: [ (vec_i, vec_j) for vec_i, vec_j in itertools.combinations(vectors, 2) ]
mjj = lambda pair: (pair[0] + pair[1]).mass
d_eta = lambda pair: abs(pair[0].eta - pair[1].eta)


###########
# Filters #
###########

delta_eta_filter = lambda d_eta_cut, pairs: [ pair for pair in pairs if d_eta(pair) > d_eta_cut ]
all_pairs = lambda pairs: pairs


##################
# Discriminators #
##################

def leading_invariant_mass( vectors ):
    return max( [ mjj(pair) for pair in make_pairs(vectors) ] )

def minimum_invariant_mass( vectors ):
    return min( [ mjj(pair) for pair in make_pairs(vectors) ] )

def subleading_invariant_mass( vectors ):
    mjjs = [ mjj(pair) for pair in make_pairs(vectors) ]
    mjjs.sort(reverse=True)
    return mjjs[1] if len(mjjs) > 1 else mjjs[0]

# Find all pairs that exceed delta eta > 3,
# then return the leading mjj of those remaining
def delta_eta_cut_mjj_tagger( d_eta_cut, vectors ):
    viable_pairs = delta_eta_filter( d_eta_cut, make_pairs(vectors) )
    if len(viable_pairs) == 0: return -1
    else: return max( [ mjj(pair) for pair in viable_pairs ] )

# Above function in reverse order: Choose (only!) the highest mjj pair,
# and if the pair's d-eta < 3, throw it away
def mjj_delta_eta_cut_tagger( d_eta_cut, vectors ):
    max_mjj_pair = max( [ (mjj(pair), d_eta(pair)) for pair in make_pairs(vectors) ] )
    if max_mjj_pair[1] < d_eta_cut: return -1
    else: return max_mjj_pair[0]

def total_invariant_mass(vectors):
    total_vector = TLorentzVector(0,0,0,0)
    for vec in vectors: total_vector += vec
    return total_vector.mass

def smart_total_invariant_mass(vectors):
    num_candidates = len(vectors)
    mjNs = []
    for num_jets in range(2,num_candidates+1):
        for vec_collecton in itertools.combinations(vectors, num_jets):
            total_vector = TLorentzVector(0,0,0,0)
            for vec in vec_collecton: total_vector += vec
            mjNs.append(total_vector.mass)
    return max(mjNs)


def load_from_bdt_dump(bdt_dump, key, event_index):
    return bdt_dump[key][event_index]



Tagger_options = {
	'mjjmax': leading_invariant_mass,
	'mjjmin': minimum_invariant_mass,
    'mjjSL': subleading_invariant_mass,
	'mjN': total_invariant_mass,
	'imjN': smart_total_invariant_mass,
    'Deta3_mjjmax': partial(delta_eta_cut_mjj_tagger, 3),
    'mjjmax_Deta3': partial(mjj_delta_eta_cut_tagger, 3),
    'BDT: mjjmax-Deta': partial(load_from_bdt_dump, pickle.load(open('prediction_dump_mjj-Deta.p', 'rb')) ),
    'BDT: mjjmax-Deta-FW': partial(load_from_bdt_dump, pickle.load(open('prediction_dump_mjj-Deta-FW.p', 'rb')) )
}
