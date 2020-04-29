from functools import partial
from uproot_methods import TLorentzVector
import itertools
import random


# Selectors

def all_jets(vectors):
    return vectors


def leading_pt_jets(event): #TODO
    return ( event.jets[0], event.jets[1] )


def mjj_rank(rank, vectors):
    invariant_mass_pairs = [ ( (vec_i+vec_j).mass, vec_i, vec_j) for vec_i, vec_j in itertools.combinations(vectors, 2) ]
    invariant_mass_pairs.sort(reverse=True, key=lambda pair: pair[0]) #sort by invariant mass
    return invariant_mass_pairs[rank][1:]


def delta_eta_rank(rank, event): #TODO
    delta_eta_pairs = [ ( abs(jet_i.eta()-jet_j.eta()), jet_i, jet_j) for jet_i, jet_j in itertools.combinations(event.jets, 2) ]
    delta_eta_pairs.sort(reverse=True, key=lambda t: t[0]) #sort by delta eta
    return delta_eta_pairs[rank][1:]


def random_jets(event): #TODO
    return random.sample(event.jets, 2)


# Discriminators

def mjj(vectors):
    return (vectors[0] + vectors[1]).mass

def total_invariant_mass(event): #TODO
    total_vector = TLorentzVector(0,0,0,0)
    for jet in event.jets: total_vector += jet.vector()
    return total_vector.mass

def stdTag(selector, discriminator, vectors):
        selected_vectors = selector(vectors)
        return discriminator(selected_vectors)

selector_options = {
    'all': all_jets,
    'maxpt': leading_pt_jets,
    'mjjmax': partial(mjj_rank, 0),
    'mjjSL': partial(mjj_rank, 1),
    'Deta_max': partial(delta_eta_rank, 0),
    'random': random_jets
}


Tagger = {
	'mjN': total_invariant_mass,
	'mjj_from_leading_pt': partial(stdTag, leading_pt_jets, mjj),
	'mjjmax': partial( stdTag, partial(mjj_rank,0), mjj),
	'mjjSL': partial( stdTag, partial(mjj_rank,1), mjj),
	'mjj_of_random_jets': partial( stdTag, random_jets, mjj)
}
