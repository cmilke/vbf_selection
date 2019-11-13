#!/usr/bin/env python

import sys
import argparse
import math
import pickle
from acorn_backend.acorn_containers import acorn_jet
from acorn_backend import event_categorization
from acorn_backend import acorn_utils as autils
from acorn_backend.tagger_loader import load_network_models
from uproot_methods import TLorentzVector

#Define all the high level root stuff: ntuple files, branches to be used
_input_type_options = {
    'sig': (
        autils.Flavntuple_list_VBFH125_gamgam[:1]
      , autils.Flavntuple_list_VBFH125_gamgam[4:5]
    ),
    'bgd': (
        autils.Flavntuple_list_ggH125_gamgam[:1]
      , autils.Flavntuple_list_ggH125_gamgam[7:8]
    )
}
_branch_list = {
    'event' : ['eventWeight']
  , 'tpart' : ['tpartpdgID', 'tpartstatus', 'tpartpT', 'tparteta', 'tpartphi', 'tpartm']
  , 'truthj': ['truthjpT', 'truthjeta', 'truthjphi', 'truthjm']
  , 'j0'    : ['j0truthid', 'j0_isTightPhoton', 'j0_isPU', 
                        'j0_JVT', 'j0_fJVT_Tight', 'j0pT', 'j0eta', 'j0phi', 'j0m']
}


def match_jet(vector_to_match, event):
    for tp in autils.jet_iterator(event['tpart']):
        if tp['tpartpdgID'] == autils.PDG['photon']:
            if tp['tpartstatus'] != autils.Status['photon_out']: continue
        elif tp['tpartstatus'] != autils.Status['outgoing']: continue

        truth_vec = TLorentzVector.from_ptetaphim(tp['tpartpT'], tp['tparteta'], tp['tpartphi'], tp['tpartm'])

        deltaR = vector_to_match.delta_r(truth_vec)
        if deltaR < 0.3: return tp['tpartpdgID']
    return -1


def record_reco_jets(is_sig, event_weight, event, event_data_dump):
    recorded_jets = [] # Records all useable jets

    # Loop over reco jets, and append them to the appropriate lists
    for rj in autils.jet_iterator(event['j0']):
        # Filter out jets on basic pt/eta/photon cuts
        if not autils.passes_std_jet_cuts(rj['j0pT'], rj['j0eta']): continue
        v = TLorentzVector.from_ptetaphim(rj['j0pT'], rj['j0eta'], rj['j0phi'], rj['j0m'])
        pdgid = match_jet(v, event)
        if pdgid == autils.PDG['photon']: continue
        #if rj['j0_isTightPhoton']: continue

        # Create jet object storing the essential aspects of the ntuple reco jet
        new_jet = acorn_jet(v, pdgid, rj['j0_isPU'], rj['j0_JVT'], rj['j0_fJVT_Tight'])
        recorded_jets.append(new_jet)

    # Categorize event, and then either discard the event or perform tagging on it
    for category in event_data_dump.values():
        category.add_event(recorded_jets, is_sig, event_weight)


def record_events(input_type, no_tagging_mode, debug_mode):
    # Define all event categories we want to use
    categories_to_dump = [
        event_categorization.filter_with_JVT
    ]

    event_data_dump = {}
    for category_class in categories_to_dump:
        event_data_dump[category_class.key] = category_class(not no_tagging_mode)
        

    # Iterate over each event in the ntuple list,
    # storing/sorting/filtering events into the data_dump as it goes
    input_list = _input_type_options[input_type][no_tagging_mode]
    is_sig = input_type == 'sig'
    events_per_bucket = 10 if debug_mode else 10000
    max_bucket = 0 if debug_mode else 0
    for event in autils.event_iterator(input_list, 'Nominal', _branch_list, events_per_bucket, max_bucket):
        event_weight = event['event']['eventWeight']
        record_reco_jets(is_sig, event_weight, event, event_data_dump)

    if debug_mode:
        for category in event_data_dump.values(): print(category)
    else:
        for category in event_data_dump.values(): print( category.summary() )

    # Output the event categories for use by later scripts
    training_infix = 'untagged_' if no_tagging_mode else ''
    pickle.dump( event_data_dump, open('data/output_'+training_infix+input_type+'.p', 'wb') )


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", 
        required = False,
        default = False,
        action = 'store_true',
        help     = "Run over Signal events",
    ) 

    parser.add_argument(
        "-b", 
        required = False,
        default = False,
        action = 'store_true',
        help     = "Run over Background events"
            "(Note: if neither -s or -b are given, default behaviour is to run over both)",
    ) 

    parser.add_argument(
        "-N", 
        required = False,
        default = False,
        action = 'store_true',
        help     = "Disables tagging and VBF jet selection (only categorize and record events). Used to create inputs for ML training.",
    ) 

    parser.add_argument(
        "--debug", 
        required = False,
        default = False,
        action = 'store_true',
        help     = "Prints debug information",
    ) 

    args = parser.parse_args()

    if not args.N: load_network_models()

    if args.s: record_events('sig', args.N, args.debug)
    if args.b: record_events('bgd', args.N, args.debug)
    if not (args.b or args.s):
        record_events('sig', args.N, args.debug)
        record_events('bgd', args.N, args.debug)

run()
