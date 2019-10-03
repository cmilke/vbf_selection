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
import numpy
from acorn_backend import basic_vbf_tagging_algorithms


# A dict of the tagging algorithms available to tag VBF events
_available_taggers = {
    'delta_eta': basic_vbf_tagging_algorithms.delta_eta_tagger
  , 'mjj': basic_vbf_tagging_algorithms.mjj_tagger
  , 'mjjj': basic_vbf_tagging_algorithms.mjjj_tagger
}


def apply_tagger(input_type, tagger_name):
    tagger = _available_taggers[tagger_name]
    event_input = pickle.load( open('data/input_'+input_type+'.p', 'rb') )
    selector_input = pickle.load( open('data/jet_selections_'+input_type+'.p', 'rb') )
    tagger_output = [ {} for i in range( len(event_input) ) ]

    for jet_count, (event_list, selections) in enumerate( zip( event_input, selector_input) ):
        for algorithm_name, jet_tuple_list in selections.items():
            discriminant_list = []
            for event_count, event in enumerate(event_list):
                #if event_count >= 20: break
                vbf_jets = jet_tuple_list[event_count]
                discriminant = tagger(event,vbf_jets)
                discriminant_list.append(discriminant)
            tagger_output[jet_count][algorithm_name] = numpy.array(discriminant_list, dtype=float)

    print(input_type)
    for jet_count, selection_methods in enumerate(tagger_output):
        print(jet_count)
        for algorithm, events in selection_methods.items():
            print('|---'+algorithm+': '+str(len(events)))
    pickle.dump( tagger_output, open('data/tagged_'+tagger_name+'_'+input_type+'.p', 'wb') )


def tag_events():
    for tagger_name in _available_taggers.keys():
        print('\n*****'+tagger_name+'******')
        if len(sys.argv) < 2:
            apply_tagger('sig', tagger_name)
            apply_tagger('bgd', tagger_name)
        else:
            apply_tagger(sys.argv[1], tagger_name)

tag_events()
