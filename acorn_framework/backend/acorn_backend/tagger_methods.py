from functools import partial
from uproot_methods import TLorentzVector
import itertools


# Selectors

# This assumes the jet list is pt-ordered largest to smallest
def all_jets(event):
    return event.jets


def leading_pt_jets(event):
    return ( event.jets[0], event.jets[1] )


def mjj_rank(rank, event)
    invariant_mass_pairs = [ ( (jet_i.vector+jet_j.vector).mass, jet_i, jet_j) for jet_i, jet_j in itertools.combinations(event.jets, 2) ]
    invariant_mass_pairs.sort(reverse=True, key=lambda t: t[0]) #sort by invariant mass
    return invariant_mass_pairs[rank][1:]


def delta_eta_rank(rank, event)
    delta_eta_pairs = [ ( abs(jet_i.vector.eta-jet_j.vector.eta), jet_i, jet_j) for jet_i, jet_j in itertools.combinations(event.jets, 2) ]
    delta_eta_pairs.sort(reverse=True, key=lambda t: t[0]) #sort by delta eta
    return delta_eta_pairs[rank][1:]


def random_jets(event):
    return random.sample(event.jets, 2)

# Discriminators

def mjj(jet0, jet1):
    return (jet0.vector + jet1.vector).mass

def total_invariant_mass(event):
    total_vector = TLorentzVector(0,0,0,0)
    for jet in event.jets: total_vector += jet.vector
    return total_vector.mass

def stdTag(selector, discriminator, event):
        jets = selector(event)
        return discriminator.mjj(*jets)
    

tagging_dictionary = {
    '2jet': {
        'mjj': partial(stdTag, all_jets, mjj)
    },
    '>=3jet': {
        'mjN': total_invariant_mass,
        'mjj_from_leading_pt': partial(stdTag, leading_pt_jets, mjj),
        'mjjmax': partial( stdTag, partial(mjj_rank,0), mjj),
        'mjjSL': partial( stdTag, partial(mjj_rank,1), mjj),
        'mjj_of_random_jets': partial( stdTag, random_jets, mjj)
    }
}
