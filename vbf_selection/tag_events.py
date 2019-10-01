#!/usr/bin/env python

'''
Take as input the event_data_dump and jet_selections from
extract_inputs and jet_selector.

The nested jet categorization of jet_selections is stored here in a flattened form,
and then nested within an event tagger label.
'''

import sys
import math
import pickle
from vbf_backend.cmilke_jets import cmilke_jet
from vbf_backend import basic_vbf_tagging_algorithms


# A dict of the tagging algorithms available to tag VBF events
_available_taggers = {
    'delta_eta': basic_vbf_tagging_algorithms.delta_eta_tagger
  , 'mjj': basic_vbf_tagging_algorithms.mjj_tagger
  , 'mjjj': basic_vbf_tagging_algorithms.mjjj_tagger
}


def tag_events(input_type, tagger):
    tagger_output = {}
    jet_input = pickle.load( open('data/input_'+input_type+'.p', 'rb') )
    selector_input = pickle.load( open('data/jet_selections_'+input_type+'.p', 'rb') )

    for jet_type, event_list in jet_input.items():
        for algorithm, selections in selector_input[jet_type].items():
            category = jet_type + '_' + algorithm
            tagger_output[category] = []
            for event_count, event in enumerate(event_list):
                #if event_count >= 20: break
                vbf_jets = selections[event_count]
                discriminant = tagger(event,vbf_jets)
                tagger_output[category].append(discriminant)

    print(input_type)
    #for key,value in tagger_output.items():
    #    print(key, value)
    #    print()
    for key,value in tagger_output.items(): print( '{}: {}'.format(key, len(value) ) )
    print()
    pickle.dump( tagger_output, open('data/tagged_'+tagger_name+'_'+input_type+'.p', 'wb') )


for tagger_name in _available_taggers.keys():
    print('\n*****'+tagger_name+'******')
    tagger = _available_taggers[tagger_name]
    if len(sys.argv) < 2:
        tag_events('sig', tagger)
        tag_events('bgd', tagger)
    else:
        tag_events(sys.argv[1], tagger)
