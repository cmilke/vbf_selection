#!/usr/bin/env python

import sys
import math
import pickle


def tag_events():
    input_type = 'sig'
    jet_input = pickle.load( open('data/input_'+input_type+'.p', 'rb') )
    selector_input = pickle.load( open('data/jet_selections_'+input_type+'.p', 'rb') )

    efficiencies = {}

    for jet_count, event_list in enumerate(jet_input):
        for algorithm, selections in selector_input[jet_count].items():
            tag_label = str(jet_count) + '_' + algorithm
            total_events = 0
            total_selected_correctly = 0
            for event_count, event in enumerate(event_list):
                #if event_count >= 20: break
                selected_jets = selections[event_count]
                selected_correctly = 1
                for jet_index in selected_jets:
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

tag_events()
