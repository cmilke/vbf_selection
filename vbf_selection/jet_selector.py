import sys
import pickle
from vbf_backend.cmilke_jets import cmilke_jet
from vbf_backend import basic_jet_selection_algorithms

input_type = sys.argv[1]

unprocessed_input = pickle.load( open('data/input_'+input_type+'.p', 'rb') )
processed_output = {}

selector = {
    '2maxpt': basic_jet_selection_algorithms.highest_pt
}

output_classifiers = {
    '2'      : ['2maxpt']
  , '3'      : ['2maxpt']
  , '3inclPU': ['2maxpt']
  , '4'      : ['2maxpt']
  , '4inclPU': ['2maxpt']
}

for jet_type, event_list in unprocessed_input.items():
    processed_output[jet_type] = {}
    for algorithm in output_classifiers[jet_type]:
        processed_output[jet_type][algorithm] = []

    for event_count, event in enumerate(event_list):
        #if event_count >= 20: break
        for algorithm in output_classifiers[jet_type]:
            jet_idents = selector[algorithm](event)
            processed_output[jet_type][algorithm].append(jet_idents)


#for jet_type, selections in processed_output.items():
#    print(jet_type)
#    for algorithm, events in selections.items():
#        print('|---'+algorithm+': '+str(events))

pickle.dump( processed_output, open('data/jet_selections_'+input_type+'.p', 'wb') )
