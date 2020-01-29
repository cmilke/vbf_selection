#!/usr/bin/env python

import sys
import math
import pickle
from acorn_backend.tagger_loader import selector_options


def evaluate_selections():
    input_type = 'sig'
    data_dump = pickle.load( open('data/output_aviv_tag_'+input_type+'.p', 'rb') )
    #data_dump = pickle.load( open('data/output_cmilkeV1_truth_tag_'+input_type+'.p', 'rb') )

    selector_scores = {}
    for category in data_dump.values():
        for event in category.events:
            jet_count = len(event.jets)
            weight = event.event_weight
            for selector in event.selectors.values():
                key = str(jet_count)+category.key+'_'+selector.key

                increment = int(selector.is_correct)*weight
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
