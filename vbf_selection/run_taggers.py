#!/usr/bin/env python

'''
Script which runs over a list of ntuples, filtering out events and jets.
The output is a pickled dictionary containing categorized events,
where each event is a python list of "cmilke_jet" objects,
which store basic jet information used throughout the rest of the framework
'''

import sys
import math
import pickle
from acorn_backend.acorn_containers import acorn_jet
from acorn_backend import event_categorization
from acorn_backend import acorn_utils as autils

#Define all the high level root stuff: ntuple files, branches to be used
_input_type_options = {
    'sig': autils.Flavntuple_list_VBFH125_gamgam[:1],
    'bgd': autils.Flavntuple_list_ggH125_gamgam[:1]
}
_tpart_branches = [ 'tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi' ]
_tjet_branches = [ 'truthjpT', 'truthjeta', 'truthjphi', 'truthjm' ]
_reco_branches = ['j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
                    'j0_JVT', 'j0_fJVT_Tight',
                    'j0pT', 'j0eta', 'j0phi', 'j0m']

_branch_list = _tpart_branches+_tjet_branches+_reco_branches
_truthj_branch_index = len(_tpart_branches)
_reco_branch_index = _truthj_branch_index + len(_tjet_branches)

def jet_matches(tparteta, tpartphi, truthjeta, truthjphi):
    delta_eta = abs(tparteta - truthjeta)
    delta_phi = abs(tpartphi - truthjphi)
    delta_R = math.hypot(delta_eta, delta_phi)
    return ( delta_R < 0.3 )


def record_reco_jets(is_bgd, truth_particles, truth_jets, reco_jets, event_data_dump):
    # Initialize different category lists
    num_quark_jets = 0
    recorded_jets = [] # Records all useable jets

    # Loop over reco jets, and append them to the appropriate lists
    for rj in autils.jet_iterator(_reco_branches, reco_jets):
        # Filter out jets on basic pt/eta/photon cuts
        if not autils.passes_std_jet_cuts(rj['j0pT'], rj['j0eta']) or rj['j0_isTightPhoton']: continue

        # Create jet object storing the essential aspects of the ntuple reco jet
        new_jet = acorn_jet.from_reco(rj)
        if new_jet.is_truth_quark(): num_quark_jets += 1
        recorded_jets.append(new_jet)

    # Categorize event, and then perform tagging
    for category in event_data_dump: category.new_event(recorded_jets, is_bgd)


def record_events(input_type):
    # Define all event categories
    event_data_dump = [
        event_categorization.base_categorizer(),
        event_categorization.no_pileup(),
        event_categorization.with_pileup(),
        event_categorization.filter_with_JVT()
    ]

    # Iterate over each event in the ntuple list,
    # storing/sorting/filtering events into the data_dump as it goes
    input_list = _input_type_options[input_type]
    is_bgd = input_type == 'bgd'
    for event in autils.event_iterator(input_list, 'Nominal', _branch_list, 20, 0):
        truth_particles = event[:_truthj_branch_index]
        truth_jets = event[_truthj_branch_index:_reco_branch_index]
        reco_jets = event[_reco_branch_index:]
        record_reco_jets(is_bgd, truth_particles, truth_jets, reco_jets, event_data_dump)

    for category in event_data_dump: print( category.summary() )
    for category in event_data_dump: print( category )

    # Output the event categories for use by later scripts
    #pickle.dump( event_data_dump, open('data/input_'+input_type+'.p', 'wb') )


# Either run over background and signal, or pick one
if len(sys.argv) < 2:
    record_events('sig')
    record_events('bgd')
else:
    record_events(sys.argv[1])
