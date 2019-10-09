#!/usr/bin/env python

import sys
import math
import pickle
from acorn_backend.evaluation_filters import event_filters
from acorn_backend.evaluation_filters import filter_events


def evaluate_selections():
    input_type = 'sig'
    jet_input = pickle.load( open('data/input_'+input_type+'.p', 'rb') )
    selector_input = pickle.load( open('data/jet_selections_'+input_type+'.p', 'rb') )

    efficiencies = {}

    for jet_count, event_list in enumerate(jet_input):
        for filter_key in event_filters.keys():
            for algorithm, selections in selector_input[jet_count].items():
                tag_label = str(jet_count) + filter_key + '_' + algorithm

                event_jet_pair = list( zip(event_list, selections) )
                filtered_pair = filter_events(filter_key, event_list, event_jet_pair)

                total_events = 0
                total_selected_correctly = 0
                for event_count, (event, vbf_jets) in enumerate(filtered_pair):
                    #if event_count >= 20: break
                    selected_correctly = 1
                    for jet_index in vbf_jets:
                        jet = event.jets[jet_index]
                        if not jet.is_truth_quark():
                            selected_correctly = 0
                            break
                    total_selected_correctly += selected_correctly
                    total_events += 1

                efficiencies[tag_label] = total_selected_correctly / total_events
    display = list(efficiencies.items())
    #display.sort(key=(lambda x: x[1]), reverse=True)


    for key,value in display: print( '{}: {:.2}'.format(key, value) )

evaluate_selections()
