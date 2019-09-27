import sys
import pickle
from vbf_backend.cmilke_jets import cmilke_jet
from vbf_backend import basic_jet_selection_algorithms

_selectors = {
    '2maxpt': basic_jet_selection_algorithms.highest_pt_selector
  , 'etamax': basic_jet_selection_algorithms.maximal_eta_selector
  , 'null': basic_jet_selection_algorithms.null_selector
  , 'truth': basic_jet_selection_algorithms.truth_selector
}

_output_classifiers = {
    '2'      : ['2maxpt']
  , '3'      : ['2maxpt', 'etamax', 'truth']
  , '3inclPU': ['2maxpt']
  , '4'      : ['2maxpt']
  , '4inclPU': ['2maxpt']
}

def select_jets(input_type):
    unprocessed_input = pickle.load( open('data/input_'+input_type+'.p', 'rb') )
    processed_output = {}

    for jet_type, event_list in unprocessed_input.items():
        processed_output[jet_type] = {}
        for algorithm in _output_classifiers[jet_type]:
            processed_output[jet_type][algorithm] = []
    
        for event_count, event in enumerate(event_list):
            #if event_count >= 20: break
            for algorithm in _output_classifiers[jet_type]:
                jet_idents = _selectors[algorithm](event)
                processed_output[jet_type][algorithm].append(jet_idents)
    
    
    
    for jet_type, selections in processed_output.items():
        print(jet_type)
        for algorithm, events in selections.items():
            print('|---'+algorithm+': '+str(len(events)))
    pickle.dump( processed_output, open('data/jet_selections_'+input_type+'.p', 'wb') )


input_type = sys.argv[1]

if input_type == 'all':
    print('signal')
    select_jets('sig')
    print()
    print('background')
    select_jets('bgd')
else: select_jets(input_type)
