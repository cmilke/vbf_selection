#!/usr/bin/env python

import sys
import math
import pickle
import numpy
from acorn_backend.machine_learning.basic_selector import basic_neural_net_selector as training_class



def train():
    input_type = 'sig'
    training_category = 'JVT'

    data_dump = pickle.load( open('data/output_'+input_type+'.p', 'rb') )

    prepared_data_list = []
    data_labels_list = []
    for event in data_dump[training_category].events:
        if len(event.jets) not in training_class.jet_count_range: continue
        prepared_event = training_class.prepare_event(event)
        prepared_data_list.append(prepared_event)

        label = training_class.get_label(event)
        data_labels_list.append(label)
        if len(prepared_data_list) >= 10000: break
    prepared_data = numpy.array(prepared_data_list)
    data_labels = numpy.array(data_labels_list)

    training_cutoff = int( len(prepared_data)* (3/4) )
    training_data   = prepared_data[:training_cutoff]
    testing_data    = prepared_data[training_cutoff:]
    training_labels = data_labels[:training_cutoff]
    testing_labels  = data_labels[training_cutoff:]

    training_class.train_model(training_data, training_labels)

    training_class.test_model(training_data, training_labels)


train()
