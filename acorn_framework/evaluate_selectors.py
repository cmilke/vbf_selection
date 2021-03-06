#!/usr/bin/env python

import sys
import math
import pickle
from acorn_backend.tagger_methods import selector_options


def evaluate_selections():
    data_dump_infix = sys.argv[1]
    input_type = 'sig'
    data_file = 'data/output_'+data_dump_infix+'_'+input_type+'.p'
    data_dump = pickle.load( open(data_file, 'rb') )

    selector_scores = {}
    for category in data_dump.values():
        for event in category.events:
            jet_count = len(event.jets)
            if jet_count < 3: continue
            weight = event.event_weight
            for name, selector in selector_options.items():
                key = str(jet_count)+category.key+': '+name
                chosen_jets = selector(event)
                correct = True
                for jet in chosen_jets:
                    if not jet.is_truth_quark(): correct = False

                increment = int(correct)*weight
                if key in selector_scores:
                    selector_scores[key][0] += increment
                    selector_scores[key][1] += weight
                else:
                    selector_scores[key] = [increment, weight]

    display = []
    for key, (num_correct, total_num) in selector_scores.items():
        efficiency = num_correct / total_num
        display.append( (key, efficiency) )
    #display.sort(key=(lambda x: x[1]), reverse=True)
    for key,value in display: print( '{}: {:.2}'.format(key, value) )


evaluate_selections()
