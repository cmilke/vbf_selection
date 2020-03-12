from functools import partial
from uproot_methods import TLorentzVector
import itertools
import random
import numpy

from acorn_backend.analysis_utils import etaphi_difference


# Selectors

def all_jets(event):
    return tuple(range(len(event.jets)))


# This assumes the jet list is pt-ordered largest to smallest
def leading_pt_jets(event):
    return (0,1)


def mjj_rank(rank, event):
    index_combinations = itertools.combinations(range(len(event.jets)), 2)
    mass_pairs = [ ( (event.jets[i].vector()+event.jets[j].vector()).mass, i,j ) for i,j in index_combinations ]
    mass_pairs.sort(reverse=True, key=lambda t: t[0]) # Sort by invariant mass of the pairs, highest first
    rank_pair = mass_pairs[rank]
    jet_idents = rank_pair[1:] # Get jet indices
    return tuple(jet_idents)


def delta_eta_rank(rank, event):
    index_combinations = itertools.combinations(range(len(event.jets)), 2)
    delta_eta_pairs_pairs = [ (abs(event.jets[i].eta()-event.jets[j].eta()), i,j ) for i,j in index_combinations ]
    delta_eta_pairs.sort(reverse=True, key=lambda t: t[0]) # Sort by Deta of the pairs, highest first
    rank_pair = delta_eta_pairs[rank]
    jet_idents = rank_pair[1:] # Get jet indices
    return tuple(jet_idents)


def random_jets(event):
    return tuple(random.sample(range(len(event.jets)), 2))


# Discriminators
def total_invariant_mass(event):
    total_vector = TLorentzVector(0,0,0,0)
    for jet in event.jets: total_vector += jet.vector()
    return total_vector.mass


def mjj(selector, event):
    selections = selector(event)
    jets = [ event.jets[index] for index in selections[:2] ]
    return (jets[0].vector() + jets[1].vector()).mass


def forward_based_centrality(event):
    selections = delta_eta_rank(0, event)
    primary_jets = [ event.jets[index] for index in selections[:2] ]
    primary_jets.sort(key=lambda j: j.eta())
    extra_index = ({0,1,2} - set(selections[:2])).pop()
    extra_jet = event.jets[extra_index]

    primary_Deta = primary_jets[1].eta() - primary_jets[0].eta()
    extra_Deta = extra_jet.eta() - primary_jets[0].eta()
    centrality = abs(2*extra_Deta / primary_Deta - 1)
    #if centrality > 1: centrality = 1.0 / centrality
    return centrality


def centrality(selector, event):
    selections = selector(event)
    primary_jets = [ event.jets[index] for index in selections[:2] ]
    primary_jets.sort(key=lambda j: j.eta())
    extra_index = ({0,1,2} - set(selections[:2])).pop()
    extra_jet = event.jets[extra_index]

    primary_Deta = primary_jets[1].eta() - primary_jets[0].eta()
    extra_Deta = extra_jet.eta() - primary_jets[0].eta()
    centrality = abs(2*extra_Deta / primary_Deta - 1)
    #if centrality > 1: centrality = 1.0 / centrality
    return centrality


# For two jets only
def jet_pull_tension(event):
    jet0, jet1 = event.jets
    if jet0.jet_pull_mag() < 0 or jet1.jet_pull_mag() < 0:
        return -100
    jetvec0 = ( jet0.eta(), jet0.phi() )
    jetvec1 = ( jet1.eta(), jet1.phi() )
    pullvec0 = jet0.jet_pull_vec()
    pullvec1 = jet1.jet_pull_vec()

    Dvec  = numpy.array( etaphi_difference( *jetvec0, *jetvec1 ) )
    Dpull = numpy.array( etaphi_difference( *pullvec0, *pullvec1 ) )
    pull_tension = - numpy.dot(Dvec,Dpull)
    return pull_tension


selector_options = {
    'all': all_jets,
    'maxpt': leading_pt_jets,
    'mjjmax': partial(mjj_rank, 0),
    'mjjSL': partial(mjj_rank, 1),
    'Deta_max': partial(delta_eta_rank, 0),
    'random': random_jets
}

tagger_options = {
    '2jet': {
        'mjj': partial(mjj, leading_pt_jets),
        'pull_tension': jet_pull_tension
    },
    '>=3jet': {
        'mjN': total_invariant_mass,
        'mjj_from_leading_pt': partial(mjj, leading_pt_jets),
        'mjjmax': partial( mjj, partial(mjj_rank,0)),
        'mjjSL': partial( mjj, partial(mjj_rank,1)),
        'mjj_of_random_jets': partial( mjj, random_jets),
        'Fcentrality': forward_based_centrality,
        'centrality_of_maxpt': partial( centrality, leading_pt_jets)
    }
}

jet_ident_counter = {
    '2jet': lambda event : len(event.jets) == 2,
    '>=3jet': lambda event : len(event.jets) >= 3
}
