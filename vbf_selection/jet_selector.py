#!/usr/bin/env python

'''
Take as input the pickled event_data_dump from extract_inputs.

Output a dictionary structure resembling the extract_input event_data_dump,
but for each event, instead of storing a list of jet objects,
simply store a tuple of jet indices, where the indices correspond
to the selected jets in the event_data_dump.
(Depending on the algorithm, more the two jets may appear in the tuple)
'''

import sys
import pickle
from vbf_backend.cmilke_jets import cmilke_jet
from vbf_backend import basic_jet_selection_algorithms

# A dict of the algorithms that can be used
# to distinguish vbf jets from other jets
_selectors = {
    '2maxpt': basic_jet_selection_algorithms.highest_pt_selector
  , 'etamax': basic_jet_selection_algorithms.maximal_eta_selector
  , 'null': basic_jet_selection_algorithms.null_selector
  , 'truth': basic_jet_selection_algorithms.truth_selector
  , 'random': basic_jet_selection_algorithms.random_selector
}

# A mapping of which algorithms are to be used
# with which jet categories
_output_classifiers = {
    '2'       : ['null']
  , '3'       : ['2maxpt', 'etamax', 'truth', 'random']
  , '3noPU'   : ['2maxpt', 'etamax', 'truth']
  , '3withPU' : ['2maxpt', 'etamax', 'truth']
  , '3noFSR'  : ['2maxpt', 'etamax', 'truth']
  , '3withFSR': ['2maxpt', 'etamax', 'truth']
  , '4'       : ['2maxpt']
  , '4withPU' : ['2maxpt']
}


# Iterate over jet categories
# For each category, iterate over the algorithms assigned to that category
# For each algorithm, iterate over all events in the category
# For each event, have the algorithm select the vbf jets in the event
def select_jets(input_type):
    unprocessed_input = pickle.load( open('data/input_'+input_type+'.p', 'rb') )
    processed_output = {} #Filled below, with a structure similar to the unprocessed_input

    for jet_type, event_list in unprocessed_input.items():
        processed_output[jet_type] = {}
        for algorithm in _output_classifiers[jet_type]:
            processed_output[jet_type][algorithm] = []
            for event_count, event in enumerate(event_list):
                #if event_count >= 20: break
                jet_idents = _selectors[algorithm](event)
                processed_output[jet_type][algorithm].append(jet_idents)
    
    print('\n******'+input_type+'******')
    for jet_type, selections in processed_output.items():
        print(jet_type)
        for algorithm, events in selections.items():
            print('|---'+algorithm+': '+str(len(events)))

    pickle.dump( processed_output, open('data/jet_selections_'+input_type+'.p', 'wb') )


# Either run over background and signal, or pick one
if len(sys.argv) < 2:
    select_jets('sig')
    select_jets('bgd')
else: select_jets(sys.argv[1])
